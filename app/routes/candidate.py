from flask import Blueprint, render_template, request, redirect, url_for, flash, session
from app import db
from app.models import (
    User,
    Pathway,
    WorkProofChallenge,
    WorkProofSubmission,
    SkillsPassport,
)
from app.routes.auth import candidate_required

candidate_bp = Blueprint("candidate", __name__)


@candidate_bp.route("/candidate/dashboard")
@candidate_required
def dashboard():
    user = db.get_or_404(User, session["user_id"])
    passport = SkillsPassport.query.filter_by(user_id=user.id).first()
    if not passport:
        passport = SkillsPassport(
            user_id=user.id, readiness_score=20, highest_trust_level=1, verified_skills_json="[]"
        )
        db.session.add(passport)
        db.session.commit()

    pathways = Pathway.query.order_by(Pathway.market_share_pct.desc()).all()
    submissions = WorkProofSubmission.query.filter_by(user_id=user.id).all()
    submissions_by_challenge = {sub.challenge_id: sub for sub in submissions}

    latest_submission = (
        WorkProofSubmission.query.filter_by(user_id=user.id)
        .order_by(WorkProofSubmission.completed_at.desc().nullslast(), WorkProofSubmission.id.desc())
        .first()
    )

    return render_template(
        "candidate/dashboard.html",
        user=user,
        passport=passport,
        pathways=pathways,
        submissions_by_challenge=submissions_by_challenge,
        latest_submission=latest_submission,
    )


@candidate_bp.route("/candidate/profile", methods=["GET", "POST"])
@candidate_required
def profile():
    user = db.get_or_404(User, session["user_id"])
    passport = SkillsPassport.query.filter_by(user_id=user.id).first()

    if request.method == "POST":
        institution = (request.form.get("institution") or "").strip()
        location = (request.form.get("location") or "").strip()
        grad_year_raw = request.form.get("graduation_year")
        is_open_to_work = request.form.get("is_open_to_work") == "on"

        if institution:
            user.institution = institution
        if location:
            user.location = location
        user.is_open_to_work = is_open_to_work

        if grad_year_raw and grad_year_raw.isdigit():
            user.graduation_year = int(grad_year_raw)

        db.session.commit()
        flash("Readiness preferences and profile details successfully saved.", "success")
        return redirect(url_for("candidate.profile"))

    return render_template(
        "candidate/profile.html",
        user=user,
        passport=passport,
    )


@candidate_bp.route("/candidate/workproof/<int:challenge_id>")
@candidate_required
def workproof_stepper(challenge_id: int):
    user = db.get_or_404(User, session["user_id"])
    challenge = db.get_or_404(WorkProofChallenge, challenge_id)
    submission = WorkProofSubmission.query.filter_by(
        user_id=user.id, challenge_id=challenge.id
    ).first()

    return render_template(
        "candidate/workproof_stepper.html",
        user=user,
        challenge=challenge,
        submission=submission,
    )


@candidate_bp.route("/passport/<int:user_id>")
def skills_passport(user_id: int):
    candidate = db.get_or_404(User, user_id)
    passport = SkillsPassport.query.filter_by(user_id=candidate.id).first()
    if not passport:
        passport = SkillsPassport(
            user_id=candidate.id,
            readiness_score=20,
            highest_trust_level=1,
            verified_skills_json="[]",
        )
        db.session.add(passport)
        db.session.commit()

    submissions = (
        WorkProofSubmission.query.filter_by(user_id=candidate.id)
        .order_by(WorkProofSubmission.evidence_score.desc())
        .all()
    )

    trust_tiers = [
        {
            "level": 1,
            "name": "Self-Declared",
            "desc": "Candidate registered profile and declared target IT career pathway.",
        },
        {
            "level": 2,
            "name": "Evidence Attached",
            "desc": "GitHub repository, diagnostic script, or project artifact attached.",
        },
        {
            "level": 3,
            "name": "Source Verified",
            "desc": "Institutional (.ac.za) identity & repository structure validated.",
        },
        {
            "level": 4,
            "name": "Path2Work Assessed",
            "desc": "Controlled 3-stage 'Build → Explain → Adapt' WorkProof passed (>= 70%).",
        },
        {
            "level": 5,
            "name": "Employer Verified",
            "desc": "Technical evidence inspected and endorsed by a hiring partner.",
        },
    ]

    return render_template(
        "candidate/skills_passport.html",
        candidate=candidate,
        passport=passport,
        submissions=submissions,
        trust_tiers=trust_tiers,
    )
