import hmac
import json
import os
import re
import secrets
import sqlite3
from datetime import datetime, timedelta, timezone

from flask import (
    Flask,
    flash,
    g,
    redirect,
    render_template,
    request,
    session,
    url_for,
)
from werkzeug.security import check_password_hash, generate_password_hash


EMAIL_PATTERN = re.compile(r"^[^@\s]+@[^@\s]+\.[^@\s]+$")
MIN_PASSWORD_LENGTH = 8
MAX_PASSWORD_LENGTH = 256


def create_app(test_config=None):
    app = Flask(__name__, instance_relative_config=True)
    configured_secret = os.environ.get("PATH2WORK_SECRET_KEY")
    app.config.from_mapping(
        SECRET_KEY=configured_secret or secrets.token_hex(32),
        DATABASE=os.path.join(app.instance_path, "path2work.sqlite3"),
        SESSION_COOKIE_HTTPONLY=True,
        SESSION_COOKIE_SAMESITE="Lax",
        SESSION_COOKIE_SECURE=os.environ.get("PATH2WORK_COOKIE_SECURE") == "1",
        PERMANENT_SESSION_LIFETIME=timedelta(days=7),
    )
    if test_config:
        app.config.update(test_config)

    if not configured_secret and not app.config.get("TESTING"):
        app.logger.warning(
            "PATH2WORK_SECRET_KEY is not set; sessions will be invalidated on restart."
        )

    os.makedirs(app.instance_path, exist_ok=True)
    database_path = app.config["DATABASE"]
    if database_path != ":memory:":
        os.makedirs(os.path.dirname(os.path.abspath(database_path)), exist_ok=True)
    initialize_database(app)

    @app.teardown_appcontext
    def close_database(_error=None):
        connection = g.pop("database", None)
        if connection is not None:
            connection.close()

    @app.before_request
    def load_current_user():
        user_id = session.get("user_id")
        g.current_user = None
        if user_id is not None:
            database = get_database()
            columns = database.execute("PRAGMA table_info(users)").fetchall()
            available_columns = {row[1] for row in columns}
            select_columns = ["id", "full_name", "email"]
            if "onboarding_completed" in available_columns:
                select_columns.append("onboarding_completed")
            g.current_user = database.execute(
                f"SELECT {', '.join(select_columns)} FROM users WHERE id = ?",
                (user_id,),
            ).fetchone()
            if g.current_user is None:
                session.pop("user_id", None)

    @app.context_processor
    def inject_template_helpers():
        def csrf_token():
            token = session.get("_csrf_token")
            if token is None:
                token = secrets.token_urlsafe(32)
                session["_csrf_token"] = token
            return token

        return {
            "csrf_token": csrf_token,
            "current_user": g.get("current_user"),
            "current_year": datetime.now(timezone.utc).year,
        }

    @app.cli.command("init-db")
    def init_db_command():
        initialize_database(app)
        print("Initialized the Path2Work database.")

    @app.get("/")
    def home():
        return render_template("index.html", active_page="home")

    @app.get("/opportunities")
    def opportunities():
        return render_template("opportunities.html", active_page="opportunities")

    @app.route("/onboarding", methods=["GET", "POST"])
    @app.route("/onboarding/<int:step>", methods=["GET", "POST"])
    def onboarding(step=None):
        if not g.get("current_user"):
            return redirect(url_for("sign_in"))

        profile = get_onboarding_profile(g.current_user["id"])
        current_step = step if step is not None else next_onboarding_step(profile)
        if current_step < 1 or current_step > 4:
            return redirect(url_for("onboarding", step=1))
        if g.current_user["onboarding_completed"]:
            return redirect(url_for("home"))

        if current_step > 1 and not profile.get("career_goal"):
            return redirect(url_for("onboarding", step=1))
        if current_step > 2 and (
            not profile.get("career_fields") or not profile.get("preferred_roles")
        ):
            return redirect(url_for("onboarding", step=2))
        if current_step > 3 and not all(
            profile.get(key)
            for key in (
                "preferred_locations",
                "work_arrangement",
                "availability",
                "opportunity_types",
            )
        ):
            return redirect(url_for("onboarding", step=3))

        if request.method == "POST":
            return save_onboarding_step(current_step)

        return render_onboarding_step(current_step)

    @app.post("/onboarding/complete")
    def complete_onboarding():
        if not g.get("current_user"):
            flash("Please sign in to continue.", "error")
            return redirect(url_for("sign_in"))

        if not valid_csrf_token():
            flash("Your session expired. Please try again.", "error")
            return redirect(url_for("onboarding", step=4))

        user = g.current_user
        profile = get_onboarding_profile(user["id"])
        errors = validate_onboarding_submission(profile)
        if errors:
            return render_onboarding_step(4, errors=errors), 400

        database = get_database()
        try:
            database.execute(
                "UPDATE users SET onboarding_completed = 1 WHERE id = ? AND onboarding_completed = 0",
                (user["id"],),
            )
            database.commit()
        except sqlite3.Error:
            flash("We couldn't finish onboarding right now. Please try again.", "error")
            return redirect(url_for("onboarding", step=4))

        flash("You're all set. Your onboarding is complete.", "success")
        return redirect(url_for("home"))

    @app.route("/register", methods=["GET", "POST"])
    def register():
        if request.method == "GET":
            return render_template("register.html", errors={}, form_data={})

        if not valid_csrf_token():
            flash("Your session expired. Please try again.", "error")
            return render_template("register.html", errors={}, form_data={}), 400

        full_name = request.form.get("full_name", "").strip()
        email = request.form.get("email", "").strip().lower()
        password = request.form.get("password", "")
        errors = {}

        if not full_name:
            errors["full_name"] = "Enter your full name."
        elif len(full_name) > 120:
            errors["full_name"] = "Your name must be 120 characters or fewer."

        if not email:
            errors["email"] = "Enter your email address."
        elif len(email) > 254 or not EMAIL_PATTERN.fullmatch(email):
            errors["email"] = "Enter a valid email address."

        if len(password) < MIN_PASSWORD_LENGTH:
            errors["password"] = (
                f"Use at least {MIN_PASSWORD_LENGTH} characters for your password."
            )
        elif len(password) > MAX_PASSWORD_LENGTH:
            errors["password"] = (
                f"Your password must be {MAX_PASSWORD_LENGTH} characters or fewer."
            )

        if errors:
            return (
                render_template(
                    "register.html",
                    errors=errors,
                    form_data={"full_name": full_name, "email": email},
                ),
                400,
            )

        database = get_database()
        existing_user = database.execute(
            "SELECT id FROM users WHERE email = ?", (email,)
        ).fetchone()
        if existing_user:
            return (
                render_template(
                    "register.html",
                    errors={"email": "An account with this email already exists."},
                    form_data={"full_name": full_name, "email": email},
                ),
                409,
            )

        try:
            cursor = database.execute(
                "INSERT INTO users (full_name, email, password_hash) VALUES (?, ?, ?)",
                (full_name, email, generate_password_hash(password)),
            )
            database.commit()
        except sqlite3.IntegrityError:
            existing_user = database.execute(
                "SELECT id FROM users WHERE email = ?", (email,)
            ).fetchone()
            if existing_user:
                return (
                    render_template(
                        "register.html",
                        errors={"email": "An account with this email already exists."},
                        form_data={"full_name": full_name, "email": email},
                    ),
                    409,
                )
            raise

        session.clear()
        session["user_id"] = cursor.lastrowid
        flash("Your account is ready. Welcome to Path2Work.", "success")
        return redirect(url_for("onboarding", step=1))

    @app.route("/signin", methods=["GET", "POST"])
    def sign_in():
        if request.method == "GET":
            return render_template("sign_in.html")

        if not valid_csrf_token():
            flash("Your session expired. Please try again.", "error")
            return render_template("sign_in.html"), 400

        email = request.form.get("email", "").strip().lower()
        password = request.form.get("password", "")
        user = get_database().execute(
            "SELECT id, password_hash, onboarding_completed FROM users WHERE email = ?",
            (email,),
        ).fetchone()
        if not user or not check_password_hash(user["password_hash"], password):
            flash("Email or password is incorrect. Check your details and try again.", "error")
            return render_template("sign_in.html", email=email), 401

        session.clear()
        session["user_id"] = user["id"]
        flash("You're signed in.", "success")
        if not user["onboarding_completed"]:
            profile = get_onboarding_profile(user["id"])
            return redirect(url_for("onboarding", step=next_onboarding_step(profile)))
        return redirect(url_for("home"))

    @app.post("/signout")
    def sign_out():
        if not valid_csrf_token():
            flash("Your session expired. Please try again.", "error")
            return redirect(url_for("home"))
        session.clear()
        flash("You're signed out.", "success")
        return redirect(url_for("home"))

    return app


