# Path2Work — Antigravity Master Frontend Build Prompt

> **Purpose:** Give Antigravity one source of truth for a complete, polished frontend build in the existing repository. Read this file together with `docs/path2work-frontend-build-prompt.md`.

## Mission

Build the Path2Work frontend in one continuous run, moving through the phases below in order without stopping for approval between phases. Prioritise shipping the implementation over exhaustive testing. The developer is using a limited Antigravity plan: do not spend the budget on repeated repo audits, full test suites, browser-test loops, or speculative refactors. Inspect only what is needed to understand the existing template/routes, implement the work, perform a small final sanity check, and report honestly.

**Product promise:** “A CV says what you know. Path2Work shows what you can do.”

Path2Work is a South African early-career IT readiness and verified-talent platform. Candidates complete a role-specific WorkProof challenge across **Build (40%) → Explain (30%) → Adapt (30%)**, then present evidence through a Skills Passport with trust levels from 1 to 5. Employers review proof before interviewing. Students do not pay; the business model is employer-side.

## Read these sources first

1. `docs/path2work-frontend-build-prompt.md` — full product context, existing screen inventory, design/UX requirements, accessibility, acceptance criteria, demo script.
2. This file — execution plan, skill/tool guidance, image generation brief, and budget limits.
3. `README.md` and only the relevant route/template/base/config files needed to preserve existing contracts.

Treat the existing code and route names as authoritative. Do not assume an endpoint exists just because a design would benefit from it.

## Hard constraints — preserve the working app

- Keep Flask, the application factory, blueprints, SQLAlchemy models, server-rendered Jinja templates and existing URL contracts.
- Do **not** migrate to React, Next.js, Vite, or another frontend framework.
- Do not introduce Wix/Base44/v0 runtime dependencies or make the deployed product depend on a builder.
- Preserve every existing `url_for(...)`, form action/method, input `name`, session/auth flow, permission check, validation, AI feedback/retry flow, and CSV export.
- Keep the existing app and `legacy/` intact except where a necessary compatibility fix is clear.
- No fake data presented as live, fake buttons, pretend AI features, invented routes, or client-side-only changes that appear to save data without persisting it.
- Do not expose secrets, API keys, or environment values in templates or browser JavaScript.
- Be careful with low-bandwidth South African users and budget Android phones. Avoid heavy dependencies, unnecessary animation, external image services, and unnecessary remote font/icon requests.

## Visual direction

Create an exceptionally considered, editorial product experience — premium, confident, human, clear, and specific to Path2Work. Avoid the generic AI-dashboard look.

### Core palette

- Ink/navy: `#0F1B2D`
- Primary violet: `#635BFF`
- Teal: `#14967F`
- Accent orange: `#E66C37`
- App background: `#F7F8FC`
- Main text: `#172033`
- Secondary text: `#687386`
- Borders: `#E5E9F0`

Use these as design tokens in one coherent system. Keep typography, spacing, radii, shadows, borders, iconography, buttons, forms, badges, navigation, tables and feedback states consistent. Use strong editorial type hierarchy and purposeful whitespace. Glassmorphism/blur can be used sparingly where it serves a clear visual purpose; do not put every element in a frosted card. Use gradients only when justified. Avoid excessive rounded cards, decorative blobs, stock dashboard layouts, and generic slogans.

### Design quality requirements

- Design the actual journey, not isolated screens: each page should make the next action obvious.
- Use purposeful empty, loading, success, error, disabled and retry states.
- Make trust and evidence legible: show what has and has not been verified; never imply a higher trust level than the stored data supports.
- Candidate and employer experiences must feel designed for their distinct goals.
- Responsive layouts for mobile first, then tablet and desktop.
- WCAG 2.1 AA-oriented: semantic landmarks, clear heading order, labels, visible keyboard focus, accessible status/error messages, useful alt text, contrast, and reduced-motion support.
- Preserve server-side form behaviour and sensible no-JavaScript fallbacks.
- Print-friendly Skills Passport and employer evidence view.
- Use inline/local SVGs or existing icon tooling rather than adding an icon-font CDN.
- Centralise reusable components/styles. Do not create a separate design language per template.

