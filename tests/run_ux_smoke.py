"""Smoke-test the real Flask app's primary user journeys with temporary SQLite data.

This covers routing and server-rendered templates. It is not a replacement for browser/E2E checks.
Run with: python tests/run_ux_smoke.py
"""
import json
import os
import sys
import tempfile

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)

from config import Config
from app import create_app, db


def get_ok(client, path, follow_redirects=False):
    response = client.get(path, follow_redirects=follow_redirects)
    assert response.status_code == 200, f"GET {path}: expected 200, got {response.status_code}"
    print(f"PASS GET {path} -> 200")
    return response


def main():
    with tempfile.TemporaryDirectory() as folder:
        database_path = os.path.join(folder, "path2work-smoke.sqlite")

        class SmokeConfig(Config):
            SECRET_KEY = "path2work-smoke-test"
            TESTING = True
            SQLALCHEMY_DATABASE_URI = "sqlite:///" + database_path

        app = create_app(SmokeConfig)

        from app.models import User, Pathway, WorkProofChallenge, WorkProofSubmission, SkillsPassport, EmployerShortlist

        with app.app_context():
            candidate = User(
                email="candidate@example.ac.za",
                full_name="Lindiwe Test",
                role="candidate",
                institution="Demo University",
                graduation_year=2026,
                location="Durban",
                is_open_to_work=True,
            )
            candidate.set_password("password123")

            employer = User(
                email="employer@example.co.za",
                full_name="Gareth Test",
                role="employer",
                institution="Demo Hiring Team",
                location="Durban",
            )
            employer.set_password("password123")

            pathway = Pathway(
                title="Junior Software Developer",
                slug="junior-software-developer",
                description="Build and explain practical software solutions.",
                market_share_pct=26,
            )
            db.session.add_all([candidate, employer, pathway])
            db.session.flush()

            challenge = WorkProofChallenge(
                pathway_id=pathway.id,
                title="Resilient API",
                scenario="A production API needs validation and safe retries.",
                build_prompt="Build a validated endpoint.",
                explain_prompt="Explain the design and its trade-offs.",
                adapt_prompt="Adapt the endpoint for increased traffic.",
                passing_score=70,
            )
            db.session.add(challenge)
            db.session.flush()

            db.session.add(SkillsPassport(
                user_id=candidate.id,
                readiness_score=82,
                highest_trust_level=4,
                verified_skills_json=json.dumps([{
                    "pathway": pathway.title,
                    "challenge_title": challenge.title,
                    "score": 82,
                    "trust_level": 4,
                    "skills": ["Python", "SQL", "API Validation"],
                }]),
            ))
            submission = WorkProofSubmission(
                user_id=candidate.id,
                challenge_id=challenge.id,
                build_repo_url="https://github.com/example/resilient-api",
                build_code_snippet="def validate(payload):\n    return bool(payload)",
                explain_notes="I validate input before writing to the database.",
                adapt_solution="Add rate limiting and bounded retries.",
                status="verified",
                evidence_score=82,
                readiness_feedback="Good baseline work. Add tests for malformed input.",
                next_best_action="Add focused validation tests and resubmit.",
                feedback_status="failed",
                feedback_error="unavailable",
            )
            db.session.add(submission)
            db.session.flush()
            db.session.add(EmployerShortlist(
                employer_id=employer.id,
                candidate_id=candidate.id,
                notes="Clear reasoning in the submission.",
                status="shortlisted",
            ))
            db.session.commit()
            candidate_id, challenge_id = candidate.id, challenge.id
            submission_id, pathway_slug = submission.id, pathway.slug

        public = app.test_client()
        get_ok(public, "/")
        get_ok(public, "/login")
        get_ok(public, "/register")
        get_ok(public, f"/passport/{candidate_id}")

        candidate_client = app.test_client()
        response = candidate_client.post(
            "/login",
            data={"email": "candidate@example.ac.za", "password": "password123"},
            follow_redirects=True,
        )
        assert response.status_code == 200, f"Candidate sign in failed: {response.status_code}"
        print("PASS candidate sign in")
        get_ok(candidate_client, "/", follow_redirects=True)
        get_ok(candidate_client, "/candidate/dashboard")
        get_ok(candidate_client, "/candidate/profile")
        get_ok(candidate_client, "/candidate/onboarding")
        get_ok(candidate_client, f"/candidate/workproof/{challenge_id}")
        get_ok(candidate_client, f"/assessment/submission/{submission_id}/feedback")
        get_ok(candidate_client, f"/passport/{candidate_id}")
        get_ok(candidate_client, "/settings")

        draft_response = candidate_client.post(
            f"/assessment/submit/{challenge_id}",
            data={
                "build_repo_url": "https://github.com/example/resilient-api",
                "build_code_snippet": "def validate(payload): return bool(payload)",
                "explain_notes": "I validate before storing data.",
                "adapt_solution": "Add rate limiting for increased traffic.",
                "action": "save_draft",
            },
            follow_redirects=False,
        )
        assert draft_response.status_code in (302, 303), (
            f"Saving WorkProof draft failed: {draft_response.status_code}"
        )
        print("PASS WorkProof draft submission")

        employer_client = app.test_client()
        response = employer_client.post(
            "/login",
            data={"email": "employer@example.co.za", "password": "password123"},
            follow_redirects=True,
        )
        assert response.status_code == 200, f"Employer sign in failed: {response.status_code}"
        print("PASS employer sign in")
        get_ok(employer_client, "/", follow_redirects=True)
        get_ok(employer_client, "/employer/dashboard")
        get_ok(employer_client, f"/employer/dashboard?pathway={pathway_slug}&min_trust=3&min_score=70&location=Durban&only_open=on")
        get_ok(employer_client, "/employer/shortlist-board")
        get_ok(employer_client, f"/employer/candidate/{candidate_id}/evidence")
        get_ok(employer_client, "/employer/export/csv")
        get_ok(employer_client, "/settings")

        registration_client = app.test_client()
        response = registration_client.post(
            "/register",
            data={
                "full_name": "New Candidate",
                "email": "new-candidate@example.ac.za",
                "password": "fresh-password-123",
                "role": "candidate",
                "institution": "New Demo University",
                "graduation_year": "2027",
            },
            follow_redirects=True,
        )
        assert response.status_code == 200 and b"Let's make your next step clear" in response.data, (
            "New candidate signup should lead to the onboarding step."
        )
        print("PASS registration leads to candidate onboarding")
        response = registration_client.post(
            "/candidate/onboarding",
            data={
                "target_pathway": pathway_slug,
                "institution": "New Demo University",
                "graduation_year": "2027",
                "location": "Durban",
                "is_open_to_work": "on",
                "skills_summary": "Python and SQL",
            },
            follow_redirects=True,
        )
        assert response.status_code == 200 and b"Pick the work you want to prove" in response.data, (
            "Completing onboarding should open the candidate workspace."
        )
        print("PASS onboarding completion opens candidate workspace")

        print("\nAll Path2Work UX route smoke checks passed.")


if __name__ == "__main__":
    main()
