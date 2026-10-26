"""Routes for the AI feedback feature. Attach them to your existing `assessment` blueprint:

    from feedback_routes import register as register_feedback_routes
    register_feedback_routes(
        assessment_bp,
        db=db,
        Submission=Submission,
        get_current_user=get_current_user,   # function returning the signed-in user or None
        login_required=login_required,       # your existing decorator
    )
    app.register_blueprint(assessment_bp)    # call register() BEFORE this line

This adds three endpoints, so templates can use:
    url_for('assessment.feedback', submission_id=...)          page the candidate sees after submitting
    url_for('assessment.feedback_status', submission_id=...)   JSON the page polls
    url_for('assessment.feedback_retry', submission_id=...)    POST to run the review again
"""
from flask import abort, jsonify, redirect, render_template, url_for

import ai_feedback


def register(bp, *, db, Submission, get_current_user, login_required, owner_attr="user_id"):
    ai_feedback.configure(db, Submission)

    def _own_submission(submission_id):
        user = get_current_user()
        sub = db.session.get(Submission, submission_id)
        # 404 rather than 403 so ids of other people's submissions are not revealed.
        if sub is None or user is None or getattr(sub, owner_attr) != user.id:
            abort(404)
        return sub

    @bp.route("/submission/<int:submission_id>/feedback")
    @login_required
    def feedback(submission_id):
        sub = _own_submission(submission_id)
        ai_feedback.expire_if_stale(sub)
        return render_template(
            "assessment/feedback.html",
            submission=sub,
            challenge=sub.challenge,
            feedback=ai_feedback.load_feedback(sub),
        )

    @bp.route("/submission/<int:submission_id>/feedback/status")
    @login_required
    def feedback_status(submission_id):
        sub = _own_submission(submission_id)
        ai_feedback.expire_if_stale(sub)
        resp = jsonify(status=sub.feedback_status or "none", error=sub.feedback_error)
        resp.headers["Cache-Control"] = "no-store"
        return resp

    @bp.post("/submission/<int:submission_id>/feedback/retry")
    @login_required
    def feedback_retry(submission_id):
        sub = _own_submission(submission_id)
        ai_feedback.expire_if_stale(sub)
        ai_feedback.enqueue_feedback(sub.id)  # does nothing if a review is already running
        return redirect(url_for("assessment.feedback", submission_id=sub.id))