## Images — generate exactly five originals

Use Antigravity's available image-generation capability to create **exactly five** useful, original, realistic images. Save them in `app/static/images/` using these filenames. If the image tool cannot save files directly, create the images through the available UI and save them into this folder; do not waste the session trying repeatedly to make a tool work. Do not substitute remote URLs.

1. **`path2work-hero.webp`** — wide cinematic hero image. A young African technology professional in a real-feeling modern workspace, subject weighted to the right, generous dark negative space on the left for a white heading. Aspirational but believable, natural light, editorial photography.
2. **`path2work-auth.webp`** — vertical/cropped portrait of an African early-career professional working thoughtfully at a laptop in a contemporary workspace. Warm, welcoming, confident, realistic. For sign-in/sign-up split panel.
3. **`path2work-pathway-support.webp`** — African IT support professional diagnosing a workstation/network issue in a real small-business or campus environment. Show practical work, not posed stock photography.
4. **`path2work-pathway-development.webp`** — African junior software developer building and reviewing code at a computer, focused and credible; no readable code or UI text.
5. **`path2work-employer-talent.webp`** — diverse African technology colleagues collaborating around a real work task, natural candid composition, suitable for employer/talent discovery.

For all five: no text, letters, logos, watermarks, mockup frames, dashboard screenshots, or uncanny hands/faces. Avoid overly polished generic stock-photo staging. Choose crops that work at the intended aspect ratio and use overlays only when needed for text contrast. Integrate each image into the relevant page during the same build — do not merely generate and leave unused.

Create `app/static/images/README.md` documenting the five filenames, intended placements, crop/ratio guidance, and clear placeholder slots for future images the developer may add. Keep image references easy to replace, use Flask static paths, and ensure missing future images do not break layout. Do not invent additional images beyond these five; use CSS, inline SVGs, and existing assets for other visuals.

## Screen and implementation sequence

Work through all phases in one run. Do not stop after the landing page.

### Phase 1 — foundation and design system
- Inspect the current `base.html`, static assets, template inventory, relevant routes, and existing CSS approach.
- Define tokens and reusable styles/components for layout, typography, navigation, buttons, forms, notices, badges, score displays, evidence blocks, tables, progress, and responsive behaviour.
- Improve the base template without breaking route contracts.
- The existing brief asks to remove Tailwind CDN usage. If a local compiled build already exists, use it. Otherwise prefer a maintainable self-hosted CSS implementation that fits this app and does not require a complex new build pipeline. Do not leave a permanent Tailwind CDN dependency if you can replace it safely in this pass.
- Self-host assets where feasible; avoid pulling in a large frontend stack.

### Phase 2 — landing and authentication
- Polish the landing page around the “prove before hire” promise and one clear primary action.
- Make sign-in and sign-up visually compelling using `path2work-auth.webp`.
- Preserve existing fields, endpoint names, validation and role behaviour. Improve inline validation/error presentation where supported; do not invent password-reset or email-verification flows if the backend does not implement them.

### Phase 3 — candidate onboarding and dashboard
- Make the candidate's next step unmistakable: choose/continue a pathway, complete WorkProof, review feedback, improve the Skills Passport.
- Add or polish profile editing for fields already supported by the model, especially location and open-to-work status, only if persistence can be wired to an existing or safely added route and the backend permissions remain correct.
- If a backend dependency is genuinely missing, do not fake persistence. Leave a clearly documented dependency.

### Phase 4 — pathways and WorkProof
- Design pathway selection with the supplied support and development images.
- Polish the Build → Explain → Adapt stepper and reuse the existing `app/templates/assessment/workproof_stepper.html` if appropriate rather than leaving it orphaned.
- Preserve assessment submission fields, draft/save behaviour, validation and route contracts.
- Communicate progress, expectations and stage weighting clearly without distracting from the task.

