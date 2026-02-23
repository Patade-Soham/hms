from datetime import datetime

from flask import Blueprint, abort, flash, jsonify, redirect, render_template, request, session, url_for

from routes.db import execute, fetch_all, fetch_one
from routes.decorators import login_required, role_required

bp = Blueprint("appointments", __name__)

TIME_SLOTS = [
    "09:00:00",
    "09:30:00",
    "10:00:00",
    "10:30:00",
    "11:00:00",
    "11:30:00",
    "12:00:00",
    "12:30:00",
    "14:00:00",
    "14:30:00",
    "15:00:00",
    "15:30:00",
    "16:00:00",
    "16:30:00",
]


def _current_patient_id():
    user_id = session.get("user_id")
    row = fetch_one("SELECT patient_id FROM patients WHERE user_id = %s", (user_id,))
    return row["patient_id"] if row else None


def _current_doctor_id():
    user_id = session.get("user_id")
    row = fetch_one("SELECT doctor_id FROM doctors WHERE user_id = %s", (user_id,))
    return row["doctor_id"] if row else None


@bp.route("/admin/appointments")
@login_required
@role_required("admin")
def admin_appointments():
    date_filter = request.args.get("date", "").strip()
    doctor_filter = request.args.get("doctor_id", "").strip()
    status_filter = request.args.get("status", "").strip()

    clauses = ["1=1"]
    params = []
    if date_filter:
        clauses.append("a.appt_date = %s")
        params.append(date_filter)
    if doctor_filter:
        clauses.append("a.doctor_id = %s")
        params.append(doctor_filter)
    if status_filter:
        clauses.append("a.status = %s")
        params.append(status_filter)

    appointments = fetch_all(
        f"""
        SELECT a.appt_id, a.appt_date, a.appt_time, a.reason, a.status,
               pu.name AS patient_name, du.name AS doctor_name
        FROM appointments a
        JOIN patients p ON p.patient_id = a.patient_id
        JOIN users pu ON pu.user_id = p.user_id
        JOIN doctors d ON d.doctor_id = a.doctor_id
        JOIN users du ON du.user_id = d.user_id
        WHERE {' AND '.join(clauses)}
        ORDER BY a.appt_date DESC, a.appt_time DESC
        """,
        tuple(params),
    )
    doctors = fetch_all(
        """
        SELECT d.doctor_id, u.name
        FROM doctors d
        JOIN users u ON u.user_id = d.user_id
        WHERE d.is_active = 1
        ORDER BY u.name
        """
    )
    return render_template(
        "admin/appointments/list.html",
        active_page="appointments",
        appointments=appointments,
        doctors=doctors,
    )


@bp.route("/appointments/book")
@login_required
def booking_wizard():
    doctors = fetch_all(
        """
        SELECT d.doctor_id, u.name, d.specialization, dep.dept_name, d.consultation_fee
        FROM doctors d
        JOIN users u ON u.user_id = d.user_id
        LEFT JOIN departments dep ON dep.dept_id = d.dept_id
        WHERE d.is_active = 1
        ORDER BY u.name
        """
    )
    patients = []
    if session.get("role") == "admin":
        patients = fetch_all(
            """
            SELECT p.patient_id, p.patient_code, u.name
            FROM patients p
            JOIN users u ON u.user_id = p.user_id
            WHERE p.is_active = 1
            ORDER BY u.name
            """
        )

    return render_template(
        "admin/appointments/book.html",
        active_page="appointments",
        doctors=doctors,
        patients=patients,
    )


@bp.route("/appointments/book/slots", methods=["POST"])
@login_required
def available_slots():
    doctor_id = request.form.get("doctor_id")
    appt_date = request.form.get("appt_date")
    if not doctor_id or not appt_date:
        return jsonify({"slots": []}), 400

    booked_rows = fetch_all(
        """
        SELECT appt_time
        FROM appointments
        WHERE doctor_id = %s
          AND appt_date = %s
          AND status <> 'cancelled'
        """,
        (doctor_id, appt_date),
    )
    booked = {str(row["appt_time"]) for row in booked_rows}
    available = [slot for slot in TIME_SLOTS if slot not in booked]
    return jsonify({"slots": available, "booked": sorted(booked)})


