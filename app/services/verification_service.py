import json
import re
from datetime import datetime, timezone
from app.models import User, WorkProofChallenge, WorkProofSubmission, SkillsPassport

REPO_URL_PATTERN = re.compile(
    r"^https?://(www\.)?(github\.com|gitlab\.com|bitbucket\.org)/[A-Za-z0-9_.-]+/[A-Za-z0-9_.-]+/?.*$",
    re.IGNORECASE,
)

PATHWAY_KEYWORDS = {
    "junior-software-developer": {
        "build": ["def ", "return", "status", "json", "route", "request", "400", "404", "409", "422", "200"],
        "explain": ["status", "lock", "idempoten", "validation", "transaction", "409", "422", "conflict", "error"],
        "adapt": ["pagina", "limit", "cursor", "offset", "rate", "429", "redis", "token", "cache"],
        "verified_skills": [
            "RESTful API Implementation",
            "Payload Validation & Error Handling",
            "Database Concurrency & Idempotency",
            "Pagination & Rate-Limiting Architecture",
        ],
    },
    "junior-data-analyst": {
        "build": ["select", "group by", "fillna", "drop_duplicates", "median", "mean", "sum", "pandas", "df", "join"],
        "explain": ["imput", "median", "mean", "outlier", "skew", "missing", "kpi", "null", "duplicate"],
        "adapt": ["currency", "fx", "exchange", "zar", "nad", "bwp", "timezone", "utc", "convert", "join"],
        "verified_skills": [
            "Data Cleaning & Deduplication",
            "Statistical Missing-Data Imputation",
            "Provincial KPI Aggregation",
            "Multi-Currency Normalization",
        ],
    },
    "it-support-cloud": {
        "build": ["#!/bin/bash", "ufw", "allow", "deny", "top", "ps", "df", "free", "grep", "sshd", "port"],
        "explain": ["least privilege", "deny", "port", "ssh", "22", "443", "firewall", "diagnostic", "root cause"],
        "adapt": ["fail2ban", "jail", "ban", "webhook", "curl", "alert", "ip", "retry", "log"],
        "verified_skills": [
            "Bash Automated System Diagnostics",
            "UFW Firewall Hardening",
            "Linux Incident Triage",
            "Automated Fail2Ban & Alerting",
        ],
    },
    "junior-cybersecurity-analyst": {
        "build": ["import", "re", "log", "ip", "popia", "sha256", "hash", "failed", "alert", "json", "parse"],
        "explain": ["popia", "pii", "mask", "false positive", "brute", "credential", "regulator", "incident"],
        "adapt": ["siem", "mitre", "webhook", "block", "token", "revoke", "session", "quarantine", "rate"],
        "verified_skills": [
            "SIEM Log Parsing & Threat Triage",
            "POPIA PII Masking & Compliance",
            "Brute-Force & Credential Stuffing Detection",
            "Automated Incident Containment",
        ],
    },
    "junior-qa-automation": {
        "build": ["pytest", "assert", "def test_", "status_code", "response", "client", "json", "parametrize", "400", "200"],
        "explain": ["boundary", "equivalence", "idempoten", "race", "regression", "mock", "fixture", "edge"],
        "adapt": ["github", "actions", "ci", "yaml", "parallel", "retry", "flaky", "report", "coverage"],
        "verified_skills": [
            "Pytest API Regression Suites",
            "Boundary Value & Equivalence Partitioning",
            "Payment Double-Debit Edge Testing",
            "CI/CD Test Pipeline Integration",
        ],
    },
    "junior-devops-engineer": {
        "build": ["from ", "dockerfile", "workdir", "copy", "run", "expose", "cmd", "user", "healthcheck", "alpine", "slim"],
        "explain": ["multi-stage", "non-root", "layer", "cache", "image", "security", "healthcheck", "size"],
        "adapt": ["kubernetes", "deployment", "livenessprobe", "readinessprobe", "resources", "limits", "rollback", "helm"],
        "verified_skills": [
            "Multi-Stage Docker Containerization",
            "Container Hardening (Non-Root & Minimal Image)",
            "CI/CD Pipeline Automation",
            "Kubernetes Probes & Zero-Downtime Rollouts",
        ],
    },
    "junior-mobile-developer": {
        "build": ["async", "await", "queue", "sqlite", "local", "sync", "retry", "status", "fetch", "conflict", "json"],
        "explain": ["offline", "eventual", "uuid", "idempoten", "battery", "bandwidth", "conflict", "storage"],
        "adapt": ["delta", "compress", "gzip", "backoff", "exponential", "2g", "3g", "chunk", "batch"],
        "verified_skills": [
            "Offline-First Local Persistence",
            "Idempotent Background Sync Queues",
            "Timestamp & Version Conflict Resolution",
            "Low-Bandwidth Exponential Backoff",
        ],
    },
    "junior-bi-sql-developer": {
        "build": ["with ", "select", "join", "group by", "case when", "sum", "count", "over", "partition by", "coalesce"],
        "explain": ["cte", "window", "index", "null", "grain", "fact", "dimension", "ncr", "arrears"],
        "adapt": ["materialized", "partition", "incremental", "star schema", "slowly changing", "scd", "power bi"],
        "verified_skills": [
            "Advanced SQL CTEs & Window Functions",
            "Star Schema & Warehouse Fact Modelling",
            "Credit Risk & Arrears Cohort Analytics",
            "Query Indexing & Partition Optimization",
        ],
    },
    "junior-frontend-uiux": {
        "build": ["aria-", "role=", "label", "form", "input", "required", "error", "button", "focus", "tabindex"],
        "explain": ["wcag", "accessibility", "screen reader", "contrast", "keyboard", "bandwidth", "progressive", "semantic"],
        "adapt": ["localstorage", "service worker", "offline", "lazy", "debounce", "i18n", "zulu", "afrikaans"],
        "verified_skills": [
            "Semantic HTML5 & WCAG 2.1 AA Accessibility",
            "Keyboard Navigation & ARIA Live States",
            "Low-Bandwidth Performance Optimization",
            "Multi-Language (i18n) & Offline Form Recovery",
        ],
    },
}


