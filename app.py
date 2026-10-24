import hmac
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
            g.current_user = get_database().execute(
                "SELECT id, full_name, email FROM users WHERE id = ?", (user_id,)
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
        return redirect(url_for("home"))

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
            "SELECT id, password_hash FROM users WHERE email = ?", (email,)
        ).fetchone()
        if not user or not check_password_hash(user["password_hash"], password):
            flash("Email or password is incorrect. Check your details and try again.", "error")
            return render_template("sign_in.html", email=email), 401

        session.clear()
        session["user_id"] = user["id"]
        flash("You're signed in.", "success")
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
                created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
            );
            """
        )
        connection.commit()
    finally:
        connection.close()


if __name__ == "__main__":
    app = create_app()
    app.run()
