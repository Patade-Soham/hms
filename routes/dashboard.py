from flask import Blueprint, render_template

from routes.db import fetch_all, fetch_one
from routes.decorators import login_required, role_required

bp = Blueprint("dashboard", __name__, url_prefix="/admin")


@bp.route("/dashboard")
@login_required
@role_required("admin")
def admin_dashboard():
    stats = {
        "total_patients": fetch_one(
            "SELECT COUNT(*) AS value FROM patients WHERE is_active = 1"
        )["value"],
        "appointments_today": fetch_one(
            "SELECT COUNT(*) AS value FROM appointments WHERE appt_date = CURDATE()"
        )["value"],
        "revenue": fetch_one(
            "SELECT COALESCE(SUM(total), 0) AS value FROM bills WHERE status = 'paid'"
        )["value"],
        "available_beds": fetch_one(
            "SELECT COUNT(*) AS value FROM rooms WHERE status = 'available'"
        )["value"],
    }

    monthly = fetch_all(
        """
        SELECT DATE_FORMAT(appt_date, '%%Y-%%m') AS month, COUNT(*) AS total
        FROM appointments
        WHERE appt_date >= DATE_SUB(CURDATE(), INTERVAL 12 MONTH)
        GROUP BY DATE_FORMAT(appt_date, '%%Y-%%m')
        ORDER BY month
        """
    )

    recent_registrations = fetch_all(
        """
        SELECT p.patient_code, u.name, u.created_at
        FROM patients p
        JOIN users u ON u.user_id = p.user_id
        ORDER BY u.created_at DESC
        LIMIT 5
        """
    )
    recent_appointments = fetch_all(
        """
        SELECT a.appt_id, a.appt_date, a.appt_time, a.status, pu.name AS patient_name, du.name AS doctor_name
        FROM appointments a
        JOIN patients p ON p.patient_id = a.patient_id
        JOIN users pu ON pu.user_id = p.user_id
        JOIN doctors d ON d.doctor_id = a.doctor_id
        JOIN users du ON du.user_id = d.user_id
        ORDER BY a.created_at DESC
        LIMIT 5
        """
    )

    rooms = fetch_all(
        """
        SELECT r.room_id, r.room_number, r.type, r.status, u.name AS patient_name, ad.admitted_on
        FROM rooms r
        LEFT JOIN admissions ad ON ad.room_id = r.room_id AND ad.discharged_on IS NULL
        LEFT JOIN patients p ON p.patient_id = ad.patient_id
        LEFT JOIN users u ON u.user_id = p.user_id
        ORDER BY r.room_number
        """
    )

    return render_template(
        "admin/dashboard.html",
        active_page="dashboard",
        stats=stats,
        monthly=monthly,
        recent_registrations=recent_registrations,
        recent_appointments=recent_appointments,
        rooms=rooms,
    )
