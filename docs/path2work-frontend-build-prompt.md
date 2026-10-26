# Path2Work — Frontend Build Prompt

> Derived from `docs/` (the FNB AOTY Hackathon 2026 programme, the Path2Work Mentor
> Presentation, and the hackathon framework deck) and grounded in the app that now lives in
> this repository. Everything below the horizontal rule is the prompt itself — paste it into a
> frontend agent or hand it to a designer.

---

## Context: what we are building

**Path2Work — "Prove Before Hire."** A South African early-career IT readiness and verified-talent
platform. IT students and recent graduates prove they can do the job *before* someone gives them
their first job; employers see verified evidence before they interview.

**The pivot that defines the product.** The original broad concept — a generic youth employment
platform with profiles, CV guidance, job matching and an AI assistant — was cut. The panel signal
was "CAN USE, CAN NOT BUY, WOULD PAY: R0". The product is now narrow and specific:

> From "help me find a job" → **"help me prove I can do the work."**

**Who it is for.** Final-year IT students and recent IT graduates in South Africa. Not every
unemployed young person. 1st-year students are future pipeline only.

**The one journey that matters.** Do not build a marketplace. Prove one complete role-specific
journey end to end:

1. Choose a target IT role (a *pathway*).
2. Complete one **WorkProof** challenge.
3. Prove understanding across three stages — **Build → Explain → Adapt** (40% / 30% / 30%).
4. Earn a **Skills Passport** carrying an evidence score (0–100) and a trust level (1–5).
5. The employer sees a role-fit signal and can act on it.

**The trust layer.** Every badge must say what was actually verified.

- Evidence trust levels: **1** Self-Declared · **2** Evidence Attached · **3** Source Verified ·
  **4** Path2Work Assessed · **5** Employer Verified.
- Proof of understanding: **Build** (can they complete the task?) · **Explain** (can they explain
  their choices?) · **Adapt** (can they change it when requirements change?).

**Business model (for tone only — the student never pays).** Students get free core access;
employers pay for qualified shortlists, sponsored WorkProof campaigns and talent-pipeline access.

**Positioning to keep in the copy.** LinkedIn records your career. OfferZen helps move a tech
career. Path2Work helps prove you are ready to start one.

**Why this is judged this way.** The hackathon scores Product (10), Creativity (10), Usability (10),
Sustainability (10), Impact (10), Presentation (10) and Intelligence (10). Usability and Product are
a third of the score, so polish, clarity and a working happy path are not optional.

---

## Your task

Rebuild and extend the frontend of this Flask app so it fully expresses the product above. Work
screen by screen and component by component. Keep the existing server-rendered Jinja architecture
and every existing route contract; you are replacing the *presentation*, not the backend.

### Hard constraints

- **Stack stays as-is.** Flask application factory + blueprints (`auth`, `candidate`, `employer`,
  `assessment`). Templates live in `app/templates/` and extend `app/templates/base.html`. Keep
  `url_for('blueprint.view')` names and every form `action`/`method` and field `name` exactly as
  they are, or the app breaks.
- **Stop shipping Tailwind from the CDN.** `https://cdn.tailwindcss.com` is a development crutch and
  a real performance cost on South African prepaid data. Move to a compiled Tailwind build (or
  hand-written CSS) with only the classes actually used, and self-host the fonts. Keep the same
  design tokens and class names so templates do not churn.
- **Low-data first.** Target a light page. No heavy JS frameworks, no icon-font CDN if a small
  inline SVG sprite will do, lazy-load below-the-fold imagery, and make every interactive feature
  degrade without JavaScript (the app already ships `<noscript>` fallbacks and server-side forms —
  preserve that).
- **Accessible by default: WCAG 2.1 AA.** Semantic landmarks, one `h1` per page in order, skip link,
  visible `:focus-visible` ring, `aria-current="page"` on nav, `role="alert"`/`role="status"` on
  messages, `role="progressbar"` with `aria-valuenow` on scores, labelled every input,
  `prefers-reduced-motion` respected, and text/background contrast that passes. This is also a
  product claim — one of the pathways is an accessibility pathway.
- **South African reality.** Assume cheap Android phones, intermittent connectivity, load-shedding
  and mixed language confidence. Keep copy short and plain. Leave room for isiZulu and Afrikaans
  labels (build the copy so a translation layer can drop in without layout breakage).
- **Print matters.** The Skills Passport and the employer evidence view must print cleanly to PDF.
  There is already a `@media print` block — keep and extend it.
- **Do not invent backend endpoints.** If a screen needs data the backend does not send today, mark
  it clearly as a backend dependency in your notes rather than fabricating a route.

