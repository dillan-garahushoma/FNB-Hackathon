import io
import csv
from datetime import datetime, timezone
from flask import Blueprint, render_template, request, redirect, url_for, flash, session, Response
from app import db
from app.models import User, Pathway, WorkProofSubmission, SkillsPassport, EmployerShortlist, CandidatePreferences
from app.routes.auth import employer_required

employer_bp = Blueprint("employer", __name__, url_prefix="/employer")


@employer_bp.route("/dashboard")
@employer_required
def dashboard():
    employer_id = session["user_id"]

    selected_pathway = request.args.get("pathway", "")
    min_trust = request.args.get("min_trust", "1")
    min_score = request.args.get("min_score", "0")
    search_skill = request.args.get("search_skill", "").strip().lower()
    location_filter = request.args.get("location", "").strip().lower()
    only_open = request.args.get("only_open") == "on"

    try:
        min_trust_int = int(min_trust)
    except ValueError:
        min_trust_int = 1
    try:
        min_score_int = int(min_score)
    except ValueError:
        min_score_int = 0

    all_candidates = User.query.filter_by(role="candidate").order_by(User.created_at.desc()).all()
    pathways = Pathway.query.order_by(Pathway.market_share_pct.desc()).all()
    selected_pathway_id = Pathway.query.filter_by(slug=selected_pathway).with_entities(Pathway.id).scalar() if selected_pathway else None

    total_applicants = len(all_candidates)
    workproof_completed_count = 0
    prequalified_count = 0

    shortlists = EmployerShortlist.query.filter_by(employer_id=employer_id).all()
    shortlist_by_candidate = {s.candidate_id: s for s in shortlists}

    filtered_candidates = []

    for cand in all_candidates:
        passport = cand.passport
        if not passport:
            continue
        preferences = CandidatePreferences.query.filter_by(user_id=cand.id).first()

        best_sub = WorkProofSubmission.query.filter_by(user_id=cand.id).order_by(WorkProofSubmission.evidence_score.desc()).first()

        if best_sub and best_sub.status in ("submitted", "verified"):
            workproof_completed_count += 1
        if passport.highest_trust_level >= 4 and passport.readiness_score >= 70:
            prequalified_count += 1

        # Filtering logic
        if passport.highest_trust_level < min_trust_int:
            continue
        if passport.readiness_score < min_score_int:
            continue
        if only_open and not cand.is_open_to_work:
            continue
        
        if location_filter and (not cand.location or location_filter not in cand.location.lower()):
            continue

        if selected_pathway:
            has_pathway_sub = bool(preferences and preferences.target_pathway_id == selected_pathway_id) or any(
                s.challenge and s.challenge.pathway and s.challenge.pathway.slug == selected_pathway
                for s in cand.submissions
            )
            if not has_pathway_sub:
                continue

        # Skill Search (Checks the JSON extracted skills)
        if search_skill:
            cand_skills = [s.lower() for s in passport.parsed_skills]
            self_described = (preferences.skills_summary or "").lower() if preferences else ""
            if not any(search_skill in s for s in cand_skills) and search_skill not in self_described:
                continue

        filtered_candidates.append({
            "user": cand,
            "passport": passport,
            "best_submission": best_sub,
            "shortlist": shortlist_by_candidate.get(cand.id),
            "preferences": preferences,
        })

    filtered_candidates.sort(key=lambda item: item["passport"].readiness_score, reverse=True)

    return render_template(
        "employer/dashboard.html",
        candidates=filtered_candidates,
        pathways=pathways,
        selected_pathway=selected_pathway,
        min_trust=min_trust_int,
        min_score=min_score_int,
        search_skill=search_skill,
        location_filter=location_filter,
        only_open=only_open,
        total_applicants=total_applicants,
        workproof_completed_count=workproof_completed_count,
        prequalified_count=prequalified_count,
        shortlisted_count=len(shortlists),
    )