def evaluate_workproof_submission(
    user: User, challenge: WorkProofChallenge, submission: WorkProofSubmission
) -> dict:
    """
    Evaluates a candidate's 3-stage Build -> Explain -> Adapt WorkProof submission.
    Weights:
      - Build Phase:   40% (max 40 points)
      - Explain Phase: 30% (max 30 points)
      - Adapt Phase:   30% (max 30 points)
    Calculates the 5-Tier Evidence Trust Level and generates actionable Readiness Feedback.
    """
    pathway_slug = challenge.pathway.slug if challenge.pathway else "junior-software-developer"
    kw_config = PATHWAY_KEYWORDS.get(
        pathway_slug, PATHWAY_KEYWORDS["junior-software-developer"]
    )

    repo_url = (submission.build_repo_url or "").strip()
    code_snippet = (submission.build_code_snippet or "").strip()
    explain_notes = (submission.explain_notes or "").strip()
    adapt_solution = (submission.adapt_solution or "").strip()

    strengths = []
    gaps = []

    # 1. BUILD CHECK (40% Weight -> 0 to 40 pts)
    build_score = 0
    valid_repo = bool(REPO_URL_PATTERN.match(repo_url))
    if valid_repo:
        build_score += 12
        strengths.append("Valid Git repository attached for source traceability")
    elif repo_url.startswith("http"):
        build_score += 6
        gaps.append("Provide a standard GitHub/GitLab repository URL (e.g., https://github.com/username/repo)")
    else:
        gaps.append("Missing valid Git repository link in the Build step")

    code_len = len(code_snippet)
    if code_len >= 220:
        build_score += 16
    elif code_len >= 90:
        build_score += 10
        gaps.append("Expand your Build code snippet to include full validation and edge-case handling")
    elif code_len > 0:
        build_score += 4
        gaps.append("Build implementation snippet is too brief to verify production readiness")

    code_lower = code_snippet.lower()
    matched_build_kw = sum(1 for kw in kw_config["build"] if kw in code_lower)
    build_kw_pts = min(12, matched_build_kw * 3)
    build_score += build_kw_pts
    if build_kw_pts >= 9:
        strengths.append("Build implementation demonstrates core domain constructs and defensive logic")
    else:
        gaps.append("Include clearer domain-specific error checks and validation rules in your Build code")

    build_score = min(40, build_score)

    # 2. EXPLAIN CHECK (30% Weight -> 0 to 30 pts)
    explain_score = 0
    explain_words = len(explain_notes.split())
    if explain_words >= 45:
        explain_score += 15
    elif explain_words >= 20:
        explain_score += 9
        gaps.append("Deepen your Explain narrative with more explicit trade-off reasoning")
    elif explain_words > 0:
        explain_score += 4
        gaps.append("Explain section requires fuller justification of your technical choices")

    explain_lower = explain_notes.lower()
    matched_explain_kw = sum(1 for kw in kw_config["explain"] if kw in explain_lower)
    explain_kw_pts = min(15, matched_explain_kw * 3)
    explain_score += explain_kw_pts
    if explain_kw_pts >= 9:
        strengths.append("Clear technical articulation of architectural trade-offs in the Explain step")
    else:
        gaps.append("Explicitly address the edge cases and design trade-offs asked in the Explain prompt")

    explain_score = min(30, explain_score)

    # 3. ADAPT CHECK (30% Weight -> 0 to 30 pts)
    adapt_score = 0
    adapt_words = len(adapt_solution.split())
    if adapt_words >= 40:
        adapt_score += 15
    elif adapt_words >= 20:
        adapt_score += 9
        gaps.append("Provide more concrete implementation details in the Adapt change-request step")
    elif adapt_words > 0:
        adapt_score += 4
        gaps.append("Adapt response is too short to verify how your solution handles new constraints")

    adapt_lower = adapt_solution.lower()
    matched_adapt_kw = sum(1 for kw in kw_config["adapt"] if kw in adapt_lower)
    adapt_kw_pts = min(15, matched_adapt_kw * 3)
    adapt_score += adapt_kw_pts
    if adapt_kw_pts >= 9:
        strengths.append("Strong adaptability to production requirement changes and scaling constraints")
    else:
        gaps.append("Detail the exact mechanism used to handle the Adapt change request")

    adapt_score = min(30, adapt_score)

    total_score = build_score + explain_score + adapt_score

    # 4. 5-TIER EVIDENCE TRUST LEVEL CALCULATOR
    trust_level = 1
    if repo_url or code_snippet:
        trust_level = 2
    if valid_repo and (user.has_institutional_email or code_len >= 120):
        trust_level = 3
    if total_score >= challenge.passing_score:
        trust_level = 4

    # 5. READINESS FEEDBACK & NEXT BEST ACTION GENERATOR
    strengths_text = (
        "; ".join(strengths)
        if strengths
        else "Initial submission recorded across the Build, Explain, and Adapt stages"
    )
    if gaps:
        gaps_text = "; ".join(gaps[:2])
    else:
        gaps_text = "Add automated unit tests and CI workflow badges to further strengthen employer confidence"

    readiness_feedback = (
        f"Score Breakdown — Build: {build_score}/40 | Explain: {explain_score}/30 | Adapt: {adapt_score}/30. "
        f"Strengths: {strengths_text}. "
        f"Readiness Gap: {gaps_text}."
    )

    if total_score >= challenge.passing_score:
        next_best_action = (
            f"Congratulations! You passed '{challenge.title}' with {total_score}/100 and unlocked "
            f"Trust Level 4 (Path2Work Assessed). Share your verifiable Skills Passport link with employers "
            f"or complete another pathway to broaden your role readiness."
        )
        status = "verified"
    else:
        points_needed = challenge.passing_score - total_score
        next_best_action = (
            f"You scored {total_score}/100 ({points_needed} pts away from the {challenge.passing_score}/100 "
            f"Level 4 verification threshold). Focus on: {gaps[0] if gaps else 'expanding your Explain and Adapt solutions'} "
            f"and re-submit your WorkProof."
        )
        status = "submitted"

    return {
        "evidence_score": total_score,
        "build_score": build_score,
        "explain_score": explain_score,
        "adapt_score": adapt_score,
        "trust_level": trust_level,
        "status": status,
        "readiness_feedback": readiness_feedback,
        "next_best_action": next_best_action,
        "verified_skills": kw_config["verified_skills"],
    }


