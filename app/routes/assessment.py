from datetime import datetime, timezone
from flask import Blueprint, request, redirect, url_for, flash, session
from app import db
from app.models import (
    User,
    WorkProofChallenge,
    WorkProofSubmission,
    SkillsPassport,
)
from app.routes.auth import candidate_required, login_required

# Imports from the root folder
import ai_feedback
from feedback_routes import register as register_feedback_routes

assessment_bp = Blueprint("assessment", __name__, url_prefix="/assessment")


@assessment_bp.route("/start/<int:challenge_id>", methods=["GET", "POST"])
@candidate_required
def start_or_resume(challenge_id: int):
    challenge = db.get_or_404(WorkProofChallenge, challenge_id)
    user_id = session["user_id"]

    submission = WorkProofSubmission.query.filter_by(
        user_id=user_id, challenge_id=challenge.id
    ).first()

    if not submission:
        submission = WorkProofSubmission(
            user_id=user_id,
            challenge_id=challenge.id,
            status="in_progress",
            evidence_score=0,
            next_best_action=f"Complete the Build, Explain, and Adapt phases for '{challenge.title}'.",
        )
        db.session.add(submission)
        db.session.commit()

    return redirect(url_for("candidate.workproof_stepper", challenge_id=challenge.id))


@assessment_bp.route("/submit/<int:challenge_id>", methods=["POST"])
@candidate_required
def submit_workproof(challenge_id: int):
    challenge = db.get_or_404(WorkProofChallenge, challenge_id)
    user = db.get_or_404(User, session["user_id"])

    submission = WorkProofSubmission.query.filter_by(
        user_id=user.id, challenge_id=challenge.id
    ).first()

    if not submission:
        submission = WorkProofSubmission(user_id=user.id, challenge_id=challenge.id)
        db.session.add(submission)

    submission.build_repo_url = (request.form.get("build_repo_url") or "").strip()
    submission.build_code_snippet = (request.form.get("build_code_snippet") or "").strip()
    submission.explain_notes = (request.form.get("explain_notes") or "").strip()
    submission.adapt_solution = (request.form.get("adapt_solution") or "").strip()

    action = request.form.get("action", "submit")

    if action == "save_draft":
        if submission.status != "verified":
            submission.status = "in_progress"
        db.session.commit()
        flash("Draft progress saved. You can resume anytime.", "info")
        return redirect(url_for("candidate.workproof_stepper", challenge_id=challenge.id))

    # 1. Save the submission to the database so it gets an ID
    db.session.commit()

    # 2. Trigger the AI Review in the background thread
    ai_feedback.enqueue_feedback(submission.id)

    flash("Submission received! The AI is reviewing your code and explanation now.", "info")
    
    # 3. Redirect to the AI feedback page
    return redirect(url_for("assessment.feedback", submission_id=submission.id))


# -------------------------------------------------------------------------
# Hook up the AI Feedback Routes to this Blueprint
# -------------------------------------------------------------------------
def get_current_user():
    if "user_id" in session:
        return db.session.get(User, session["user_id"])
    return None

register_feedback_routes(
    assessment_bp,
    db=db,
    Submission=WorkProofSubmission,
    get_current_user=get_current_user,
    login_required=login_required
)