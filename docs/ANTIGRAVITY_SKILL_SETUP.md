# Antigravity Setup — Path2Work Frontend Build

Use this checklist in Antigravity before starting the build. Keep setup lean because this project is being built on a limited/free plan.

## 1. Open the correct project

Open the local clone of `dillan-garahushoma/FNB-Hackathon` in Antigravity. Make sure it is the merged Flask app, not the historical app under `legacy/`.

## 2. Read the two prompts

Read these files fully before editing:

1. `docs/ANTIGRAVITY_MASTER_BUILD_PROMPT.md`
2. `docs/path2work-frontend-build-prompt.md`

Also glance at `README.md` and the current base template/routes only as needed. The master prompt controls execution; the frontend brief contains the detailed product and screen requirements.

## 3. Install/use the design skill

First check whether `frontend-design-pro` or an equivalent high-quality frontend design skill is already installed. If it is, use it and do not reinstall it.

If the Skills CLI is available and supports Antigravity as an agent target, install the skill with the supported Antigravity target. The upstream skill package is:

```bash
npx skills add PGraeff/frontend-design-pro-agent-skill --skill frontend-design-pro --global --yes --copy
```

If the CLI requires an explicit agent argument, consult its brief help output and use the supported Antigravity agent name. Do **not** blindly use a Codex-only target or spend time troubleshooting. If the CLI is not available or the install fails once, continue using the prompt and built-in design capabilities.

Invoke the installed skill as `$frontend-design-pro` if that invocation syntax is supported by this Antigravity setup.

## 4. Optional guidance plugins — only if missing and supported

Check whether Antigravity's `agy` plugin command exists. If it does, and these plugins are not already installed, you may install:

```bash
agy plugin install https://github.com/addyosmani/agent-skills.git
agy plugin install https://github.com/GoogleChrome/modern-web-guidance
```

These are optional. Do not spend the build budget troubleshooting them, and do not install duplicate or overlapping packs.

## 5. MCP connections

Use only what is already available and relevant:
- **GitHub** — repository context and source control integration.
- **Context7** — look up a library/API detail only when needed.
- **Chrome DevTools MCP or Playwright MCP** — one targeted visual sanity check only if already configured and affordable.
- **shadcn MCP** — not required for this Flask/Jinja application; do not migrate to React or introduce shadcn runtime dependencies.

Do not add MCP servers merely to collect tools. Avoid duplicating capabilities already built into Antigravity.

## 6. Start the build

Paste this instruction into Antigravity:

> Read `docs/ANTIGRAVITY_MASTER_BUILD_PROMPT.md` and `docs/path2work-frontend-build-prompt.md` fully. Check for the frontend-design-pro skill and relevant existing MCP connections; install only the skill/guidance that is missing, compatible, and quick to install, following `docs/ANTIGRAVITY_SKILL_SETUP.md`. Then immediately implement the entire Path2Work frontend in this repository, following the master prompt phases in order without stopping for approval. Generate and integrate the five specified images. Preserve Flask/Jinja routes and backend behaviour. I am on a limited/free plan: prioritise building the complete experience, avoid exhaustive tests and repeated audits, and finish with a concise report of what changed and any real blockers.

## 7. Budget rule

Do not spend the session on elaborate planning, installing many tools, full test suites, or repeated visual test loops. One short repository inspection, one focused implementation pass through all phases, and one short sanity pass are enough. Never claim a test passed unless it was actually run.