### Design system to keep and extend

Existing tokens (in `base.html`) — keep the meaning, improve the execution:

| Token | Value | Meaning |
|---|---|---|
| `ink` | `#0F1B2D` | Headings, dark panels, primary button |
| `build` / `build-dark` / `build-soft` | `#635BFF` / `#4B43D6` / `#EEEDFF` | **Build** stage |
| `prove` / `prove-dark` / `prove-soft` | `#14967F` / `#0E6F5E` / `#E6F5F1` | **Explain** stage, "verified", passed scores |
| `match` / `match-dark` / `match-soft` | `#E66C37` / `#B24616` / `#FDEFE7` | **Adapt** stage, employer actions |

Colour carries meaning — never use build/prove/match decoratively. Red is not in the palette as an
accent: reserve danger for genuine failures only.

- **Type:** Bricolage Grotesque (display/headings), Figtree (body), JetBrains Mono (code, scores,
  IDs). Every number that is a score is set in the display face at heavy weight.
- **Components already defined:** `.card`, `.btn` + `.btn-primary` / `.btn-secondary` /
  `.btn-accent`, `.field` / `.field-label` / `.field-hint`, `.badge`, `.code-block`. Formalise these
  into a documented component set (see "Components to build") and add the missing ones.
- **Radii and rhythm:** rounded-2xl cards, 8px-ish controls, generous spacing, 16px mobile gutters.

### Deliverables

1. A refreshed `app/templates/base.html` (app shell, tokens, component layer) plus a shared
   `app/templates/components/` set of Jinja partials for the components listed below.
2. Every screen below, rebuilt against its documented data contract.
3. The missing screens below, built.
4. A short `docs/frontend-notes.md` recording: what you changed, any backend dependency you found,
   and the demo script path you verified.

---

## Screen-by-screen brief

Each screen lists its route, the template, the data it receives, and what to build.
`[POLISH]` means the screen exists — raise it to the standard. `[BUILD]` means it does not exist yet.

### App shell — `base.html` `[POLISH]`

Sticky ink header, brand lockup with the P2W mark, role-aware nav (candidate: Dashboard · My Skills
Passport; employer: Talent pipeline), account block (name + role), sign in / Get verified when
signed out. Flash messages dismissible, `role="alert"` for errors and `role="status"` otherwise.
Mobile: nav collapses to a scrollable row (already) — consider a proper disclosure menu so it does
not overflow with the account block. Footer carries the positioning line.

### 1. Public landing page — `GET /` `[BUILD]`

Today `/` silently redirects to sign-in. The product needs a front door that sells the pivot to
three audiences: the student, the employer, and a hackathon judge.

Data: none required (static, but `current_user` aware — signed-in users should be offered their
dashboard instead of sign-up).

Build: hero carrying the positioning ("A CV says what you know. Path2Work shows what you can do.")
with a primary "Get verified" and a secondary "See a real Skills Passport" that links to a seeded
public passport (`/passport/<id>` is already public — link a demo candidate). A Build/Explain/Adapt
explainer strip (the three-stage 40/30/30 story). A five-level trust ladder explainer. A "how an
employer uses this" funnel block (500 applicants → 220 IT students → 95 WorkProof → 60
pre-qualified, labelled *illustrative*). A "for employers" band pointing at the pipeline. A demo
accounts block (gated by a real `DEMO_MODE` config flag — see backend notes). An FAQ or objection
row attacking the risky assumptions: which role first, what proof employers trust, what fraud
controls exist. Footer.

### 2. Sign in — `auth/login.html` `[POLISH]`

Data: `current_user`, `config` (`DEMO_MODE`), demo account lists (currently hardcoded in the
template), flash messages.

Keep the strong split layout: editorial pitch + 3-step explainer on the left, sticky sign-in card on
the right, form first on mobile. Polish the demo-account disclosure — group employers and
candidates, show each candidate's trust level and score as a visual ladder rather than text, and
state the shared password. Keep the password-reveal control with correct `aria-pressed`. Add
inline validation messaging and a "forgot password" affordance marked as not-yet-wired if the
backend does not have it.

### 3. Register — `auth/register.html` `[POLISH]`

Data: flash messages, role.

Keep the candidate/employer role cards and the JS that swaps the institution label, placeholder,
email hint and hides graduation year for employers — but rebuild it so it works as **progressive
enhancement**: with JS off, both fields must still be sensible and submittable. Keep the `.ac.za`
hint that sets up Level 3 source verification. Add a password strength hint and inline error state
(the backend currently flashes errors rather than returning field errors — note that dependency).

### 4. Candidate dashboard — `GET /candidate/dashboard` `[POLISH]`

