from flask import Blueprint, flash, redirect, render_template, request, session, url_for

from routes.db import execute, fetch_all, fetch_one
from routes.decorators import login_required, role_required

bp = Blueprint("patient", __name__, url_prefix="/patient")


def _patient_id():
    row = fetch_one("SELECT patient_id FROM patients WHERE user_id = %s", (session["user_id"],))
    return row["patient_id"] if row else None


@bp.route("/dashboard")
@login_required
@role_required("patient")
def patient_dashboard():
    patient_id = _patient_id()
    upcoming = fetch_all(
        """
        SELECT a.appt_id, a.appt_date, a.appt_time, a.status, u.name AS doctor_name
        FROM appointments a
        JOIN doctors d ON d.doctor_id = a.doctor_id
        JOIN users u ON u.user_id = d.user_id
        WHERE a.patient_id = %s AND a.appt_date >= CURDATE()
        ORDER BY a.appt_date, a.appt_time
        LIMIT 3
        """,
        (patient_id,),
    )
    prescriptions = fetch_all(
        """
        SELECT pr.prescription_id, m.name AS medicine_name, pr.dosage, pr.duration, pr.created_at
        FROM prescriptions pr
        JOIN appointments a ON a.appt_id = pr.appt_id
        JOIN medicines m ON m.medicine_id = pr.medicine_id
        WHERE a.patient_id = %s
        ORDER BY pr.created_at DESC
        LIMIT 2
        """,
        (patient_id,),
    )
    bills = fetch_all(
        """
        SELECT bill_id, total, status, created_at
        FROM bills
        WHERE patient_id = %s AND status = 'pending'
        ORDER BY created_at DESC
        LIMIT 5
        """,
        (patient_id,),
    )
    return render_template(
        "patient/dashboard.html",
        active_page="dashboard",
        upcoming=upcoming,
        prescriptions=prescriptions,
        bills=bills,
    )


@bp.route("/appointments")
@login_required
@role_required("patient")
def patient_appointments():
    patient_id = _patient_id()
    appointments = fetch_all(
        """
        SELECT a.appt_id, a.appt_date, a.appt_time, a.reason, a.status, u.name AS doctor_name
        FROM appointments a
        JOIN doctors d ON d.doctor_id = a.doctor_id
        JOIN users u ON u.user_id = d.user_id
        WHERE a.patient_id = %s
        ORDER BY a.appt_date DESC, a.appt_time DESC
        """,
        (patient_id,),
    )
    return render_template(
        "patient/appointments.html", active_page="appointments", appointments=appointments
    )


@bp.route("/appointments/book")
@login_required
@role_required("patient")
def patient_book_appointment():
    return redirect(url_for("appointments.booking_wizard"))


@bp.route("/prescriptions")
@login_required
@role_required("patient")
def patient_prescriptions():
    patient_id = _patient_id()
    prescriptions = fetch_all(
        """
        SELECT pr.prescription_id, pr.dosage, pr.duration, pr.instructions, pr.created_at,
               m.name AS medicine_name, a.appt_date, du.name AS doctor_name
        FROM prescriptions pr
        JOIN appointments a ON a.appt_id = pr.appt_id
        JOIN doctors d ON d.doctor_id = a.doctor_id
        JOIN users du ON du.user_id = d.user_id
        JOIN medicines m ON m.medicine_id = pr.medicine_id
        WHERE a.patient_id = %s
        ORDER BY pr.created_at DESC
        """,
        (patient_id,),
    )
    return render_template(
        "patient/prescriptions.html",
        active_page="prescriptions",
        prescriptions=prescriptions,
    )


@bp.route("/bills")
@login_required
@role_required("patient")
def patient_bills():
    patient_id = _patient_id()
    bills = fetch_all(
        """
        SELECT bill_id, consultation_fee, room_charges, medicine_charges, subtotal, tax, total, status, created_at
        FROM bills
        WHERE patient_id = %s
        ORDER BY created_at DESC
        """,
        (patient_id,),
    )
    return render_template("patient/bills.html", active_page="bills", bills=bills)


@bp.route("/bills/<int:bill_id>/pdf")
@login_required
@role_required("patient")
def patient_bill_pdf(bill_id: int):
    return redirect(url_for("billing.bill_pdf", bill_id=bill_id))


@bp.route("/profile", methods=["GET", "POST"])
@login_required
@role_required("patient")
def patient_profile():
    patient = fetch_one(
        """
        SELECT p.*, u.name, u.email
        FROM patients p
        JOIN users u ON u.user_id = p.user_id
        WHERE p.user_id = %s
        """,
        (session["user_id"],),
    )
    if request.method == "POST":
        name = request.form.get("name", "").strip()
        phone = request.form.get("phone", "").strip()
        address = request.form.get("address", "").strip() or None
        emergency_contact = request.form.get("emergency_contact", "").strip() or None

        execute(
            "UPDATE users SET name = %s WHERE user_id = %s",
            (name, session["user_id"]),
        )
        execute(
            "UPDATE patients SET phone = %s, address = %s, emergency_contact = %s WHERE patient_id = %s",
            (phone, address, emergency_contact, patient["patient_id"]),
        )
        flash("Profile updated.", "success")
        return redirect(url_for("patient.patient_profile"))

    return render_template("patient/profile.html", active_page="profile", patient=patient)
