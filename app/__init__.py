from flask import Flask, render_template, redirect, url_for, session
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
        # Find a demo candidate with verified passport for hackathon judges to inspect directly
        demo_candidate = User.query.filter_by(role="candidate").first()
        demo_id = demo_candidate.id if demo_candidate else 1
        return render_template("index.html", demo_candidate_id=demo_id)

    @app.context_processor
    def inject_current_user():
        user = None
        if "user_id" in session:
            user = db.session.get(User, session["user_id"])
        return dict(current_user=user)

    with app.app_context():
        db.create_all()

    return app