def get_database():
    if "database" not in g:
        connection = sqlite3.connect(current_app_config_database())
        connection.row_factory = sqlite3.Row
        connection.execute("PRAGMA foreign_keys = ON")
        g.database = connection
    return g.database


def current_app_config_database():
    from flask import current_app

    return current_app.config["DATABASE"]


def valid_csrf_token():
    expected = session.get("_csrf_token")
    submitted = request.form.get("csrf_token", "")
    return bool(expected and submitted and hmac.compare_digest(expected, submitted))


def initialize_database(app):
    connection = sqlite3.connect(app.config["DATABASE"])
    try:
        connection.executescript(
            """
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                full_name TEXT NOT NULL,
                email TEXT NOT NULL UNIQUE COLLATE NOCASE,
                password_hash TEXT NOT NULL,
                career_goal TEXT,
                career_fields TEXT,
                preferred_roles TEXT,
                preferred_locations TEXT,
                work_arrangement TEXT,
                availability TEXT,
                opportunity_types TEXT,
                onboarding_completed INTEGER NOT NULL DEFAULT 0,
                created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
            );
            """
        )
        ensure_user_columns(connection)
        connection.commit()
    finally:
        connection.close()


def ensure_user_columns(connection):
    columns = connection.execute("PRAGMA table_info(users)").fetchall()
    existing = {row[1] for row in columns}
    additions = [
        ("career_goal", "TEXT"),
        ("career_fields", "TEXT"),
        ("preferred_roles", "TEXT"),
        ("preferred_role_other", "TEXT"),
        ("preferred_locations", "TEXT"),
        ("work_arrangement", "TEXT"),
        ("availability", "TEXT"),
        ("opportunity_types", "TEXT"),
        ("onboarding_completed", "INTEGER NOT NULL DEFAULT 0"),
    ]
    for column_name, definition in additions:
        if column_name not in existing:
            connection.execute(f"ALTER TABLE users ADD COLUMN {column_name} {definition}")


