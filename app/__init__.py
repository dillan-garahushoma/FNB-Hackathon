from flask import Flask, redirect, url_for, session
from flask_sqlalchemy import SQLAlchemy
from config import Config

db = SQLAlchemy()


def create_app(config_class=Config):
    app = Flask(__name__)
    app.config.from_object(config_class)

    db.init_app(app)

    from app.models import (
        User,
        Pathway,
        WorkProofChallenge,
        WorkProofSubmission,
        SkillsPassport,
        EmployerShortlist,
    )

    from app.routes.auth import auth_bp
    from app.routes.assessment import assessment_bp
    from app.routes.candidate import candidate_bp
    from app.routes.employer import employer_bp

    app.register_blueprint(auth_bp)
    app.register_blueprint(assessment_bp)
    app.register_blueprint(candidate_bp)
    app.register_blueprint(employer_bp)

    @app.route("/")
    def index():
        user_id = session.get("user_id")
        role = session.get("role")
        if user_id and role == "candidate":
            return redirect(url_for("candidate.dashboard"))
        elif user_id and role == "employer":
            return redirect(url_for("employer.dashboard"))
        return redirect(url_for("auth.login"))

    @app.context_processor
    def inject_current_user():
        user = None
        if "user_id" in session:
            user = db.session.get(User, session["user_id"])
        return dict(current_user=user)

    with app.app_context():
        db.create_all()

    return app
