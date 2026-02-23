from datetime import datetime

from flask import Blueprint, flash, redirect, render_template, request, url_for
from werkzeug.security import generate_password_hash

from routes.db import execute, fetch_all, fetch_one, get_db, rollback
from routes.decorators import login_required, role_required

bp = Blueprint("doctors", __name__, url_prefix="/admin/doctors")


@bp.route("")
@login_required
@role_required("admin")
def list_doctors():
    doctors = fetch_all(
        """
        SELECT d.doctor_id, d.specialization, d.license_no, d.available_days, d.consultation_fee,
               d.is_active, u.name, u.email, dep.dept_name
        FROM doctors d
        JOIN users u ON u.user_id = d.user_id
        LEFT JOIN departments dep ON dep.dept_id = d.dept_id
        WHERE d.is_active = 1
        ORDER BY u.name
        """
    )
    return render_template(
        "admin/doctors/list.html", active_page="doctors", doctors=doctors
    )


@bp.route("/new", methods=["GET", "POST"])
@login_required
@role_required("admin")
def new_doctor():
    departments = fetch_all("SELECT dept_id, dept_name FROM departments ORDER BY dept_name")
    if request.method == "POST":
        name = request.form.get("name", "").strip()
        email = request.form.get("email", "").strip().lower()
        password = request.form.get("password", "").strip() or "doctor123"
        specialization = request.form.get("specialization", "").strip()
        dept_id = request.form.get("dept_id") or None
        license_no = request.form.get("license_no", "").strip()
        available_days = request.form.get("available_days", "").strip()
        consultation_fee = float(request.form.get("consultation_fee", 0) or 0)
        phone = request.form.get("phone", "").strip() or None

        if not name or not email or not specialization or not license_no:
            flash("Missing required doctor fields.", "danger")
            return render_template(
                "admin/doctors/form.html", active_page="doctors", departments=departments
            )

        conn = get_db()
        try:
            user_id = execute(
                """
                INSERT INTO users (name, email, password_hash, role, created_at)
                VALUES (%s, %s, %s, 'doctor', %s)
                """,
                (name, email, generate_password_hash(password), datetime.utcnow()),
                commit=False,
            )
            execute(
                """
                INSERT INTO doctors (
                    user_id, dept_id, specialization, license_no, available_days, consultation_fee, phone, is_active, created_at
                ) VALUES (%s, %s, %s, %s, %s, %s, %s, 1, %s)
                """,
                (
                    user_id,
                    dept_id,
                    specialization,
                    license_no,
                    available_days,
                    consultation_fee,
                    phone,
                    datetime.utcnow(),
                ),
                commit=False,
            )
            conn.commit()
        except Exception:
            rollback()
            flash("Unable to add doctor.", "danger")
            return render_template(
                "admin/doctors/form.html", active_page="doctors", departments=departments
            )

        flash("Doctor created.", "success")
        return redirect(url_for("doctors.list_doctors"))

    return render_template(
        "admin/doctors/form.html", active_page="doctors", departments=departments
    )


@bp.route("/<int:doctor_id>")
@login_required
@role_required("admin")
def doctor_detail(doctor_id: int):
    doctor = fetch_one(
        """
        SELECT d.*, u.name, u.email, dep.dept_name
        FROM doctors d
        JOIN users u ON u.user_id = d.user_id
        LEFT JOIN departments dep ON dep.dept_id = d.dept_id
        WHERE d.doctor_id = %s
        """,
        (doctor_id,),
    )
    if not doctor:
        flash("Doctor not found.", "warning")
        return redirect(url_for("doctors.list_doctors"))

    appointments = fetch_all(
        """
        SELECT a.appt_id, a.appt_date, a.appt_time, a.status, u.name AS patient_name
        FROM appointments a
        JOIN patients p ON p.patient_id = a.patient_id
        JOIN users u ON u.user_id = p.user_id
        WHERE a.doctor_id = %s
        ORDER BY a.appt_date DESC, a.appt_time DESC
        LIMIT 25
        """,
        (doctor_id,),
    )
    return render_template(
        "admin/doctors/detail.html",
        active_page="doctors",
        doctor=doctor,
        appointments=appointments,
    )


@bp.route("/<int:doctor_id>/edit", methods=["GET", "POST"])
@login_required
@role_required("admin")
def edit_doctor(doctor_id: int):
    departments = fetch_all("SELECT dept_id, dept_name FROM departments ORDER BY dept_name")
    doctor = fetch_one(
        """
        SELECT d.*, u.name, u.email
        FROM doctors d
        JOIN users u ON u.user_id = d.user_id
        WHERE d.doctor_id = %s
        """,
        (doctor_id,),
    )
    if not doctor:
        flash("Doctor not found.", "warning")
        return redirect(url_for("doctors.list_doctors"))

    if request.method == "POST":
        name = request.form.get("name", "").strip()
        email = request.form.get("email", "").strip().lower()
        specialization = request.form.get("specialization", "").strip()
        dept_id = request.form.get("dept_id") or None
        license_no = request.form.get("license_no", "").strip()
        available_days = request.form.get("available_days", "").strip()
        consultation_fee = float(request.form.get("consultation_fee", 0) or 0)
        phone = request.form.get("phone", "").strip() or None

        conn = get_db()
        try:
            execute(
                "UPDATE users SET name = %s, email = %s WHERE user_id = %s",
                (name, email, doctor["user_id"]),
                commit=False,
            )
            execute(
                """
                UPDATE doctors
                SET dept_id = %s, specialization = %s, license_no = %s, available_days = %s,
                    consultation_fee = %s, phone = %s
                WHERE doctor_id = %s
                """,
                (
                    dept_id,
                    specialization,
                    license_no,
                    available_days,
                    consultation_fee,
                    phone,
                    doctor_id,
                ),
                commit=False,
            )
            conn.commit()
        except Exception:
            rollback()
            flash("Unable to update doctor.", "danger")
            return render_template(
                "admin/doctors/form.html",
                active_page="doctors",
                doctor=doctor,
                edit_mode=True,
                departments=departments,
            )

        flash("Doctor updated.", "success")
        return redirect(url_for("doctors.doctor_detail", doctor_id=doctor_id))

    return render_template(
        "admin/doctors/form.html",
        active_page="doctors",
        doctor=doctor,
        edit_mode=True,
        departments=departments,
    )


@bp.route("/<int:doctor_id>/delete", methods=["POST"])
@login_required
@role_required("admin")
def delete_doctor(doctor_id: int):
    execute("UPDATE doctors SET is_active = 0 WHERE doctor_id = %s", (doctor_id,))
    flash("Doctor archived.", "success")
    return redirect(url_for("doctors.list_doctors"))