CAREER_GOALS = {
    "FIRST_JOB": "Find my first job",
    "INTERNSHIP_LEARNERSHIP": "Get an internship or learnership",
    "WORK_EXPERIENCE": "Gain work experience",
    "BUILD_SKILLS": "Build my skills",
    "EXPLORE_CAREERS": "Explore my career options",
}
CAREER_FIELDS = (
    "Information Technology",
    "Business & Management",
    "Healthcare",
    "Education",
    "Engineering",
    "Finance & Accounting",
    "Marketing & Communications",
    "Design & Creative",
    "Agriculture & Environment",
    "Other",
)
PREFERRED_ROLES = (
    "Software Developer",
    "IT Support",
    "Data Analyst",
    "Network Engineer",
    "Web Designer",
    "Project Coordinator",
    "Other",
)
PREFERRED_LOCATIONS = (
    "Johannesburg",
    "Cape Town",
    "Durban",
    "Pretoria",
    "Gqeberha",
    "Bloemfontein",
    "Polokwane",
    "Rustenburg",
    "Nelspruit",
    "Kimberley",
)
WORK_ARRANGEMENTS = ("On-site", "Remote", "Hybrid", "No preference")
AVAILABILITY_OPTIONS = (
    "Immediately",
    "Within 2 weeks",
    "Within a month",
    "Within 3 months",
    "Flexible / not sure yet",
)
OPPORTUNITY_TYPES = (
    "Jobs",
    "Internships",
    "Learnerships",
    "Training programmes",
    "Mentorship",
)


