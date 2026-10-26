from functools import wraps
from flask import (
    Blueprint,
    render_template,
    request,
    redirect,
    url_for,
    flash,
    session,
)
from app import db
from app.models import User, SkillsPassport

auth_bp = Blueprint("auth", __name__)


def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if "user_id" not in session:
            flash("Please log in to access this page.", "warning")
            return redirect(url_for("auth.login"))
        return f(*args, **kwargs)

    return decorated_function


def candidate_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if "user_id" not in session:
            flash("Please log in to continue.", "warning")
            return redirect(url_for("auth.login"))
        if session.get("role") != "candidate":
            flash("Access restricted to Candidate accounts.", "error")
            return redirect(url_for("employer.dashboard"))
        return f(*args, **kwargs)

    return decorated_function


def employer_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if "user_id" not in session:
            flash("Please log in to continue.", "warning")
            return redirect(url_for("auth.login"))
        if session.get("role") != "employer":
            flash("Access restricted to Employer accounts.", "error")
            return redirect(url_for("candidate.dashboard"))
        return f(*args, **kwargs)

    return decorated_function


@auth_bp.route("/login", methods=["GET", "POST"])
def login():
    if "user_id" in session:
        if session.get("role") == "employer":
            return redirect(url_for("employer.dashboard"))
        return redirect(url_for("candidate.dashboard"))

    if request.method == "POST":
        email = (request.form.get("email") or "").strip().lower()
        password = request.form.get("password") or ""

        user = User.query.filter_by(email=email).first()
        if user and user.check_password(password):
            session["user_id"] = user.id
            session["role"] = user.role
            session["full_name"] = user.full_name
            flash(f"Welcome back, {user.full_name}!", "success")
            if user.role == "employer":
                return redirect(url_for("employer.dashboard"))
            return redirect(url_for("candidate.dashboard"))
        else:
            flash("Invalid email or password. Try one of the demo accounts below.", "error")

    return render_template("auth/login.html")


@auth_bp.route("/register", methods=["GET", "POST"])
def register():
    if "user_id" in session:
        return redirect(url_for("index"))

    if request.method == "POST":
        full_name = (request.form.get("full_name") or "").strip()
        email = (request.form.get("email") or "").strip().lower()
        password = request.form.get("password") or ""
        role = request.form.get("role") or "candidate"
        institution = (request.form.get("institution") or "").strip()
        grad_year_raw = request.form.get("graduation_year")

        if not full_name or not email or not password:
            flash("Full name, email, and password are required.", "error")
            return render_template("auth/register.html")

        if role not in ("candidate", "employer"):
            role = "candidate"

        existing = User.query.filter_by(email=email).first()
        if existing:
            flash("An account with that email already exists.", "error")
            return render_template("auth/register.html")

        graduation_year = None
        if grad_year_raw and grad_year_raw.isdigit():
            graduation_year = int(grad_year_raw)

        user = User(
            full_name=full_name,
            email=email,
            role=role,
            institution=institution or ("South African University" if role == "candidate" else "SA Tech Employer"),
            graduation_year=graduation_year if role == "candidate" else None,
        )
        user.set_password(password)
        db.session.add(user)
        db.session.flush()

        if role == "candidate":
            passport = SkillsPassport(
                user_id=user.id,
                readiness_score=20,
                highest_trust_level=1,
                verified_skills_json="[]",
            )
            db.session.add(passport)

        db.session.commit()

        session["user_id"] = user.id
        session["role"] = user.role
        session["full_name"] = user.full_name

        flash("Account created successfully! Welcome to Path2Work.", "success")
        if user.role == "employer":
            return redirect(url_for("employer.dashboard"))
        return redirect(url_for("candidate.dashboard"))

    return render_template("auth/register.html")


@auth_bp.route("/logout")
def logout():
    session.clear()
    flash("You have been signed out.", "info")
    return redirect(url_for("auth.login"))
