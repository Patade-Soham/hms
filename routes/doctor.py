from flask import Blueprint, abort, flash, redirect, render_template, request, session, url_for

from routes.db import execute, fetch_all, fetch_one
from routes.decorators import login_required, role_required

bp = Blueprint("doctor", __name__, url_prefix="/doctor")


def _doctor_id():
    row = fetch_one("SELECT doctor_id FROM doctors WHERE user_id = %s", (session["user_id"],))
    return row["doctor_id"] if row else None


@bp.route("/dashboard")
@login_required
@role_required("doctor")
def doctor_dashboard():
    doctor_id = _doctor_id()
    today_schedule = fetch_all(
        """
        SELECT a.appt_id, a.appt_time, a.reason, a.status, u.name AS patient_name
        FROM appointments a
        JOIN patients p ON p.patient_id = a.patient_id
        JOIN users u ON u.user_id = p.user_id
        WHERE a.doctor_id = %s AND a.appt_date = CURDATE()
        ORDER BY a.appt_time
        """,
        (doctor_id,),
    )
    recent_patients = fetch_all(
        """
        SELECT DISTINCT p.patient_id, p.patient_code, u.name
        FROM appointments a
        JOIN patients p ON p.patient_id = a.patient_id
        JOIN users u ON u.user_id = p.user_id
        WHERE a.doctor_id = %s
        ORDER BY a.updated_at DESC
        LIMIT 10
        """,
        (doctor_id,),
    )
    return render_template(
        "doctor/dashboard.html",
        active_page="dashboard",
        today_schedule=today_schedule,
        recent_patients=recent_patients,
    )


@bp.route("/appointments")
@login_required
@role_required("doctor")
def doctor_appointments():
    doctor_id = _doctor_id()
    appointments = fetch_all(
        """
        SELECT a.appt_id, a.appt_date, a.appt_time, a.reason, a.status, u.name AS patient_name
        FROM appointments a
        JOIN patients p ON p.patient_id = a.patient_id
        JOIN users u ON u.user_id = p.user_id
        WHERE a.doctor_id = %s
        ORDER BY a.appt_date DESC, a.appt_time DESC
        """,
        (doctor_id,),
    )
    return render_template(
        "doctor/appointments.html", active_page="appointments", appointments=appointments
    )


@bp.route("/appointments/<int:appt_id>")
@login_required
@role_required("doctor")
def doctor_appointment_detail(appt_id: int):
    doctor_id = _doctor_id()
    appt = fetch_one(
        """
        SELECT a.*, pu.name AS patient_name, p.patient_code
        FROM appointments a
        JOIN patients p ON p.patient_id = a.patient_id
        JOIN users pu ON pu.user_id = p.user_id
        WHERE a.appt_id = %s
        """,
        (appt_id,),
    )
    if not appt or appt["doctor_id"] != doctor_id:
        return abort(403)
    prescriptions = fetch_all(
        """
        SELECT pr.prescription_id, m.name AS medicine_name, pr.dosage, pr.duration, pr.instructions
        FROM prescriptions pr
        JOIN medicines m ON m.medicine_id = pr.medicine_id
        WHERE pr.appt_id = %s
        ORDER BY pr.prescription_id DESC
        """,
        (appt_id,),
    )
    meds = fetch_all(
        "SELECT medicine_id, name FROM medicines WHERE is_active = 1 ORDER BY name"
    )
    return render_template(
        "doctor/appointment_detail.html",
        active_page="appointments",
        appt=appt,
        prescriptions=prescriptions,
        medicines=meds,
    )


@bp.route("/appointments/<int:appt_id>/status", methods=["POST"])
@login_required
@role_required("doctor")
def doctor_update_status(appt_id: int):
    status = request.form.get("status", "").strip().lower()
    if status not in {"pending", "confirmed", "in_progress", "completed", "cancelled"}:
        flash("Invalid status.", "danger")
        return redirect(url_for("doctor.doctor_appointment_detail", appt_id=appt_id))
    execute("UPDATE appointments SET status = %s WHERE appt_id = %s", (status, appt_id))
    flash("Appointment status updated.", "success")
    return redirect(url_for("doctor.doctor_appointment_detail", appt_id=appt_id))


@bp.route("/prescriptions/new", methods=["POST"])
@login_required
@role_required("doctor")
def doctor_new_prescription():
    appt_id = request.form.get("appt_id")
    medicine_id = request.form.get("medicine_id")
    dosage = request.form.get("dosage", "").strip()
    duration = request.form.get("duration", "").strip()
    instructions = request.form.get("instructions", "").strip() or None

    if not all([appt_id, medicine_id, dosage, duration]):
        flash("All prescription fields are required.", "danger")
        return redirect(url_for("doctor.doctor_appointments"))

    execute(
        """
        INSERT INTO prescriptions (appt_id, medicine_id, dosage, duration, instructions, created_at)
        VALUES (%s, %s, %s, %s, %s, NOW())
        """,
        (appt_id, medicine_id, dosage, duration, instructions),
    )
    flash("Prescription submitted.", "success")
    return redirect(url_for("doctor.doctor_appointment_detail", appt_id=appt_id))


@bp.route("/patients")
@login_required
@role_required("doctor")
def doctor_patients():
    doctor_id = _doctor_id()
    patients = fetch_all(
        """
        SELECT DISTINCT p.patient_id, p.patient_code, u.name, p.phone
        FROM appointments a
        JOIN patients p ON p.patient_id = a.patient_id
        JOIN users u ON u.user_id = p.user_id
        WHERE a.doctor_id = %s
        ORDER BY u.name
        """,
        (doctor_id,),
    )
    return render_template("doctor/patients.html", active_page="patients", patients=patients)