def save_onboarding_step(step):
    user = g.get("current_user")
    if not user:
        flash("Please sign in to continue.", "error")
        return redirect(url_for("sign_in"))

    if not valid_csrf_token():
        flash("Your session expired. Please try again.", "error")
        return redirect(url_for("onboarding", step=step))

    database = get_database()
    if step == 1:
        goal = request.form.get("career_goal", "").strip()
        if goal not in CAREER_GOALS:
            return render_onboarding_step(
                step,
                errors={"career_goal": "Choose one career goal to continue."},
            ), 400
        database.execute(
            "UPDATE users SET career_goal = ? WHERE id = ?",
            (goal, user["id"]),
        )
        database.commit()
        return redirect(url_for("onboarding", step=2))

    if step == 2:
        submitted_fields = request.form.getlist("career_fields")
        submitted_roles = request.form.getlist("preferred_roles")
        career_fields = normalize_multiselect(submitted_fields)
        roles = normalize_multiselect(submitted_roles)
        other_role = request.form.get("other_role", "").strip()
        errors = {}
        if any(value not in CAREER_FIELDS for value in career_fields):
            errors["career_fields"] = "Choose from the listed career fields."
        elif not career_fields:
            errors["career_fields"] = "Choose at least one career field."
        if any(value not in PREFERRED_ROLES for value in roles):
            errors["preferred_roles"] = "Choose from the listed roles."
        elif not roles:
            errors["preferred_roles"] = "Choose at least one role."
        elif len(roles) > 3:
            errors["preferred_roles"] = "Choose no more than three roles."
        if "Other" in roles and not other_role:
            errors["other_role"] = "Describe the role you have in mind."
        elif len(other_role) > 80:
            errors["other_role"] = "Keep the role description to 80 characters or fewer."
        if errors:
            return render_onboarding_step(
                step,
                errors=errors,
                submitted_fields=career_fields,
                submitted_roles=roles,
                other_role=other_role,
            ), 400
        database.execute(
            "UPDATE users SET career_fields = ?, preferred_roles = ?, preferred_role_other = ? WHERE id = ?",
            (
                json.dumps(career_fields, ensure_ascii=False),
                json.dumps(roles, ensure_ascii=False),
                other_role if "Other" in roles else None,
                user["id"],
            ),
        )
        database.commit()
        return redirect(url_for("onboarding", step=3))

    if step == 3:
        submitted_locations = request.form.getlist("preferred_locations")
        preferred_locations = normalize_multiselect(submitted_locations)
        work_arrangement = request.form.get("work_arrangement", "").strip()
        availability = request.form.get("availability", "").strip()
        opportunity_types = normalize_multiselect(request.form.getlist("opportunity_types"))
        errors = {}
        if any(value not in PREFERRED_LOCATIONS for value in preferred_locations):
            errors["preferred_locations"] = "Choose a supported location from the list."
        elif not preferred_locations:
            errors["preferred_locations"] = "Add at least one preferred location."
        if work_arrangement not in WORK_ARRANGEMENTS:
            errors["work_arrangement"] = "Choose a work arrangement."
        if availability not in AVAILABILITY_OPTIONS:
            errors["availability"] = "Choose when you are available."
        if any(value not in OPPORTUNITY_TYPES for value in opportunity_types):
            errors["opportunity_types"] = "Choose from the listed opportunity types."
        elif not opportunity_types:
            errors["opportunity_types"] = "Choose at least one opportunity type."
        if errors:
            return render_onboarding_step(
                step,
                errors=errors,
                submitted_locations=[
                    value for value in preferred_locations
                    if value in PREFERRED_LOCATIONS
                ],
                submitted_work_arrangement=work_arrangement,
                submitted_availability=availability,
                submitted_opportunity_types=[
                    value for value in opportunity_types
                    if value in OPPORTUNITY_TYPES
                ],
            ), 400
        database.execute(
            "UPDATE users SET preferred_locations = ?, work_arrangement = ?, availability = ?, opportunity_types = ? WHERE id = ?",
            (json.dumps(preferred_locations, ensure_ascii=False), work_arrangement, availability, json.dumps(opportunity_types, ensure_ascii=False), user["id"]),
        )
        database.commit()
        return redirect(url_for("onboarding", step=4))

    flash("Invalid onboarding step.", "error")
    return redirect(url_for("onboarding", step=1))


def normalize_multiselect(values, allowed_values=None):
    items = []
    seen = set()
    for value in values:
        cleaned = value.strip() if isinstance(value, str) else ""
        if not cleaned:
            continue
        if allowed_values is not None and cleaned not in allowed_values:
            continue
        if cleaned not in seen:
            seen.add(cleaned)
            items.append(cleaned)
    return items


