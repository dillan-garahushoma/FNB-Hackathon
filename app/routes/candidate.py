from flask import Blueprint, render_template, request, redirect, url_for, flash, session
from app import db
from app.models import (
    User,
    CandidatePreferences,
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
    if session.get("needs_onboarding"):
        return redirect(url_for("candidate.onboarding"))
    user = db.get_or_404(User, session["user_id"])
    preferences = CandidatePreferences.query.filter_by(user_id=user.id).first()
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
        preferences=preferences,
    )


@candidate_bp.route("/candidate/profile", methods=["GET", "POST"])
@candidate_required
def profile():
    user = db.get_or_404(User, session["user_id"])
    passport = SkillsPassport.query.filter_by(user_id=user.id).first()

    if request.method == "POST":
        if request.form.get("action") == "skip":
            if not preferences:
                preferences = CandidatePreferences(user_id=user.id)
                db.session.add(preferences)
            preferences.onboarding_completed = True
            db.session.commit()
            session.pop("needs_onboarding", None)
            flash("Setup skipped. You can finish your profile and preferences anytime.", "info")
            return redirect(url_for("candidate.dashboard"))

        institution = (request.form.get("institution") or "").strip()
        location = (request.form.get("location") or "").strip()
        grad_year_raw = request.form.get("graduation_year")
        is_open_to_work = request.form.get("is_open_to_work") == "on"
        target_slug = (request.form.get("target_pathway") or "").strip()
        skills_summary = (request.form.get("skills_summary") or "").strip()[:600]
        preferences = CandidatePreferences.query.filter_by(user_id=user.id).first()
        if not preferences:
            preferences = CandidatePreferences(user_id=user.id)
            db.session.add(preferences)

        if institution:
            user.institution = institution
        if location:
            user.location = location
        user.is_open_to_work = is_open_to_work
        preferences.skills_summary = skills_summary
        if target_slug:
            target = Pathway.query.filter_by(slug=target_slug).first()
            if target:
                preferences.target_pathway_id = target.id

        if grad_year_raw and grad_year_raw.isdigit():
            user.graduation_year = int(grad_year_raw)

        db.session.commit()
        flash("Readiness preferences and profile details successfully saved.", "success")
        return redirect(url_for("candidate.profile"))

    return render_template(
        "candidate/profile.html",
        user=user,
        passport=passport,
        pathways=Pathway.query.order_by(Pathway.market_share_pct.desc()).all(),
        preferences=CandidatePreferences.query.filter_by(user_id=user.id).first(),
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

@candidate_bp.route("/candidate/onboarding", methods=["GET", "POST"])
@candidate_required
def onboarding():
    """Short, skippable first-run setup for new candidates."""
    user = db.get_or_404(User, session["user_id"])
    preferences = CandidatePreferences.query.filter_by(user_id=user.id).first()
    if preferences and preferences.onboarding_completed:
        session.pop("needs_onboarding", None)
        return redirect(url_for("candidate.dashboard"))

    pathways = Pathway.query.order_by(Pathway.market_share_pct.desc()).all()
    if request.method == "POST":
        institution = (request.form.get("institution") or "").strip()
        location = (request.form.get("location") or "").strip()
        grad_year_raw = (request.form.get("graduation_year") or "").strip()
        target_slug = (request.form.get("target_pathway") or "").strip()
        skills_summary = (request.form.get("skills_summary") or "").strip()[:600]

        if institution:
            user.institution = institution[:150]
        if location:
            user.location = location[:100]
        if grad_year_raw.isdigit() and 2020 <= int(grad_year_raw) <= 2035:
            user.graduation_year = int(grad_year_raw)
        user.is_open_to_work = request.form.get("is_open_to_work") == "on"

        if not preferences:
            preferences = CandidatePreferences(user_id=user.id)
            db.session.add(preferences)
        if target_slug:
            target = Pathway.query.filter_by(slug=target_slug).first()
            if target:
                preferences.target_pathway_id = target.id
        preferences.skills_summary = skills_summary
        preferences.onboarding_completed = True
        db.session.commit()
        session.pop("needs_onboarding", None)
        flash("Your starting point is saved. You can update these preferences anytime.", "success")
        return redirect(url_for("candidate.dashboard"))

    return render_template("candidate/onboarding.html", user=user, pathways=pathways, preferences=preferences)
