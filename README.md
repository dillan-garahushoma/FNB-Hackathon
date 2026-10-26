# Path2Work — Prove Before Hire

Path2Work is a South African early-career IT readiness and verified-talent platform.
IT students and recent graduates prove they can do the job — with role-specific WorkProof
challenges (Build → Explain → Adapt), a readiness score and a Skills Passport with five
evidence trust levels — and employers review that evidence before they interview.

This project is the merged work from both hackathon repositories:

- `NqobaMhlongo/FNB-HACKERTHON` — the base Flask application (blueprints, models, seed data, Jinja frontend).
- `AyandaMnyango/FNB-Hackathon` — a superset of the above, adding the AI review layer, the
  assessment screens and the upgraded employer pipeline.

Every file from `NqobaMhlongo/FNB-HACKERTHON` is contained in the merged tree, so pulling the
`AyandaMnyango/FNB-Hackathon` version in loses nothing.

The previous single-page Path2Work site (`app.py`, `templates/`, `static/`, `tests/`) has been
moved to `legacy/` and is no longer part of the running application.

## Stack

- Flask 3 (application factory + blueprints: `auth`, `candidate`, `employer`, `assessment`)
- Flask-SQLAlchemy 3 with SQLite (`path2work.db`)
- Server-rendered Jinja templates in `app/templates/`, styled with Tailwind (CDN), the
  Phosphor icon set, and a Build/Prove/Match design system defined in `app/templates/base.html`
- Optional local AI review via Ollama (`ai_feedback.py`) — the app still works without it

## Run locally

1. Create and activate a virtual environment:

   ```powershell
   py -m venv .venv
   .\.venv\Scripts\Activate.ps1
   ```

2. Install dependencies:

   ```powershell
   python -m pip install -r requirements.txt
   ```

3. Seed the database with pathways, challenges, demo candidates and demo employers:

   ```powershell
   python seed.py
   ```

4. Start the application:

   ```powershell
   python run.py
   ```

   Open <http://127.0.0.1:5000>.

## Demo accounts

Seeded by `seed.py`. Password for all accounts: `password123`.

| Role | Email |
|---|---|
| Employer | `talent@paystack-sa.co.za` |
| Verified candidate (Level 5) | `sipho.dlamini@richfield.ac.za` |
| Verified candidate (Level 4) | `zanele.khumalo@wits.ac.za` |
| New candidate (Level 1) | `lerato.mokoena@tut.ac.za` |

## Routes

| Route | Purpose |
|---|---|
| `/` | Role-aware entry — redirects to the right dashboard or to sign in |
| `/login`, `/register`, `/logout` | Authentication (candidate or employer) |
| `/settings` | Account basics and authenticated password change |
| `/candidate/onboarding` | First-run candidate setup: target pathway, location, availability and optional profile context |
| `/candidate/dashboard` | Candidate home: readiness score, trust level, next step and pathway chooser |
| `/candidate/profile` | Update institution, graduation year, location, open-to-work state, target pathway and optional self-described skills |
| `/candidate/workproof/<challenge_id>` | The three-stage WorkProof stepper |
| `/assessment/submit/<challenge_id>` | Saves a WorkProof draft or submits it for review |
| `/assessment/submission/<id>/feedback` | AI first review, with status polling and retry |
| `/passport/<user_id>` | Public Skills Passport (contact details gated to owner/employers) |
| `/employer/dashboard` | Talent discovery with pathway, skill, location, trust, score and Open-to-Work filters | 
| `/employer/shortlist-board` | Review candidates by shortlist status and next action |
| `/employer/candidate/<user_id>/evidence` | Full candidate evidence review + shortlist actions |
| `/employer/export/csv` | CSV export of verified candidates |

## Candidate profile data

Candidate role preferences are stored in the `candidate_preferences` table: selected target pathway, optional self-described skills context, and onboarding completion. The existing application factory calls `db.create_all()`, so the table is created when the app next starts. The summary can be used for discovery, but is explicitly labelled self-described and is not considered verified evidence. Existing candidate records continue to work without a preferences row until the candidate saves their profile.

## AI review (optional)

`ai_feedback.py` sends each submitted WorkProof to a local Ollama model
(`llama3.2:3b` by default) and stores a structured review. Configure with environment variables:

- `OLLAMA_URL` (default `http://localhost:11434/api/chat`)
- `OLLAMA_MODEL` (default `llama3.2:3b`)
- `OLLAMA_TIMEOUT` (default `180`)
- `AI_AUTO_VERIFY` (default `true`)

If Ollama is not running, submissions are saved and the feedback page offers a retry — nothing
is lost.

## Tests

`tests/run_flow_test.py` exercises the AI feedback pipeline against a stand-in app with a faked
model, so it needs no Ollama. Run it from the project root:

```powershell
python tests/run_flow_test.py
```