def sync_skills_passport(
    user: User,
    challenge: WorkProofChallenge,
    evaluation: dict,
    passport: SkillsPassport,
) -> None:
    """Updates the candidate's SkillsPassport based on all their submissions."""
    existing_records = passport.verified_skills
    pathway_title = challenge.pathway.title if challenge.pathway else "IT Pathway"

    updated_records = [
        r for r in existing_records if r.get("challenge_title") != challenge.title
    ]

    if evaluation["evidence_score"] >= challenge.passing_score:
        updated_records.append(
            {
                "pathway": pathway_title,
                "challenge_title": challenge.title,
                "score": evaluation["evidence_score"],
                "trust_level": max(4, passport.highest_trust_level),
                "skills": evaluation["verified_skills"],
                "verified_at": datetime.now(timezone.utc).strftime("%Y-%m-%d"),
            }
        )

    passport.verified_skills_json = json.dumps(updated_records)

    all_scores = [s.evidence_score for s in user.submissions if s.evidence_score is not None]
    all_scores.append(evaluation["evidence_score"])
    passport.readiness_score = max(all_scores) if all_scores else evaluation["evidence_score"]

    if passport.highest_trust_level < 5:
        passport.highest_trust_level = max(
            passport.highest_trust_level, evaluation["trust_level"]
        )
    passport.updated_at = datetime.now(timezone.utc)