### Phase 5 — AI feedback and Skills Passport
- Make AI feedback explain strengths, gaps, next actions, and the status of the review. Keep retry/status behaviour connected to the existing backend. If Ollama is unavailable, communicate that accurately while preserving the saved submission.
- Do not call AI providers directly from browser JavaScript.
- Make the Skills Passport feel like a credible shareable evidence document: score, trust level, verified proof, pathway, and clear distinction between self-declared and assessed skills. Keep it print-friendly.

### Phase 6 — employer experience
- Polish the employer dashboard and candidate discovery/evidence flow around faster, evidence-led screening.
- Render the employer KPI values already computed by the backend instead of leaving them unused.
- Use `path2work-employer-talent.webp` in a relevant, restrained placement.
- Preserve filters, candidate evidence access controls, shortlist actions and CSV export.
- Build a useful shortlist board/view if the existing shortlist data and status/update route support it. If the route or data model is insufficient, document the exact missing backend dependency instead of faking status changes.
- Keep candidate evidence private behind existing authorisation rules.

### Phase 7 — responsive and finishing pass
- Apply consistent responsive treatment to all screens, including navigation, forms, tables, score components and the Skills Passport.
- Add thoughtful empty/error/success states where they can be implemented with existing data.
- Confirm all five generated images are integrated, references are local, and future-image replacement instructions exist.
- Make only a short final sanity pass on key templates, broken asset references, and route/form contracts. Do **not** run the full test suite or repeated browser automation unless a specific implementation blocker makes it essential.

## Known issues to handle carefully

The existing repo review identified these possible gaps; confirm only what is needed while implementing:
- `DEMO_MODE` is referenced by login template but may not be defined in configuration. Add a safe default (disabled unless intentionally enabled) if still missing.
- Employer KPI counts may be computed but not rendered.
- Employer filters use candidate location/open-to-work fields, but the UI may not currently let candidates maintain those fields.
- There may be no complete shortlist board even though shortlist actions/status logic exists.
- Registration errors may be flashed globally instead of shown next to the relevant field.
- Password reset and email verification are not implemented; do not imply otherwise.
- The existing `legacy/` app and `legacy/tests/test_app.py` are historical. Do not migrate them into the active app.

## Skills and MCP/tool guidance

Before coding, inspect the skills and MCP connections already available in Antigravity. Keep setup short and avoid duplicates. Read `docs/ANTIGRAVITY_SKILL_SETUP.md` for suggested commands.

Use the `frontend-design-pro` skill if installed and compatible with this Antigravity environment. Use a modern web-design guidance skill if already available. Use Context7 only when a genuine API/library detail needs checking. Use Chrome DevTools or Playwright MCP only for a brief targeted visual check if already configured and affordable. Use the existing GitHub connection for repository context. Do not install a large collection of overlapping skills or MCP servers. Do not add React/shadcn just because a shadcn MCP is available; this is a Flask/Jinja app.

## Token and execution discipline

- Start work immediately after reading the brief; no long planning response, no approval checkpoints.
- Make focused edits in the repository. Prefer implementing the full journey over polishing one page endlessly.
- Do not repeatedly reread the whole repository or the entire brief.
- Do not run exhaustive tests, full test suites, dependency scans, or multiple browser loops.
- Do not install packages unless needed for the implementation.
- Do not spend time troubleshooting an optional skill/MCP install. If setup fails once, continue with the available design capability.
- Do not commit or push changes unless the user explicitly requests it.
- Finish with a concise report: screens completed, five image files created and placements, important files changed, any genuinely blocked backend dependencies, and a simple run instruction. Be honest about what was and was not checked.

**Success means:** the actual Flask app now has a cohesive, distinctive, responsive, evidence-first Path2Work experience across candidate and employer journeys — not just a mockup, not just a landing page, and not a frontend rewrite.
