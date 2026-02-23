import os
from datetime import datetime

from dotenv import load_dotenv
from flask import Flask, render_template

from routes import appointments, auth, billing, dashboard, departments, doctor, doctors
from routes import feedback, patient, patients, pharmacy, rooms
from routes.db import init_app as init_db
from routes.decorators import current_user

load_dotenv()


def create_app():
    app = Flask(__name__)
    app.config["SECRET_KEY"] = os.getenv("SECRET_KEY", "dev-secret-key-change-me")

    init_db(app)

    app.register_blueprint(auth.bp)
    app.register_blueprint(dashboard.bp)
    app.register_blueprint(patients.bp)
    app.register_blueprint(doctors.bp)
    app.register_blueprint(departments.bp)
    app.register_blueprint(appointments.bp)
    app.register_blueprint(rooms.bp)
    app.register_blueprint(pharmacy.bp)
    app.register_blueprint(billing.bp)
    app.register_blueprint(doctor.bp)
    app.register_blueprint(patient.bp)
    app.register_blueprint(feedback.bp)

    @app.context_processor
    def inject_globals():
        return {
            "now": datetime.utcnow(),
            "session_user": current_user(),
        }

    @app.errorhandler(403)
    def forbidden(_):
        return render_template("403.html"), 403

    @app.errorhandler(404)
    def not_found(_):
        return render_template("404.html"), 404

    @app.route("/")
    def index():
        return render_template("index.html")

    return app


app = create_app()


if __name__ == "__main__":
    app.run(debug=os.getenv("FLASK_DEBUG", "1") == "1")
