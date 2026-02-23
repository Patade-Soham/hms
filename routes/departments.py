from flask import Blueprint, flash, redirect, render_template, request, url_for

from routes.db import execute, fetch_all
from routes.decorators import login_required, role_required

bp = Blueprint("departments", __name__, url_prefix="/admin/departments")


@bp.route("", methods=["GET", "POST"])
@login_required
@role_required("admin")
def list_departments():
    if request.method == "POST":
        dept_name = request.form.get("dept_name", "").strip()
        head_doctor_id = request.form.get("head_doctor_id") or None
        if dept_name:
            execute(
                "INSERT INTO departments (dept_name, head_doctor_id) VALUES (%s, %s)",
                (dept_name, head_doctor_id),
            )
            flash("Department added.", "success")
        else:
            flash("Department name is required.", "danger")
        return redirect(url_for("departments.list_departments"))

    departments = fetch_all(
        """
        SELECT dep.dept_id, dep.dept_name, u.name AS head_doctor
        FROM departments dep
        LEFT JOIN doctors d ON d.doctor_id = dep.head_doctor_id
        LEFT JOIN users u ON u.user_id = d.user_id
        ORDER BY dep.dept_name
        """
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
        "admin/departments/list.html",
        active_page="departments",
        departments=departments,
        doctors=doctors,
    )


@bp.route("/<int:dept_id>/edit", methods=["POST"])
@login_required
@role_required("admin")
def edit_department(dept_id: int):
    dept_name = request.form.get("dept_name", "").strip()
    head_doctor_id = request.form.get("head_doctor_id") or None
    execute(
        "UPDATE departments SET dept_name = %s, head_doctor_id = %s WHERE dept_id = %s",
        (dept_name, head_doctor_id, dept_id),
    )
    flash("Department updated.", "success")
    return redirect(url_for("departments.list_departments"))


@bp.route("/<int:dept_id>/delete", methods=["POST"])
@login_required
@role_required("admin")
def delete_department(dept_id: int):
    execute("UPDATE doctors SET dept_id = NULL WHERE dept_id = %s", (dept_id,))
    execute("DELETE FROM departments WHERE dept_id = %s", (dept_id,))
    flash("Department removed.", "success")
    return redirect(url_for("departments.list_departments"))
