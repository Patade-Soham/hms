from datetime import date

from flask import Blueprint, flash, redirect, render_template, request, url_for

from routes.db import execute, fetch_all, fetch_one, get_db, rollback
from routes.decorators import login_required, role_required

bp = Blueprint("rooms", __name__)


@bp.route("/admin/rooms")
@login_required
@role_required("admin")
def room_grid():
    room_type = request.args.get("type", "").strip().lower()
    status = request.args.get("status", "").strip().lower()

    clauses = ["1=1"]
    params = []
    if room_type:
        clauses.append("r.type = %s")
        params.append(room_type)
    if status:
        clauses.append("r.status = %s")
        params.append(status)

    rooms = fetch_all(
        f"""
        SELECT r.room_id, r.room_number, r.type, r.floor, r.status, r.price_per_day,
               u.name AS patient_name, ad.admission_id, ad.admitted_on
        FROM rooms r
        LEFT JOIN admissions ad ON ad.room_id = r.room_id AND ad.discharged_on IS NULL
        LEFT JOIN patients p ON p.patient_id = ad.patient_id
        LEFT JOIN users u ON u.user_id = p.user_id
        WHERE {' AND '.join(clauses)}
        ORDER BY r.room_number
        """,
        tuple(params),
    )
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
        "admin/rooms/grid.html", active_page="rooms", rooms=rooms, patients=patients
    )


@bp.route("/admin/rooms/new", methods=["POST"])
@login_required
@role_required("admin")
def add_room():
    room_number = request.form.get("room_number", "").strip()
    room_type = request.form.get("type", "general")
    floor = request.form.get("floor", "").strip() or None
    price_per_day = float(request.form.get("price_per_day", 0) or 0)
    if not room_number:
        flash("Room number is required.", "danger")
        return redirect(url_for("rooms.room_grid"))

    execute(
        """
        INSERT INTO rooms (room_number, type, floor, status, price_per_day)
        VALUES (%s, %s, %s, 'available', %s)
        """,
        (room_number, room_type, floor, price_per_day),
    )
    flash("Room added.", "success")
    return redirect(url_for("rooms.room_grid"))


@bp.route("/admin/rooms/<int:room_id>/admit", methods=["POST"])
@login_required
@role_required("admin")
def admit_patient(room_id: int):
    patient_id = request.form.get("patient_id")
    if not patient_id:
        flash("Select a patient first.", "warning")
        return redirect(url_for("rooms.room_grid"))

    room = fetch_one("SELECT status FROM rooms WHERE room_id = %s", (room_id,))
    if not room or room["status"] == "occupied":
        flash("Room is not available.", "danger")
        return redirect(url_for("rooms.room_grid"))

    conn = get_db()
    try:
        execute(
            """
            INSERT INTO admissions (patient_id, room_id, admitted_on)
            VALUES (%s, %s, %s)
            """,
            (patient_id, room_id, date.today()),
            commit=False,
        )
        execute(
            "UPDATE rooms SET status = 'occupied' WHERE room_id = %s",
            (room_id,),
            commit=False,
        )
        conn.commit()
    except Exception:
        rollback()
        flash("Unable to admit patient.", "danger")
        return redirect(url_for("rooms.room_grid"))

    flash("Patient admitted successfully.", "success")
    return redirect(url_for("rooms.room_grid"))


@bp.route("/admin/admissions/<int:admission_id>/discharge", methods=["POST"])
@login_required
@role_required("admin")
def discharge_patient(admission_id: int):
    admission = fetch_one(
        "SELECT room_id FROM admissions WHERE admission_id = %s", (admission_id,)
    )
    if not admission:
        flash("Admission record not found.", "warning")
        return redirect(url_for("rooms.room_grid"))

    conn = get_db()
    try:
        execute(
            """
            UPDATE admissions
            SET discharged_on = %s
            WHERE admission_id = %s
            """,
            (date.today(), admission_id),
            commit=False,
        )
        execute(
            "UPDATE rooms SET status = 'available' WHERE room_id = %s",
            (admission["room_id"],),
            commit=False,
        )
        conn.commit()
    except Exception:
        rollback()
        flash("Unable to discharge patient.", "danger")
        return redirect(url_for("rooms.room_grid"))

    flash("Patient discharged and room released.", "success")
    return redirect(url_for("rooms.room_grid"))


@bp.route("/admin/admissions/<int:patient_id>")
@login_required
@role_required("admin")
def admission_history(patient_id: int):
    history = fetch_all(
        """
        SELECT ad.admission_id, ad.admitted_on, ad.discharged_on, r.room_number, r.type
        FROM admissions ad
        JOIN rooms r ON r.room_id = ad.room_id
        WHERE ad.patient_id = %s
        ORDER BY ad.admitted_on DESC
        """,
        (patient_id,),
    )
    patient = fetch_one(
        """
        SELECT p.patient_id, p.patient_code, u.name
        FROM patients p
        JOIN users u ON u.user_id = p.user_id
        WHERE p.patient_id = %s
        """,
        (patient_id,),
    )
    return render_template(
        "admin/rooms/history.html",
        active_page="rooms",
        history=history,
        patient=patient,
    )
