from datetime import datetime

from flask import Blueprint, flash, redirect, render_template, request, session, url_for
from werkzeug.security import check_password_hash, generate_password_hash

from routes.db import execute, fetch_one, get_db, rollback
from routes.decorators import role_home

bp = Blueprint("auth", __name__, url_prefix="/auth")


@bp.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        email = request.form.get("email", "").strip().lower()
        password = request.form.get("password", "")

        user = fetch_one(
            "SELECT user_id, name, email, password_hash, role FROM users WHERE email = %s",
            (email,),
        )

        if not user or not check_password_hash(user["password_hash"], password):
            flash("Invalid email or password.", "danger")
            return render_template("auth/login.html"), 401

        session.clear()
        session["user_id"] = user["user_id"]
        session["role"] = user["role"]
        session["name"] = user["name"]

        flash(f"Welcome back, {user['name']}!", "success")
        return redirect(url_for(role_home(user["role"])))

    return render_template("auth/login.html")


@bp.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        name = request.form.get("name", "").strip()
        email = request.form.get("email", "").strip().lower()
        password = request.form.get("password", "")
        dob = request.form.get("dob") or None
        gender = request.form.get("gender", "other")
        blood_group = request.form.get("blood_group", "").strip().upper() or None
        phone = request.form.get("phone", "").strip()
        address = request.form.get("address", "").strip() or None
        emergency_contact = request.form.get("emergency_contact", "").strip() or None

        if not name or not email or not password or not phone:
            flash("Name, email, password, and phone are required.", "danger")
            return render_template("auth/register.html"), 400

        if fetch_one("SELECT user_id FROM users WHERE email = %s", (email,)):
            flash("Email is already in use.", "warning")
            return render_template("auth/register.html"), 409

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

            seq_row = fetch_one(
                "SELECT COALESCE(MAX(patient_id), 0) + 1 AS next_id FROM patients"
            )
            patient_code = f"PAT-{seq_row['next_id']:04d}"
            execute(
                """
                INSERT INTO patients (
                    user_id, patient_code, dob, gender, blood_group, phone, address,
                    emergency_contact, is_active, created_at
                ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, 1, %s)
                """,
                (
                    user_id,
                    patient_code,
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
            flash("Registration failed. Please try again.", "danger")
            return render_template("auth/register.html"), 500

        flash("Registration complete. Please login.", "success")
        return redirect(url_for("auth.login"))

    return render_template("auth/register.html")


@bp.route("/logout")
def logout():
    session.clear()
    flash("Logged out successfully.", "success")
    return redirect(url_for("auth.login"))
