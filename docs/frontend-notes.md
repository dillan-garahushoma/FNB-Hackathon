# Path2Work Frontend Redesign Notes

## Product direction

Path2Work helps South African IT students and recent graduates demonstrate job readiness through role-specific WorkProof challenges and a shareable Skills Passport. The experience is designed around **evidence before interviews**, rather than a generic job board or a metrics-heavy admin dashboard.

Visual direction references established hiring and professional products for interaction patterns, not copied layouts:
- [LinkedIn Recruiter](https://www.linkedin.com/business/talent/blog/talent-acquisition/tips-for-getting-the-most-out-of-linkedin-recruiter) — clear search and candidate information hierarchy.
- [Wellfound](https://wellfound.com/) — human-first talent discovery.
- [Greenhouse's visual candidate pipeline](https://support.greenhouse.io/hc/en-us/articles/4874727408795-Visual-Candidate-Pipeline) — visible hiring-stage progression.
- [Indeed candidate sourcing](https://www.indeed.com/help/employers/articles/360015979211) — practical search criteria.

## Implementation

The application remains Flask + Jinja + SQLAlchemy. This is a presentation and workflow refactor; it does not replace the app with React, introduce a second data layer, or fabricate API routes. Existing route names, form actions, form field names, session logic and database models are retained.

### Screens and journeys updated

1. **Public landing page** — a more focused editorial hero, real product promise, three-stage WorkProof explanation (Build 40% / Explain 30% / Adapt 30%), five evidence-trust levels, employer value proposition, and clear calls to action.
2. **Role-aware app shell** — distinct public and authenticated navigation, role-specific workspace navigation, clearer page titles, flash messaging, keyboard skip link, and responsive sidebar/navigation behavior.
3. **Sign in** — direct benefit copy, password visibility control, evaluator account quick-fill, and demo credentials aligned with `seed.py`.
4. **Registration** — candidate/employer onboarding with an explanatory side panel and preserved server-side form contract and role-selection behavior.
5. **Candidate workspace** — readiness score and 70-point marker, trust progression, next-step guidance, recent WorkProof activity, pathway cards, searchable/filterable pathways, and explicit challenge actions.
6. **WorkProof assessment** — Build / Explain / Adapt stage rail, preserved field names and draft/submission actions, clear 40/30/30 score weighting, and a no-JavaScript fallback where all stage panels remain available.
7. **Assessment feedback** — differentiated pending/failed/ready/legacy/unreviewed states retained, with clearer score presentation and per-stage contribution bars.
8. **Skills Passport** — public shareable credential, verification ladder, skill evidence, expandable WorkProof responses, copy-link and print actions.
9. **Candidate profile** — clearer identity, institution, location and Open-to-Work settings, still saved through the existing POST route.
10. **Employer talent discovery** — visible candidate-pool metrics, server-backed pathway/skill/location/trust/score/Open-to-Work filters, ranked evidence summaries, readiness and trust signals, CSV export and shortlist navigation.
11. **Employer evidence review** — clearer evidence sections and decision sidebar styling, preserving existing shortlist and endorsement forms.
12. **Employer shortlist board** — readable hiring-stage columns and candidate evidence links, preserving existing status-management routes.
13. **First-run candidate onboarding** — a skippable role/location/open-to-work setup that persists preferences and resumes after next sign-in if left incomplete.
14. **Account settings** — account identity, real password change with current-password verification and clear sign-out; no fake password-reset or delete-account actions.
15. **Candidate context** — target pathway and optional self-described skills shown separately from assessed evidence in discovery, candidate evidence, and the Skills Passport.

## Routing and data behavior

- A signed-in user visiting `/` is redirected to the correct role dashboard. This fixes a case where the landing hero could render inside the authenticated workspace shell.
- Candidate pathway search is a client-side view filter over the pathways already sent by Flask; it does not invent new pathways or backend endpoints.
- Employer filters remain GET parameters consumed by `employer.dashboard`.
- `candidate_preferences` persists target pathway, skills context and onboarding completion. The app factory's `db.create_all()` creates this table for existing SQLite deployments.
- Candidate registration requires a password of at least eight characters. Password changes validate the current password, new-password length, confirmation and reuse.
- WorkProof stage navigation uses tab/tabpanel semantics, arrow-key navigation, and synchronised hidden/visible state.
- Demo account email addresses shown on sign-in now match the account records created by `seed.py`. The shared demo password remains `password123` as configured by seed data.

## Styling and assets

The redesign adds a shared light visual system, accessible focus states, responsive layouts, purposeful spacing, proof-stage color semantics, score meters, clearer candidate rows, print rules and restrained hover motion. It uses existing local project imagery under `app/static/images/`.

**Known follow-up:** existing templates rely heavily on Tailwind utility classes and currently load Tailwind from its CDN. Replacing this with a compiled, minimal local stylesheet and self-hosted font/icon assets is a separate performance pass; removing the CDN before compiling equivalent utilities would break many pages.

## Verification status and next review

- Changes are committed to `ui/path2work-product-redesign` for review in [PR #1](https://github.com/dillan-garahushoma/FNB-Hackathon/pull/1); `main` has not been merged or changed by this PR.
- A GitHub Actions workflow has been added to compile Python, compile Jinja templates, and run `tests/run_flow_test.py`.
- I could not clone the repository or launch a local browser from the editing environment, so the visual appearance and the complete browser journey still require a local preview. Do not treat the redesign as browser/E2E verified until the CI result and a candidate/employer preview have been inspected.
- Recommended preview sequence: public landing → register/sign in → candidate dashboard → WorkProof draft → submit/review → Skills Passport; then sign in as employer → talent discovery filters → candidate evidence → shortlist board → CSV export.
