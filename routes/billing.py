from datetime import datetime

from flask import Blueprint, Response, flash, redirect, render_template, request, session, url_for

from routes.db import execute, fetch_all, fetch_one
from routes.decorators import login_required, role_required

bp = Blueprint("billing", __name__)


def _bill_breakdown(patient_id: int):
    consultation_fee = fetch_one(
        """
        SELECT COALESCE(SUM(d.consultation_fee), 0) AS total
        FROM appointments a
        JOIN doctors d ON d.doctor_id = a.doctor_id
        WHERE a.patient_id = %s AND a.status IN ('confirmed', 'in_progress', 'completed')
        """,
        (patient_id,),
    )["total"]

    room_charges = fetch_one(
        """
        SELECT COALESCE(SUM((DATEDIFF(COALESCE(ad.discharged_on, CURDATE()), ad.admitted_on) + 1) * r.price_per_day), 0) AS total
        FROM admissions ad
        JOIN rooms r ON r.room_id = ad.room_id
        WHERE ad.patient_id = %s
        """,
        (patient_id,),
    )["total"]

    medicine_charges = fetch_one(
        """
        SELECT COALESCE(SUM(m.price), 0) AS total
        FROM appointments a
        JOIN prescriptions p ON p.appt_id = a.appt_id
        JOIN medicines m ON m.medicine_id = p.medicine_id
        WHERE a.patient_id = %s
        """,
        (patient_id,),
    )["total"]

    subtotal = float(consultation_fee) + float(room_charges) + float(medicine_charges)
    tax = round(subtotal * 0.05, 2)
    total = round(subtotal + tax, 2)
    return {
        "consultation_fee": round(float(consultation_fee), 2),
        "room_charges": round(float(room_charges), 2),
        "medicine_charges": round(float(medicine_charges), 2),
        "subtotal": round(subtotal, 2),
        "tax": tax,
        "total": total,
    }


@bp.route("/admin/billing/<int:patient_id>")
@login_required
@role_required("admin")
def patient_billing(patient_id: int):
    patient = fetch_one(
        """
        SELECT p.patient_id, p.patient_code, u.name, u.email
        FROM patients p
        JOIN users u ON u.user_id = p.user_id
        WHERE p.patient_id = %s
        """,
        (patient_id,),
    )
    bills = fetch_all(
        """
        SELECT bill_id, consultation_fee, room_charges, medicine_charges, subtotal, tax, total, status, created_at, paid_at
        FROM bills
        WHERE patient_id = %s
        ORDER BY created_at DESC
        """,
        (patient_id,),
    )
    preview = _bill_breakdown(patient_id)
    return render_template(
        "admin/billing/detail.html",
        active_page="billing",
        patient=patient,
        bills=bills,
        preview=preview,
    )


@bp.route("/admin/billing/generate/<int:patient_id>", methods=["POST"])
@login_required
@role_required("admin")
def generate_bill(patient_id: int):
    breakdown = _bill_breakdown(patient_id)
    latest_admission = fetch_one(
        """
        SELECT admission_id
        FROM admissions
        WHERE patient_id = %s
        ORDER BY admitted_on DESC
        LIMIT 1
        """,
        (patient_id,),
    )

    execute(
        """
        INSERT INTO bills (
            patient_id, admission_id, consultation_fee, room_charges, medicine_charges,
            subtotal, tax, total, status, created_at
        ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, 'pending', %s)
        """,
        (
            patient_id,
            latest_admission["admission_id"] if latest_admission else None,
            breakdown["consultation_fee"],
            breakdown["room_charges"],
            breakdown["medicine_charges"],
            breakdown["subtotal"],
            breakdown["tax"],
            breakdown["total"],
            datetime.utcnow(),
        ),
    )
    flash("Bill generated.", "success")
    return redirect(url_for("billing.patient_billing", patient_id=patient_id))


@bp.route("/admin/billing/<int:bill_id>/pay", methods=["POST"])
@login_required
@role_required("admin")
def mark_bill_paid(bill_id: int):
    execute(
        "UPDATE bills SET status = 'paid', paid_at = %s WHERE bill_id = %s",
        (datetime.utcnow(), bill_id),
    )
    flash("Bill marked as paid.", "success")
    return redirect(request.referrer or url_for("dashboard.admin_dashboard"))


def _load_invoice_context(bill_id: int):
    bill = fetch_one(
        """
        SELECT b.*, p.patient_code, u.name AS patient_name, u.email AS patient_email
        FROM bills b
        JOIN patients p ON p.patient_id = b.patient_id
        JOIN users u ON u.user_id = p.user_id
        WHERE b.bill_id = %s
        """,
        (bill_id,),
    )
    if not bill:
        return None
    return {"bill": bill}


@bp.route("/admin/billing/<int:bill_id>/pdf")
@login_required
def bill_pdf(bill_id: int):
    ctx = _load_invoice_context(bill_id)
    if not ctx:
        flash("Bill not found.", "warning")
        return redirect(url_for("dashboard.admin_dashboard"))

    role = session.get("role")
    if role == "patient":
        patient = fetch_one("SELECT patient_id FROM patients WHERE user_id = %s", (session["user_id"],))
        if not patient or patient["patient_id"] != ctx["bill"]["patient_id"]:
            return ("Forbidden", 403)

    html = render_template("admin/billing/invoice.html", **ctx)
    try:
        from weasyprint import HTML

        pdf = HTML(string=html).write_pdf()
        return Response(
            pdf,
            mimetype="application/pdf",
            headers={"Content-Disposition": f"attachment; filename=invoice-{bill_id}.pdf"},
        )
    except Exception:
        return Response(
            html,
            mimetype="text/html",
            headers={"Content-Disposition": f"inline; filename=invoice-{bill_id}.html"},
        )
