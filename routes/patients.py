from datetime import datetime

from flask import Blueprint, flash, jsonify, redirect, render_template, request, url_for
from werkzeug.security import generate_password_hash

from routes.db import execute, fetch_all, fetch_one, get_db, rollback
from routes.decorators import login_required, role_required

bp = Blueprint("patients", __name__, url_prefix="/admin/patients")


def _next_patient_code():
    row = fetch_one("SELECT COALESCE(MAX(patient_id), 0) + 1 AS next_id FROM patients")
    return f"PAT-{row['next_id']:04d}"


@bp.route("")
@login_required
@role_required("admin")
def list_patients():
    page = max(int(request.args.get("page", 1)), 1)
    per_page = 10
    offset = (page - 1) * per_page

    patients = fetch_all(
        """
        SELECT p.patient_id, p.patient_code, p.dob, p.gender, p.blood_group, p.phone,
               p.is_active, u.name, u.email
        FROM patients p
        JOIN users u ON u.user_id = p.user_id
        WHERE p.is_active = 1
        ORDER BY p.patient_id DESC
        LIMIT %s OFFSET %s
        """,
        (per_page, offset),
    )
    total = fetch_one(
        "SELECT COUNT(*) AS value FROM patients WHERE is_active = 1"
    )["value"]

    return render_template(
        "admin/patients/list.html",
        active_page="patients",
        patients=patients,
        page=page,
        per_page=per_page,
        total=total,
    )


@bp.route("/search")
@login_required
@role_required("admin")
def search_patients():
    q = request.args.get("q", "").strip()
    like = f"%{q}%"
    rows = fetch_all(
        """
        SELECT p.patient_id, p.patient_code, u.name, p.phone, p.blood_group
        FROM patients p
        JOIN users u ON u.user_id = p.user_id
        WHERE p.is_active = 1
        AND (u.name LIKE %s OR p.patient_code LIKE %s OR p.phone LIKE %s)
        ORDER BY u.name
        LIMIT 25
        """,
        (like, like, like),
    )
    return jsonify(rows)


@bp.route("/new", methods=["GET", "POST"])
@login_required
@role_required("admin")
def new_patient():
    if request.method == "POST":
        name = request.form.get("name", "").strip()
        email = request.form.get("email", "").strip().lower()
        password = request.form.get("password", "").strip() or "patient123"
        phone = request.form.get("phone", "").strip()
        dob = request.form.get("dob") or None
        gender = request.form.get("gender", "other")
        blood_group = request.form.get("blood_group", "").strip().upper() or None
        address = request.form.get("address", "").strip() or None
        emergency_contact = request.form.get("emergency_contact", "").strip() or None

        if not name or not email or not phone:
            flash("Name, email and phone are required.", "danger")
            return render_template("admin/patients/form.html", active_page="patients")

        if fetch_one("SELECT user_id FROM users WHERE email = %s", (email,)):
            flash("Email already exists.", "warning")
            return render_template("admin/patients/form.html", active_page="patients")

        conn = get_db()
        try:
            user_id = execute(
                """
                INSERT INTO users (name, email, password_hash, role, created_at)
                VALUES (%s, %s, %s, 'patient', %s)
                """,
                (name, email, generate_password_hash(password), datetime.utcnow()),
                commit=False,
            )
            execute(
                """
                INSERT INTO patients (
                    user_id, patient_code, dob, gender, blood_group, phone, address,
                    emergency_contact, is_active, created_at
                ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, 1, %s)
                """,
                (
                    user_id,
                    _next_patient_code(),
                    dob,
                    gender,
                    blood_group,
                    phone,
                    address,
                    emergency_contact,
                    datetime.utcnow(),
                ),
                commit=False,
            )
            conn.commit()
        except Exception:
            rollback()
            flash("Unable to add patient.", "danger")
            return render_template("admin/patients/form.html", active_page="patients")

        flash("Patient added successfully.", "success")
        return redirect(url_for("patients.list_patients"))

    return render_template("admin/patients/form.html", active_page="patients")


@bp.route("/<int:patient_id>")
@login_required
@role_required("admin")
def patient_detail(patient_id: int):
    patient = fetch_one(
        """
        SELECT p.*, u.name, u.email
        FROM patients p
        JOIN users u ON u.user_id = p.user_id
        WHERE p.patient_id = %s
        """,
        (patient_id,),
    )
    if not patient:
        flash("Patient not found.", "warning")
        return redirect(url_for("patients.list_patients"))

    visits = fetch_all(
        """
        SELECT a.appt_id, a.appt_date, a.appt_time, a.status, a.notes, u.name AS doctor_name
        FROM appointments a
        JOIN doctors d ON d.doctor_id = a.doctor_id
        JOIN users u ON u.user_id = d.user_id
        WHERE a.patient_id = %s
        ORDER BY a.appt_date DESC, a.appt_time DESC
        """,
        (patient_id,),
    )
    bills = fetch_all(
        """
        SELECT bill_id, total, status, created_at
        FROM bills
        WHERE patient_id = %s
        ORDER BY created_at DESC
        """,
        (patient_id,),
    )

    return render_template(
        "admin/patients/detail.html",
        active_page="patients",
        patient=patient,
        visits=visits,
        bills=bills,
    )


@bp.route("/<int:patient_id>/edit", methods=["GET", "POST"])
@login_required
@role_required("admin")
def edit_patient(patient_id: int):
    patient = fetch_one(
        """
        SELECT p.*, u.name, u.email
        FROM patients p
        JOIN users u ON u.user_id = p.user_id
        WHERE p.patient_id = %s
        """,
        (patient_id,),
    )
    if not patient:
        flash("Patient not found.", "warning")
        return redirect(url_for("patients.list_patients"))

    if request.method == "POST":
        name = request.form.get("name", "").strip()
        email = request.form.get("email", "").strip().lower()
        phone = request.form.get("phone", "").strip()
        dob = request.form.get("dob") or None
        gender = request.form.get("gender", "other")
        blood_group = request.form.get("blood_group", "").strip().upper() or None
        address = request.form.get("address", "").strip() or None
        emergency_contact = request.form.get("emergency_contact", "").strip() or None

        conn = get_db()
        try:
            execute(
                "UPDATE users SET name = %s, email = %s WHERE user_id = %s",
                (name, email, patient["user_id"]),
                commit=False,
            )
            execute(
                """
                UPDATE patients
                SET dob = %s, gender = %s, blood_group = %s, phone = %s, address = %s, emergency_contact = %s
                WHERE patient_id = %s
                """,
                (
                    dob,
                    gender,
                    blood_group,
                    phone,
                    address,
                    emergency_contact,
                    patient_id,
                ),
                commit=False,
            )
            conn.commit()
        except Exception:
            rollback()
            flash("Unable to update patient.", "danger")
            return render_template(
                "admin/patients/form.html",
                active_page="patients",
                patient=patient,
                edit_mode=True,
            )

        flash("Patient updated.", "success")
        return redirect(url_for("patients.patient_detail", patient_id=patient_id))

    return render_template(
        "admin/patients/form.html",
        active_page="patients",
        patient=patient,
        edit_mode=True,
    )


@bp.route("/<int:patient_id>/delete", methods=["POST"])
@login_required
@role_required("admin")
def delete_patient(patient_id: int):
    execute("UPDATE patients SET is_active = 0 WHERE patient_id = %s", (patient_id,))
    flash("Patient archived (soft delete).", "success")
    return redirect(url_for("patients.list_patients"))
