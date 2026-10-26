# Path2Work UI redesign notes

## What changed on branch `ui/path2work-product-redesign`

- Replaced the single dark horizontal authenticated header with a light workspace shell: persistent desktop sidebar, role-specific navigation, current-page state, account identity, and a compact top bar.
- Kept public routes on a separate lighter header so the marketing/auth experience doesn't inherit the authenticated application's navigation.
- Introduced a shared token-led visual layer for surfaces, borders, spacing, controls, feedback messages, focus states, reduced motion, and responsive layout.
- Applied a specific landing hero and sign-in image treatment while preserving the existing Jinja forms, route names, and backend-driven values.
- Updated existing image references to use the canonical `.jpg` asset paths present in this repository.

## Design references used

The implementation takes principles—not copied UI—from the following public guidance:

- [Vercel Web Interface Guidelines](https://vercel.com/design/guidelines): keyboard operability, visible focus, responsive coverage, deliberate alignment, clear typography, resilient content, native links, and reduced-motion behavior.
- [Vercel's web-interface-guidelines repository](https://github.com/vercel-labs/web-interface-guidelines): practical design/interaction rules that are framework-agnostic.
- [Wix Headless: Moving Your Site to a Custom Frontend](https://support.wix.com/en/article/wix-headless-moving-your-site-to-a-custom-frontend): illustrates the separation between a custom frontend and existing backend/business data. This is an architectural comparison, not a recommendation to move Path2Work's data into Wix.

## Architecture decision

Path2Work already has a Flask backend and server-rendered Jinja templates. A strong visual interface does not require React: CSS and shared templates can deliver a polished product UI without re-implementing auth, forms, permissions, evidence state, and AI feedback.

A React frontend is also possible, but the present Flask pages submit HTML forms and render Jinja views rather than exposing a complete JSON API. A future React migration should therefore be a deliberate project: preserve the Flask services/models, add explicit authenticated API endpoints, and migrate one workflow at a time. Do not replace the existing backend with a builder's generated storage/auth just to improve the UI.

Before adopting Wix Vibe or another builder, confirm that the current plan can export the actual source code and that the output can be hosted independently. A visual preview or published URL is not a portable codebase. Any extracted frontend must be wired to Path2Work's existing Flask routes/API and must not silently replace its data store or authentication model.

## Scope / checks

This is a focused visual pass on the shared shell and common component styling. It does not claim full cross-browser, accessibility, or end-to-end validation. Review the branch locally, run the existing app, and check one candidate journey and one employer journey before merging.
