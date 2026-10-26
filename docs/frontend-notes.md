# Path2Work Frontend Implementation Notes

## 1. Overview
Rebuilt and polished the complete Path2Work frontend adhering strictly to the server-rendered Flask/Jinja architecture. Replaced arbitrary layout styles with a cohesive, editorial South African tech talent platform experience.

## 2. Screens Implemented & Polished
1. **Public Landing Page (`GET /`)** (`app/templates/index.html`)
   - High-impact editorial hero utilizing `path2work-hero.webp`
   - Three-stage WorkProof explanation (Build 40% / Explain 30% / Adapt 30%)
   - Five-tier trust ladder explainer (Level 1 to Level 5)
   - Employer screening funnel metric (illustrative 500 applicants to 60 pre-qualified)
   - One-click demo evaluator accounts gated by `DEMO_MODE`
2. **Sign In (`GET /login`)** (`app/templates/auth/login.html`)
   - Split-panel layout integrating `path2work-auth.webp`
   - Password reveal toggle with accessible `aria-pressed` and `aria-label`
   - Categorized demo logins for candidates and employers with quick-fill actions
3. **Register (`GET /register`)** (`app/templates/auth/register.html`)
   - Progressive enhancement: role switcher seamlessly adapts fields for Candidate vs Employer
   - Institutional `.ac.za` email guidance for Level 3 Source Verification
   - Live password strength meter
4. **Candidate Dashboard (`GET /candidate/dashboard`)** (`app/templates/candidate/dashboard.html`)
   - Welcome banner with institutional badge and open-to-work status
   - Segmented five-level trust ladder display
   - Readiness score card featuring the 70 benchmark threshold marker
   - Dynamic next-best-action guidance panel
   - Pathway track grid integrating `path2work-pathway-development.webp` and `path2work-pathway-support.webp`
5. **Candidate Profile & Preferences (`GET /candidate/profile`)** (`app/templates/candidate/profile.html`)
   - Two-column settings interface allowing candidates to update metro location and Open-to-Work availability
   - Full backend persistence wired safely to `candidate.profile` route
6. **WorkProof Stepper (`GET /candidate/workproof/<id>`)** (`app/templates/candidate/workproof_stepper.html`)
   - Persistent 3-stage progress rail (Build &rarr; Explain &rarr; Adapt)
   - Monospace dark-surface code editor with live line count
   - Real-time word count with thinness warning threshold (&lt;40 words)
   - Draft saving (`action=save_draft`) and final submission triggers
   - Removed orphaned `app/templates/assessment/workproof_stepper.html`
7. **AI Feedback (`GET /assessment/submission/<id>/feedback`)** (`app/templates/assessment/feedback.html`)
   - Distinct verified states: Pending (with polite auto-polling), Failed (with retry action), Ready (full 100-pt breakdown), Legacy, and Unreviewed
   - Stage-by-stage score breakdown (points of 40/30/30) and scoring limitation callouts
8. **Skills Passport (`GET /passport/<user_id>`)** (`app/templates/candidate/skills_passport.html`)
   - Publicly shareable credential with seal badge and `P2W-ZA-XXXX` identifier
   - Five-tier trust ladder status
   - Verified competencies grouped by pathway with extracted skill chips
   - Accordion WorkProof evidence view with syntax code blocks
   - Clean `@media print` PDF styles
9. **Employer Talent Pipeline (`GET /employer/dashboard`)** (`app/templates/employer/dashboard.html`)
   - KPI metrics row rendering: Total Applicants, WorkProof Completed, Pre-Qualified (>=70), and Shortlisted counts
   - Integrated `path2work-employer-talent.webp` context banner
   - Advanced screening filters (Pathway, Skill, Location, Trust Level, Open to Work)
   - Ranked candidate rows with extracted skill tags and direct evidence access
   - Live CSV export
10. **Employer Shortlist Board (`GET /employer/shortlist-board`)** (`app/templates/employer/shortlist_board.html`)
    - Three-stage recruitment board: Shortlisted &rarr; Invited to Technical Interview &rarr; Not a Fit
    - Recruiter notes and direct evidence deep-linking
11. **Candidate Evidence Review (`GET /employer/candidate/<id>/evidence`)** (`app/templates/employer/candidate_evidence.html`)
    - Two-column layout with sticky decision sidebar
    - Status management and private recruiter notes
    - "Endorse as Level 5" employer action with confirmation prompt

## 3. Five Generated Images Created & Integrated
All stored in `app/static/images/` and documented in `app/static/images/README.md`:
1. `path2work-hero.webp` &mdash; Public Landing Hero
2. `path2work-auth.webp` &mdash; Sign In & Sign Up Panels
3. `path2work-pathway-support.webp` &mdash; IT Support / Cloud Pathway Card
4. `path2work-pathway-development.webp` &mdash; Software Engineering Pathway Card
5. `path2work-employer-talent.webp` &mdash; Employer Talent Discovery Banner

## 4. Logo Asset
- Copied from `C:\Users\garah\Downloads\Path2Work_ Your Future Forward.png` into `app/static/assets/path2work-logo.png`
- Configured in header navigation, footer, and favicon

## 5. Backend Dependencies & Fixes Handled
1. **`DEMO_MODE`:** Explicitly defined in `config.py` (defaults to `True` for demo/testing).
2. **Employer KPIs:** Fully wired and displayed on `employer/dashboard.html`.
3. **Candidate Location & Availability:** Implemented `GET` and `POST` routes at `/candidate/profile` persisting to the SQLAlchemy `User` model.
4. **Shortlist Board:** Built dedicated route `/employer/shortlist-board` and template.
5. **Orphan Stepper:** Safely removed `app/templates/assessment/workproof_stepper.html`.
6. **Self-Hosted Design Tokens:** Implemented `app/static/css/styles.css` containing tokens, components, and print rules.