def get_onboarding_profile(user_id):
    user = get_database().execute(
        "SELECT full_name, email, career_goal, career_fields, preferred_roles, preferred_role_other, preferred_locations, work_arrangement, availability, opportunity_types, onboarding_completed FROM users WHERE id = ?",
        (user_id,),
    ).fetchone()
    if user is None:
        return {}
    profile = dict(user)
    profile["career_fields"] = json.loads(profile["career_fields"]) if profile["career_fields"] else []
    profile["preferred_roles"] = json.loads(profile["preferred_roles"]) if profile["preferred_roles"] else []
    profile["preferred_locations"] = json.loads(profile["preferred_locations"]) if profile["preferred_locations"] else []
    profile["opportunity_types"] = json.loads(profile["opportunity_types"]) if profile["opportunity_types"] else []
    return profile


def validate_onboarding_submission(profile):
    errors = {}
    if not profile.get("career_goal"):
        errors["career_goal"] = "Choose a goal."
    if not profile.get("career_fields"):
        errors["career_fields"] = "Select at least one field."
    if not profile.get("preferred_roles"):
        errors["preferred_roles"] = "Select at least one role."
    if not profile.get("preferred_locations"):
        errors["preferred_locations"] = "Add at least one location."
    if not profile.get("work_arrangement"):
        errors["work_arrangement"] = "Choose a work arrangement."
    if not profile.get("availability"):
        errors["availability"] = "Choose your availability."
    if not profile.get("opportunity_types"):
        errors["opportunity_types"] = "Select at least one opportunity type."
    return errors


def next_onboarding_step(profile):
    if not profile.get("career_goal"):
        return 1
    if not profile.get("career_fields") or not profile.get("preferred_roles"):
        return 2
    if not all(
        profile.get(key)
        for key in (
            "preferred_locations",
            "work_arrangement",
            "availability",
            "opportunity_types",
        )
    ):
        return 3
    return 4


def render_onboarding_step(
    step,
    errors=None,
    submitted_fields=None,
    submitted_roles=None,
    other_role=None,
    submitted_locations=None,
    submitted_work_arrangement=None,
    submitted_availability=None,
    submitted_opportunity_types=None,
):
    user = g.current_user
    profile = get_onboarding_profile(user["id"])
    step_names = ["Career goal", "Interests & roles", "Location & preferences", "Review"]
    selected_goal = profile.get("career_goal")
    selected_fields = submitted_fields if submitted_fields is not None else profile.get("career_fields", [])
    selected_roles = submitted_roles if submitted_roles is not None else profile.get("preferred_roles", [])
    selected_locations = submitted_locations if submitted_locations is not None else profile.get("preferred_locations", [])
    work_arrangement = submitted_work_arrangement if submitted_work_arrangement is not None else profile.get("work_arrangement")
    availability = submitted_availability if submitted_availability is not None else profile.get("availability")
    opportunity_types = submitted_opportunity_types if submitted_opportunity_types is not None else profile.get("opportunity_types", [])

    goal_options = [
        ("FIRST_JOB", "Find my first job", "Explore entry-level roles and opportunities made for your first step."),
        ("INTERNSHIP_LEARNERSHIP", "Get an internship or learnership", "Build experience while learning on the job."),
        ("WORK_EXPERIENCE", "Gain work experience", "Add practical experience through part-time or volunteer work."),
        ("BUILD_SKILLS", "Build my skills", "Develop in-demand skills for the work you want."),
        ("EXPLORE_CAREERS", "Explore my career options", "Discover career paths that could suit you."),
    ]

    return render_template(
        "onboarding.html",
        step=step,
        current_step=step,
        active_page="profile",
        step_names=step_names,
        profile=profile,
        errors=errors or {},
        selected_goal=selected_goal,
        other_role=other_role if other_role is not None else profile.get("preferred_role_other", ""),
        selected_fields=selected_fields,
        selected_roles=selected_roles,
        selected_locations=selected_locations,
        work_arrangement=work_arrangement,
        availability=availability,
        opportunity_types=opportunity_types,
        goal_options=goal_options,
        goal_labels={value: title for value, title, _ in goal_options},
        field_options=CAREER_FIELDS,
        role_options=PREFERRED_ROLES,
        location_options=PREFERRED_LOCATIONS,
        work_arrangement_options=WORK_ARRANGEMENTS,
        availability_options=AVAILABILITY_OPTIONS,
        opportunity_options=OPPORTUNITY_TYPES,
    )


if __name__ == "__main__":
    app = create_app()
    app.run()