@bp.route("/appointments/book/confirm", methods=["POST"])
@login_required
def confirm_booking():
    doctor_id = request.form.get("doctor_id")
    patient_id = request.form.get("patient_id")
    appt_date = request.form.get("appt_date")
    appt_time = request.form.get("appt_time")
    reason = request.form.get("reason", "").strip() or "General Consultation"

    role = session.get("role")
    if role == "patient":
        patient_id = _current_patient_id()
    elif role != "admin":
        return abort(403)

    if not all([doctor_id, patient_id, appt_date, appt_time]):
        flash("Please complete all appointment fields.", "danger")
        return redirect(url_for("appointments.booking_wizard"))

    conflict = fetch_one(
        """
        SELECT appt_id
        FROM appointments
        WHERE doctor_id = %s AND appt_date = %s AND appt_time = %s AND status <> 'cancelled'
        """,
        (doctor_id, appt_date, appt_time),
    )
    if conflict:
        flash("Selected time slot is no longer available.", "warning")
        return redirect(url_for("appointments.booking_wizard"))

    execute(
        """
        INSERT INTO appointments (
            patient_id, doctor_id, appt_date, appt_time, reason, status, created_at, updated_at
        ) VALUES (%s, %s, %s, %s, %s, 'pending', %s, %s)
        """,
        (patient_id, doctor_id, appt_date, appt_time, reason, datetime.utcnow(), datetime.utcnow()),
    )
    flash("Appointment booked successfully.", "success")
    if role == "patient":
        return redirect(url_for("patient.patient_appointments"))
    return redirect(url_for("appointments.admin_appointments"))


@bp.route("/appointments/<int:appt_id>")
@login_required
def appointment_detail(appt_id: int):
    appt = fetch_one(
        """
        SELECT a.*, pu.name AS patient_name, p.patient_code, du.name AS doctor_name
        FROM appointments a
        JOIN patients p ON p.patient_id = a.patient_id
        JOIN users pu ON pu.user_id = p.user_id
        JOIN doctors d ON d.doctor_id = a.doctor_id
        JOIN users du ON du.user_id = d.user_id
        WHERE a.appt_id = %s
        """,
        (appt_id,),
    )
    if not appt:
        flash("Appointment not found.", "warning")
        return redirect(url_for("dashboard.admin_dashboard"))

    role = session.get("role")
    if role == "doctor":
        doctor_id = _current_doctor_id()
        if doctor_id != appt["doctor_id"]:
            return abort(403)
    if role == "patient":
        patient_id = _current_patient_id()
        if patient_id != appt["patient_id"]:
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

    tpl = "admin/appointments/detail.html"
    if role == "doctor":
        tpl = "doctor/appointment_detail.html"
    if role == "patient":
        tpl = "patient/appointment_detail.html"

    return render_template(
        tpl,
        active_page="appointments",
        appt=appt,
        prescriptions=prescriptions,
    )


@bp.route("/appointments/<int:appt_id>/status", methods=["POST"])
@login_required
def update_appointment_status(appt_id: int):
    status = request.form.get("status", "").strip().lower()
    if status not in {"pending", "confirmed", "in_progress", "completed", "cancelled"}:
        flash("Invalid status value.", "danger")
        return redirect(url_for("appointments.appointment_detail", appt_id=appt_id))

    appt = fetch_one("SELECT doctor_id FROM appointments WHERE appt_id = %s", (appt_id,))
    if not appt:
        flash("Appointment not found.", "warning")
        return redirect(url_for("dashboard.admin_dashboard"))

    role = session.get("role")
    if role not in {"admin", "doctor"}:
        return abort(403)
    if role == "doctor":
        doctor_id = _current_doctor_id()
        if doctor_id != appt["doctor_id"]:
            return abort(403)

    execute(
        "UPDATE appointments SET status = %s, updated_at = %s WHERE appt_id = %s",
        (status, datetime.utcnow(), appt_id),
    )
    flash("Appointment status updated.", "success")
    return redirect(url_for("appointments.appointment_detail", appt_id=appt_id))


@bp.route("/appointments/<int:appt_id>/notes", methods=["POST"])
@login_required
def update_appointment_notes(appt_id: int):
    role = session.get("role")
    if role not in {"admin", "doctor"}:
        return abort(403)
    notes = request.form.get("notes", "").strip()
    execute(
        "UPDATE appointments SET notes = %s, updated_at = %s WHERE appt_id = %s",
        (notes, datetime.utcnow(), appt_id),
    )
    flash("Consultation notes saved.", "success")
    return redirect(url_for("appointments.appointment_detail", appt_id=appt_id))
