import json
from datetime import datetime, timezone
from werkzeug.security import generate_password_hash, check_password_hash
from app import db


def utc_now():
    return datetime.now(timezone.utc)


class User(db.Model):
    __tablename__ = "users"

    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(120), unique=True, nullable=False, index=True)
    password_hash = db.Column(db.String(256), nullable=False)
    full_name = db.Column(db.String(120), nullable=False)
    role = db.Column(db.String(20), nullable=False, default="candidate")
    institution = db.Column(db.String(150), nullable=True)
    graduation_year = db.Column(db.Integer, nullable=True)
    created_at = db.Column(db.DateTime, default=utc_now)

    # Candidate discovery preferences
    location = db.Column(db.String(100), nullable=True, default="South Africa")
    is_open_to_work = db.Column(db.Boolean, default=True)

    submissions = db.relationship(
        "WorkProofSubmission", backref="candidate", lazy=True, cascade="all, delete-orphan"
    )
    passport = db.relationship(
        "SkillsPassport", backref="candidate", uselist=False, lazy=True, cascade="all, delete-orphan"
    )

    def set_password(self, password: str) -> None:
        self.password_hash = generate_password_hash(password)

    def check_password(self, password: str) -> bool:
        return check_password_hash(self.password_hash, password)

    @property
    def has_institutional_email(self) -> bool:
        email_lower = (self.email or "").lower()
        return email_lower.endswith(".ac.za") or email_lower.endswith(".edu.za")


class Pathway(db.Model):
    __tablename__ = "pathways"

    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(120), nullable=False)
    slug = db.Column(db.String(80), unique=True, nullable=False)
    description = db.Column(db.Text, nullable=False)
    market_share_pct = db.Column(db.Integer, nullable=False)

    challenges = db.relationship(
        "WorkProofChallenge", backref="pathway", lazy=True, cascade="all, delete-orphan"
    )


class WorkProofChallenge(db.Model):
    __tablename__ = "workproof_challenges"

    id = db.Column(db.Integer, primary_key=True)
    pathway_id = db.Column(db.Integer, db.ForeignKey("pathways.id"), nullable=False)
    title = db.Column(db.String(150), nullable=False)
    scenario = db.Column(db.Text, nullable=False)
    build_prompt = db.Column(db.Text, nullable=False)
    explain_prompt = db.Column(db.Text, nullable=False)
    adapt_prompt = db.Column(db.Text, nullable=False)
    passing_score = db.Column(db.Integer, nullable=False, default=70)

    submissions = db.relationship(
        "WorkProofSubmission", backref="challenge", lazy=True, cascade="all, delete-orphan"
    )


class WorkProofSubmission(db.Model):
    __tablename__ = "workproof_submissions"

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)
    challenge_id = db.Column(db.Integer, db.ForeignKey("workproof_challenges.id"), nullable=False)
    build_repo_url = db.Column(db.String(255), nullable=True)
    build_code_snippet = db.Column(db.Text, nullable=True)
    explain_notes = db.Column(db.Text, nullable=True)
    adapt_solution = db.Column(db.Text, nullable=True)
    status = db.Column(db.String(20), nullable=False, default="in_progress")
    evidence_score = db.Column(db.Integer, nullable=False, default=0)
    readiness_feedback = db.Column(db.Text, nullable=True)
    next_best_action = db.Column(db.Text, nullable=True)
    completed_at = db.Column(db.DateTime, nullable=True)

    feedback_status = db.Column(db.String(16), nullable=True)
    feedback_json = db.Column(db.Text, nullable=True)
    feedback_error = db.Column(db.String(64), nullable=True)
    feedback_started_at = db.Column(db.DateTime, nullable=True)
    feedback_finished_at = db.Column(db.DateTime, nullable=True)
    feedback_model = db.Column(db.String(64), nullable=True)


class SkillsPassport(db.Model):
    __tablename__ = "skills_passports"

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), unique=True, nullable=False)
    readiness_score = db.Column(db.Integer, nullable=False, default=15)
    highest_trust_level = db.Column(db.Integer, nullable=False, default=1)
    verified_skills_json = db.Column(db.Text, nullable=False, default="[]")
    updated_at = db.Column(db.DateTime, default=utc_now, onupdate=utc_now)

    @property
    def verified_skills(self):
        try:
            return json.loads(self.verified_skills_json or "[]")
        except (ValueError, TypeError):
            return []

    @property
    def parsed_skills(self):
        """Extracts a flat list of all skills for employer filtering."""
        skills = []
        for record in self.verified_skills:
            skills.extend(record.get("skills", []))
        return list(set(skills))

    @property
    def trust_level_label(self) -> str:
        labels = {
            1: "Level 1: Self-Declared",
            2: "Level 2: Evidence Attached",
            3: "Level 3: Source Verified",
            4: "Level 4: Path2Work Assessed",
            5: "Level 5: Employer Verified",
        }
        return labels.get(self.highest_trust_level, "Level 1: Self-Declared")


class EmployerShortlist(db.Model):
    __tablename__ = "employer_shortlists"

    id = db.Column(db.Integer, primary_key=True)
    employer_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)
    candidate_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)
    notes = db.Column(db.Text, nullable=True)
    status = db.Column(db.String(20), nullable=False, default="shortlisted")
    created_at = db.Column(db.DateTime, default=utc_now)

    employer = db.relationship("User", foreign_keys=[employer_id], backref="shortlists_created")
    candidate_user = db.relationship("User", foreign_keys=[candidate_id], backref="shortlisted_by")


class CandidatePreferences(db.Model):
    """Persisted candidate discovery preferences; safe to add to existing databases."""

    __tablename__ = "candidate_preferences"

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), unique=True, nullable=False, index=True)
    target_pathway_id = db.Column(db.Integer, db.ForeignKey("pathways.id"), nullable=True)
    skills_summary = db.Column(db.Text, nullable=True)
    onboarding_completed = db.Column(db.Boolean, nullable=False, default=False)
    created_at = db.Column(db.DateTime, default=utc_now)
    updated_at = db.Column(db.DateTime, default=utc_now, onupdate=utc_now)

    target_pathway = db.relationship("Pathway", lazy="joined")