@employer_bp.route("/shortlist-board")
@employer_required
def shortlist_board():
    employer_id = session["user_id"]
    shortlists = EmployerShortlist.query.filter_by(employer_id=employer_id).all()
    
    board = {
        "shortlisted": [],
        "invited": [],
        "rejected": []
    }
    
    for s in shortlists:
        cand = s.candidate_user
        if cand and cand.passport:
            target_bucket = s.status if s.status in board else "shortlisted"
            best_sub = WorkProofSubmission.query.filter_by(user_id=cand.id).order_by(WorkProofSubmission.evidence_score.desc()).first()
            board[target_bucket].append({
                "shortlist": s,
                "user": cand,
                "passport": cand.passport,
                "best_submission": best_sub,
            })
            
    return render_template(
        "employer/shortlist_board.html",
        board=board,
        total_shortlisted=len(shortlists)
    )


@employer_bp.route("/export/csv")
@employer_required
def export_csv():
    """Exports candidates to a CSV file."""
    candidates = User.query.filter_by(role="candidate").all()
    
    output = io.StringIO()
    writer = csv.writer(output)
    writer.writerow(["Name", "Email", "Location", "Institution", "Trust Level", "Readiness Score", "Top Skills"])
    
    for c in candidates:
        if c.passport and c.passport.highest_trust_level >= 2:
            skills = ", ".join(c.passport.parsed_skills[:5])
            writer.writerow([
                c.full_name, 
                c.email, 
                c.location or "N/A", 
                c.institution or "N/A", 
                c.passport.highest_trust_level, 
                c.passport.readiness_score, 
                skills
            ])
            
    return Response(
        output.getvalue(),
        mimetype="text/csv",
        headers={"Content-disposition": "attachment; filename=path2work_verified_talent.csv"}
    )


@employer_bp.route("/candidate/<int:user_id>/evidence")
@employer_required
def candidate_evidence(user_id: int):
    employer_id = session["user_id"]
    candidate = db.get_or_404(User, user_id)
    passport = SkillsPassport.query.filter_by(user_id=candidate.id).first()
    submissions = WorkProofSubmission.query.filter_by(user_id=candidate.id).order_by(WorkProofSubmission.evidence_score.desc()).all()
    shortlist = EmployerShortlist.query.filter_by(employer_id=employer_id, candidate_id=candidate.id).first()
    preferences = CandidatePreferences.query.filter_by(user_id=candidate.id).first()

    return render_template(
        "employer/candidate_evidence.html",
        candidate=candidate,
        passport=passport,
        submissions=submissions,
        shortlist=shortlist,
        preferences=preferences,
    )


@employer_bp.route("/shortlist/<int:candidate_id>", methods=["POST"])
@employer_required
def shortlist_candidate(candidate_id: int):
    employer_id = session["user_id"]
    candidate = db.get_or_404(User, candidate_id)

    action = request.form.get("action", "shortlist")
    notes = (request.form.get("notes") or "").strip()
    status = request.form.get("status", "shortlisted")

    shortlist = EmployerShortlist.query.filter_by(employer_id=employer_id, candidate_id=candidate.id).first()

    if not shortlist:
        shortlist = EmployerShortlist(employer_id=employer_id, candidate_id=candidate.id, status=status, notes=notes)
        db.session.add(shortlist)
    else:
        if notes:
            shortlist.notes = notes
        shortlist.status = status

    if action == "verify_level_5":
        passport = SkillsPassport.query.filter_by(user_id=candidate.id).first()
        if passport:
            passport.highest_trust_level = 5
            passport.updated_at = datetime.now(timezone.utc)
        shortlist.status = "invited"
        db.session.commit()
        flash(f"{candidate.full_name} has been verified and endorsed to Trust Level 5!", "success")
    else:
        db.session.commit()
        flash(f"Candidate {candidate.full_name} shortlist status updated to '{status}'.", "success")

    next_url = request.form.get("next_url") or url_for("employer.candidate_evidence", user_id=candidate.id)
    return redirect(next_url)
