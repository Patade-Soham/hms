from datetime import datetime

from flask import Blueprint, abort, flash, redirect, render_template, request, session, url_for

from routes.db import execute, fetch_all
from routes.decorators import login_required, role_required

bp = Blueprint("pharmacy", __name__)


@bp.route("/admin/pharmacy")
@login_required
@role_required("admin")
def inventory():
    medicines = fetch_all(
        """
        SELECT medicine_id, name, quantity, price, expiry_date,
               CASE WHEN quantity < 10 THEN 1 ELSE 0 END AS low_stock
        FROM medicines
        WHERE is_active = 1
        ORDER BY name
        """
    )
    appointments = fetch_all(
        """
        SELECT a.appt_id, a.appt_date, a.appt_time, pu.name AS patient_name, du.name AS doctor_name
        FROM appointments a
        JOIN patients p ON p.patient_id = a.patient_id
        JOIN users pu ON pu.user_id = p.user_id
        JOIN doctors d ON d.doctor_id = a.doctor_id
        JOIN users du ON du.user_id = d.user_id
        ORDER BY a.appt_date DESC, a.appt_time DESC
        LIMIT 50
        """
    )
    return render_template(
        "admin/pharmacy/inventory.html",
        active_page="pharmacy",
        medicines=medicines,
        appointments=appointments,
    )


@bp.route("/admin/pharmacy/new", methods=["POST"])
@login_required
@role_required("admin")
def add_medicine():
    name = request.form.get("name", "").strip()
    quantity = int(request.form.get("quantity", 0) or 0)
    price = float(request.form.get("price", 0) or 0)
    expiry_date = request.form.get("expiry_date") or None
    if not name:
        flash("Medicine name is required.", "danger")
        return redirect(url_for("pharmacy.inventory"))

    execute(
        """
        INSERT INTO medicines (name, quantity, price, expiry_date, is_active, created_at)
        VALUES (%s, %s, %s, %s, 1, %s)
        """,
        (name, quantity, price, expiry_date, datetime.utcnow()),
    )
    flash("Medicine added.", "success")
    return redirect(url_for("pharmacy.inventory"))


@bp.route("/admin/pharmacy/<int:medicine_id>/edit", methods=["POST"])
@login_required
@role_required("admin")
def edit_medicine(medicine_id: int):
    quantity = int(request.form.get("quantity", 0) or 0)
    price = float(request.form.get("price", 0) or 0)
    expiry_date = request.form.get("expiry_date") or None
    execute(
        "UPDATE medicines SET quantity = %s, price = %s, expiry_date = %s WHERE medicine_id = %s",
        (quantity, price, expiry_date, medicine_id),
    )
    flash("Medicine updated.", "success")
    return redirect(url_for("pharmacy.inventory"))


@bp.route("/admin/pharmacy/<int:medicine_id>/delete", methods=["POST"])
@login_required
@role_required("admin")
def delete_medicine(medicine_id: int):
    execute("UPDATE medicines SET is_active = 0 WHERE medicine_id = %s", (medicine_id,))
    flash("Medicine removed from active inventory.", "success")
    return redirect(url_for("pharmacy.inventory"))


@bp.route("/admin/prescriptions/new", methods=["POST"])
@login_required
def create_prescription():
    role = session.get("role")
    if role not in {"admin", "doctor"}:
        return abort(403)

    appt_id = request.form.get("appt_id")
    medicine_id = request.form.get("medicine_id")
    dosage = request.form.get("dosage", "").strip()
    duration = request.form.get("duration", "").strip()
    instructions = request.form.get("instructions", "").strip() or None

    if not all([appt_id, medicine_id, dosage, duration]):
        flash("Prescription form is incomplete.", "danger")
        return redirect(url_for("pharmacy.inventory"))

    execute(
        """
        INSERT INTO prescriptions (appt_id, medicine_id, dosage, duration, instructions, created_at)
        VALUES (%s, %s, %s, %s, %s, %s)
        """,
        (appt_id, medicine_id, dosage, duration, instructions, datetime.utcnow()),
    )
    execute("UPDATE appointments SET updated_at = %s WHERE appt_id = %s", (datetime.utcnow(), appt_id))
    flash("Prescription recorded.", "success")
    return redirect(url_for("appointments.appointment_detail", appt_id=appt_id))


@bp.route("/admin/prescriptions/<int:appt_id>")
@login_required
def appointment_prescriptions(appt_id: int):
    rows = fetch_all(
        """
        SELECT pr.prescription_id, m.name AS medicine_name, pr.dosage, pr.duration, pr.instructions
        FROM prescriptions pr
        JOIN medicines m ON m.medicine_id = pr.medicine_id
        WHERE pr.appt_id = %s
        ORDER BY pr.prescription_id DESC
        """,
        (appt_id,),
    )
    return render_template(
        "admin/pharmacy/prescriptions.html",
        active_page="pharmacy",
        prescriptions=rows,
        appt_id=appt_id,
    )