Data: `user` (full_name, institution, graduation_year), `passport` (readiness_score,
highest_trust_level, trust_level_label), `pathways[]` (title, description, market_share_pct,
`challenges[0]`), `submissions_by_challenge` (status, evidence_score), `latest_submission`
(readiness_feedback, next_best_action).

Build: a greeting that names the person and their one fact (institution, class of year). A clear
five-segment **trust ladder** for the current level. A **readiness score** block — big display
number, progress bar with the 70 passing mark drawn on it, and a plain sentence about how far to go.
A dark **next step** panel driven by `latest_submission.next_best_action`, falling back to a
"start a challenge" prompt. A latest-feedback card. Then the **pathway chooser**: nine cards, each
with the pathway title, description, "N% of SA entry-level demand", the challenge title and a
clamped scenario, the submission status badge, and the right CTA for the state —
`Not started` → Start challenge · `in_progress` → Resume challenge · `submitted`/`verified` →
View feedback (score) + Improve and resubmit. Make the pathway grid filterable or grouped so nine
cards do not overwhelm; the docs say three MVP pathways lead, so visually prioritise Junior Software
Developer, Junior Data Analyst and IT Support / Cloud.

### 5. WorkProof stepper — `GET /candidate/workproof/<challenge_id>` `[POLISH]`

Template: `candidate/workproof_stepper.html`. Data: `challenge` (title, scenario, build_prompt,
explain_prompt, adapt_prompt, passing_score, pathway.title) and `submission` (any saved draft).

