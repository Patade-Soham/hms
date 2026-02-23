from functools import wraps

from flask import abort, flash, redirect, request, session, url_for

from routes.db import fetch_one


def login_required(view):
    @wraps(view)
    def wrapped_view(*args, **kwargs):
        if session.get("user_id") is None:
            flash("Please login first.", "warning")
            return redirect(url_for("auth.login", next=request.path))
        return view(*args, **kwargs)

    return wrapped_view


def role_required(*roles):
    allowed = {role.lower() for role in roles}

    def decorator(view):
        @wraps(view)
        def wrapped_view(*args, **kwargs):
            if session.get("role", "").lower() not in allowed:
                return abort(403)
            return view(*args, **kwargs)

        return wrapped_view

    return decorator


def current_user():
    user_id = session.get("user_id")
    if not user_id:
        return None
    return fetch_one(
        "SELECT user_id, name, email, role FROM users WHERE user_id = %s", (user_id,)
    )


def role_home(role: str):
    role = (role or "").lower()
    if role == "admin":
        return "dashboard.admin_dashboard"
    if role == "doctor":
        return "doctor.doctor_dashboard"
    return "patient.patient_dashboard"
