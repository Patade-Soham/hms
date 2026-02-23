from datetime import datetime

from flask import Blueprint, flash, redirect, render_template, request, session, url_for

from routes.db import execute, fetch_all
from routes.decorators import login_required, role_required

bp = Blueprint("feedback", __name__)


@bp.route("/patient/feedback", methods=["GET", "POST"])
@login_required
@role_required("patient")
def submit_feedback():
    if request.method == "POST":
        message = request.form.get("message", "").strip()
        if message:
            execute(
                """
                INSERT INTO feedback (user_id, message, submitted_at, status)
                VALUES (%s, %s, %s, 'new')
                """,
                (session["user_id"], message, datetime.utcnow()),
            )
            flash("Feedback submitted. Thank you.", "success")
            return redirect(url_for("feedback.submit_feedback"))
        flash("Feedback message cannot be empty.", "warning")
    return render_template("patient/feedback.html", active_page="feedback")


@bp.route("/admin/feedback")
@login_required
@role_required("admin")
def admin_feedback():
    rows = fetch_all(
        """
        SELECT f.feedback_id, f.message, f.submitted_at, f.status, u.name, u.email
        FROM feedback f
        JOIN users u ON u.user_id = f.user_id
        ORDER BY f.submitted_at DESC
        """
    )
    return render_template(
        "admin/feedback.html", active_page="feedback", feedback_rows=rows
    )


@bp.route("/admin/feedback/<int:feedback_id>/mark-reviewed", methods=["POST"])
@login_required
@role_required("admin")
def mark_feedback_reviewed(feedback_id: int):
    execute("UPDATE feedback SET status = 'reviewed' WHERE feedback_id = %s", (feedback_id,))
    flash("Feedback marked as reviewed.", "success")
    return redirect(url_for("feedback.admin_feedback"))