Rebuild the three-stage stepper properly. It is the core of the product and currently the weakest
screen. Keep the production-scenario brief panel and the three tabs with their weights. Upgrade:
a real persistent stepper (numbered rail showing Build/Explain/Adapt with completion state, not just
highlighted tabs); the stage prompts as clearly separated "brief" callouts in their stage colour;
a code editor feel for the Build snippet (monospace, dark surface, line-count hint); a word-count
and "this looks thin" hint on Explain and Adapt (the backend's guards cap thin answers — surface
that *before* submission so it is fair); an explicit draft state ("Saved 2 minutes ago — your work
is kept") tied to the existing `action=save_draft` submit; a summary of what will be scored; and a
prominent Submit for verification action with a confirmation that explains Build 40% / Explain 30% /
Adapt 30% and the passing score. Keep `name` attributes exactly: `build_repo_url`,
`build_code_snippet`, `explain_notes`, `adapt_solution`, `action`.

> **Reconcile the duplicate.** `app/templates/assessment/workproof_stepper.html` is an orphan —
> nothing renders it. Delete it or fold anything useful into the candidate version.

### 6. AI feedback — `GET /assessment/submission/<id>/feedback` `[POLISH]`

Template: `assessment/feedback.html`. Data: `submission` (feedback_status, feedback_error),
`challenge` (title, passing_score, pathway.title), `feedback` (score, summary, scores per stage out
of 4, points earned of 40/30/30, per-stage comments, strengths[], improvements[], next_step, notes[]
scoring limits, flags, `generated_at`, `model`, extracted skills).

Five distinct states must each look right:

1. **pending** — reviewing. Keep the polite spinner and the existing status polling (it already
   shows a "this is taking longer than usual" message after 45s). Make it feel calm and honest,
   not a dead spinner; reassure that the submission is saved.
2. **failed** — explain which failure (`unavailable`, `bad_reply`, `timed_out`, `error`), reassure
   that nothing was lost, offer *Try the review again* and a route back to the dashboard. Ollama
   will often be down in a demo — this state must look intentional, not broken.
3. **ready** — the payoff screen. Big score out of 100, passed/failed framing against
   `passing_score`, the reviewer's summary, the amber "how your score was limited" banner when
   `notes` is non-empty, three stage cards in stage colours showing x/4 and points earned, "what you
   did well" and "what to improve" lists, the next-step panel, and the **AI disclosure** kept
   verbatim ("This is a first review written by an AI model…"). Add a score breakdown visual
   (per-stage contribution to the total).
4. **legacy** — a stored `readiness_feedback` with no breakdown; offer a full review.
5. **never reviewed** — offer a review.

### 7. Skills Passport — `GET /passport/<user_id>` `[POLISH]`

Template: `candidate/skills_passport.html`. Publicly shareable. Data: `candidate` (full_name,
institution, graduation_year, email — **contact details only for the owner and signed-in
employers**), `passport` (readiness_score, highest_trust_level, trust_level_label,
verified_skills[]), `submissions[]` (challenge + pathway, status, evidence_score,
readiness_feedback, build_repo_url, build_code_snippet, explain_notes, adapt_solution),
`trust_tiers[]` (5 levels).

This is the artefact a candidate puts on a CV or LinkedIn, so it must look like a credential.
Keep: the dark passport header with the seal badge, the `P2W-ZA-0000` passport ID, the score/trust
stat block, copy-link and print actions, the owner "this is how employers see it" notice, the
five-level trust ladder (reached / current / locked), verified competencies grouped by pathway with
skill chips, and the expandable WorkProof evidence with the Build/Explain/Adapt colour-coded
columns. Improve the print stylesheet so the printed passport is one clean document. Add a
share-friendly empty-of-chrome layout for signed-out viewers, and make the "build your own passport"
CTA strong for anonymous visitors.

### 8. Employer talent pipeline — `GET /employer/dashboard` `[POLISH]`

Template: `employer/dashboard.html`. Data: `candidates[]` ({user, passport, best_submission,
shortlist}), `pathways[]`, current filters (`selected_pathway`, `min_trust`, `min_score`,
`search_skill`, `location_filter`, `only_open`), and — **currently passed but never rendered** —
`total_applicants`, `workproof_completed_count`, `prequalified_count`, `shortlisted_count`.

Build the KPI row the backend already computes: applicants, WorkProof completed, pre-qualified
(level ≥ 4 and score ≥ 70), shortlisted. Then the filter bar (role pathway, tech stack/skill,
location, minimum trust level, open-to-work toggle, apply/reset) — it should read as a proper
screening tool. Then the result list: each row shows the candidate, institution and location, an
Open-to-Work pill, the trust-level badge, the pathway, the top extracted skills, the role-fit score,
and the shortlist status if one exists, with Review evidence as the action. Sort is by readiness
descending — state that in the header. Add a proper empty state that explains which filter is
likely too tight and offers reset. Consider a list/board toggle: the shortlist data
(shortlisted / invited / rejected) supports a small pipeline board.

### 9. Candidate evidence review — `GET /employer/candidate/<user_id>/evidence` `[POLISH]`

Template: `employer/candidate_evidence.html`. Data: `candidate`, `passport`, `submissions[]`
(full Build/Explain/Adapt content plus prompts and scores), `shortlist` (status, notes).

This is the screen the employer decision hangs on, and the one that proves Path2Work does not
replace their vetting. Keep the two-column layout with the **sticky decision panel**. Keep the dark
submission headers with status and score, the AI-review callout with its honesty caption, the
collapsible prompts, and the colour-coded Build/Explain/Adapt sections with code blocks. Improve:
a trust-level explainer inline (what level 4 actually means), the funnel context ("Path2Work
verifies baseline capability; you still do identity checks, your own technical assessment and the
interview"), and a clearer *Endorse as Level 5* action with its confirmation. Make printing the
whole evidence pack clean.

### 10. Employer shortlist board — `[BUILD]`

The backend already stores shortlist status (`shortlisted` / `invited` / `rejected`) and notes, and
`POST /employer/shortlist/<candidate_id>` already accepts `status`, `notes`, `action` and
`next_url`, but there is no board view. Build a filterable board grouping candidates by pipeline
status, with the notes visible, and an entry point to each candidate's evidence page.

### 11. Candidate profile and preferences — `[BUILD]` — **highest-value gap**

`User` already has `location` and `is_open_to_work`, and the employer pipeline filters on both, but
**no screen lets a candidate set them.** Location and open-to-work are also part of the candidate's
own readiness story. Build a profile/preferences screen: institution, graduation year, location,
open-to-work toggle, target pathway(s), and a short skills summary. Follow the two-column settings
pattern — label and description column beside a panel per section, sections split by rules — and
make saving explicit and confirmed. Flag the backend dependency: there is no update route for these
fields today.

### 12. First-run onboarding — `[BUILD]`

A new candidate lands on a dashboard with a score of 20 and no explanation. Add a short first-run
flow (target role → location and availability → open to work → "here is how WorkProof works") that
ends by launching their first challenge. Keep it to a few steps and never block the dashboard.

### 13. Account settings — `[BUILD]`

Password change, sign-out, and account details. Use the same two-column settings pattern. Do not
invent a delete-account flow without a backend route; note it as a dependency.

---

## Components to build

Extract these as Jinja partials in `app/templates/components/` and document each in
`docs/frontend-notes.md`.

**Primitives**
- `button` — primary / secondary / accent / ghost / destructive, sizes, `disabled`, loading state.
- `field` — label, hint, error, required marker; text, email, password, number, search, select,
  textarea; with and without a trailing action (password reveal).
- `badge` / `pill` — neutral, positive (verified), warning, negative; optional leading icon.
- `card` and `panel` — with title, optional count chip and optional "view all" link.
- `callout` — info / warning / success, used for stage briefs and AI notes.
- `code-block` — monospace, dark surface, copy button, max-height with scroll.
- `empty-state` — icon, headline, explanation, one primary action.
- `flash-stack` — success / error / warning / info, dismissible, correct ARIA roles.
- `skeleton` — loading placeholders for the pathway grid, pipeline rows and feedback page.

**Product-specific**
- `trust-ladder` — the five evidence trust levels as a horizontal ladder, with reached / current /
  locked states; compact (segmented bar) and full (five cards) variants.
- `readiness-score` — the score display plus progress bar with the 70 passing mark; size variants.
- `stage-tabs` / `stage-rail` — Build / Explain / Adapt navigation with weights and completion.
- `pathway-card` — pathway + demand share + challenge + submission state + the correct CTA.
- `workproof-evidence` — the Build/Explain/Adapt evidence block used on both the passport and the
  employer evidence page (colour-coded, collapsible prompt, repo link, code, notes).
- `score-breakdown` — x/4 per stage and points earned of 40/30/30, with the total.
- `skill-chip` — a verified skill, optionally in an extracted/self-declared variant.
- `pipeline-row` — the employer candidate row (identity, badges, skills, score, action).
- `filter-bar` — the employer screening filters, with an active-filter summary and reset.
- `kpi-tile` — label, big value, plain caption (no deltas), for the computed employer counts.
- `stepper` — the generic numbered progress rail used by onboarding and WorkProof.
- `demo-account-card` — name, organisation, email, trust level and score; used on the landing page
  and sign-in.

Keep the server-rendered approach: these are Jinja macros/includes, not a JavaScript component
framework.

---

## Voice and copy rules

- Plain South African English. Short sentences. No hype, no "revolutionise", no emoji in headings.
- Be specific and kind — the AI feedback voice is the model for the whole product ("This is a
  tender, so say what you did and why", not "Great job!!").
- Always say what was verified, never imply more than the evidence supports.
- Every AI-written block carries a visible disclaimer and says a human should check.
- Every score is explained: what it is out of, what the passing mark is, and what to do next.

## Acceptance checklist

- [ ] All 13 screens render with no template errors, signed in and signed out, and with an
      unseeded or half-seeded database (empty states everywhere).
- [ ] No Tailwind CDN, no font CDN, no render-blocking external script; page weight and request
      count measured and reported.
- [ ] Every form still posts to its existing endpoint with its existing field names; draft save,
      submit, shortlist and endorse all still work.
- [ ] Keyboard-only pass over the WorkProof stepper, the feedback page, the pipeline filters and
      the evidence decision panel.
- [ ] Screen-reader spot check on the stepper, the trust ladder, the score bars and the flash
      messages.
- [ ] Skills Passport and employer evidence print to clean PDFs.
- [ ] WCAG 2.1 AA contrast on every reachable colour pair, including the soft tints.
- [ ] The hackathon demo script below runs end to end without a single dead end.

## The demo script the frontend must support

Prepare so this path is smooth and nothing is a placeholder:

1. Land on `/` (public page) and read the one-line proposition.
2. Sign in as the Level 5 verified candidate (`sipho.dlamini@richfield.ac.za`) — dashboard shows a
   high trust level and score.
3. Open a WorkProof, walk Build → Explain → Adapt, save a draft, then submit.
4. Land on the AI feedback page — show the pending state, then the scored review.
5. Open the Skills Passport and print it.
6. Sign in as the employer (`talent@paystack-sa.co.za`) — show the pipeline, filter by pathway and
   trust level, open a candidate's evidence, then endorse them to Level 5.

## Backend dependencies to flag (do not fake these)

1. **`DEMO_MODE`** is read by `login.html` from `config` but is never defined in `config.py` — it
   currently always evaluates true, so demo accounts always show. Define it properly.
2. **Employer KPI counts** (`total_applicants`, `workproof_completed_count`, `prequalified_count`,
   `shortlisted_count`) are computed and passed to the dashboard but never rendered.
3. **No route updates `location` or `is_open_to_work`**, yet the employer pipeline filters on both.
4. **No shortlist board** view exists despite the status data and the update route.
5. **`app/templates/assessment/workproof_stepper.html` is orphaned** — delete or reconcile it.
6. **Registration errors are flashed, not returned per field**, so inline field errors on register
   and login need a backend change or must stay as a summary.
7. **No password reset or email verification** route exists; the `.ac.za` Level 3 story has no UI
   that acts on it.
