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
        if session.get("needs_onboarding"):
            return redirect(url_for("candidate.onboarding"))
        return redirect(url_for("candidate.dashboard"))

    return render_template("auth/register.html")


@auth_bp.route("/logout")
def logout():
    session.clear()
    flash("You have been signed out.", "info")
    return redirect(url_for("auth.login"))

@auth_bp.route("/settings", methods=["GET", "POST"])
@login_required
def settings():
    """Account settings with a real password-change workflow."""
    user = db.get_or_404(User, session["user_id"])
    if request.method == "POST":
        current_password = request.form.get("current_password") or ""
        new_password = request.form.get("new_password") or ""
        confirm_password = request.form.get("confirm_password") or ""

        if not user.check_password(current_password):
            flash("Your current password was not correct. Nothing has been changed.", "error")
        elif len(new_password) < 8:
            flash("Choose a new password with at least 8 characters.", "error")
        elif new_password != confirm_password:
            flash("The new passwords do not match.", "error")
        elif user.check_password(new_password):
            flash("Choose a password different from your current one.", "warning")
        else:
            user.set_password(new_password)
            db.session.commit()
            flash("Your password has been updated.", "success")
            return redirect(url_for("auth.settings"))

    return render_template("auth/settings.html", user=user)
