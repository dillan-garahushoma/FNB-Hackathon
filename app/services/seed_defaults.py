"""Auto-seed baseline pathways and challenges if the database is unseeded.

Ensures platforms deployed on ephemeral hosting (e.g. Render, Railway) always
have active pathways and challenges without requiring manual shell execution.
"""
from app import db
from app.models import Pathway, WorkProofChallenge

DEFAULT_PATHWAYS = [
    {
        "title": "Junior Software Developer",
        "slug": "junior-software-developer",
        "description": "Backend & full-stack application engineering focused on clean API design, input validation, error handling, and production bug resolution.",
        "market_share_pct": 26,
        "challenge": {
            "title": "RESTful API & Bug Resolution",
            "scenario": "You have joined a Cape Town fintech startup building a voucher disbursement API. Production logs show duplicate redemptions and unhandled 500 crashes when malformed payloads hit the /api/v1/vouchers/redeem endpoint. Implement a resilient endpoint with strict validation, explain your architectural choices, and adapt it for scale.",
            "build": "Implement the POST /api/v1/vouchers/redeem endpoint in Python (Flask/FastAPI). Include input payload validation (voucher_code, user_id, amount_zar), idempotency or state checks to prevent double-redemption, and appropriate HTTP status codes. Provide your GitHub repository link and core endpoint code snippet.",
            "explain": "Justify your choice of data structures, transaction locking/idempotency strategy, and why you selected specific HTTP status codes (e.g., 400 vs 409 vs 422) for each failure mode.",
            "adapt": "CHANGE REQUEST: A retail partner now queries GET /api/v1/vouchers/history during month-end spikes, causing database timeouts and abusive scraping. Modify your solution to handle pagination and rate-limiting (e.g., 60 requests/min per API key).",
            "passing_score": 70,
        },
    },
    {
        "title": "IT Support / Cloud",
        "slug": "it-support-cloud",
        "description": "Linux server administration, automated bash diagnostics, network firewall hardening (UFW), and cloud infrastructure incident response.",
        "market_share_pct": 18,
        "challenge": {
            "title": "Linux Server Diagnostics & Firewall Config",
            "scenario": "An Ubuntu 22.04 cloud VM hosting a student portal in a Johannesburg data center is experiencing high CPU load and unauthorized SSH brute-force attempts. Automate system health diagnostics and lock down network access without disrupting HTTPS traffic.",
            "build": "Write a Bash diagnostic script that captures CPU/memory usage, disk I/O, top 5 processes, and failed SSH logins, plus a set of UFW firewall rules that enforce least-privilege access. Provide your repository link and full script.",
            "explain": "Explain your port security choices, why default deny policies matter, and how your diagnostic script isolates root causes during an active production incident.",
            "adapt": "CHANGE REQUEST: Attackers are rotating IPs to bypass simple static blocks. Update your bash workflow and configuration to integrate automated fail2ban jail rules and dispatch a webhook alert whenever an IP is banned more than 3 times in 10 minutes.",
            "passing_score": 70,
        },
    },
    {
        "title": "Junior Data Analyst",
        "slug": "junior-data-analyst",
        "description": "Data cleaning, SQL/Python aggregation, missing-record imputation, and KPI reporting for South African retail and financial operations.",
        "market_share_pct": 12,
        "challenge": {
            "title": "Retail Sales Data Cleaning & Aggregation",
            "scenario": "A national grocery retailer in Gauteng exports daily POS transaction logs from 140 stores. Due to intermittent load-shedding sync issues, 8% of records have missing unit_price or duplicate transaction_id entries. Finance needs an accurate provincial KPI summary.",
            "build": "Write a Python (Pandas) or SQL pipeline that deduplicates transaction records, handles missing unit_price and store_region values, and computes total revenue, average basket size, and top 5 categories per province. Attach your repository URL and code.",
            "explain": "Defend your imputation strategy (e.g., category median vs mean vs dropping rows) and explain how your choice prevents distortion of provincial revenue KPIs.",
            "adapt": "CHANGE REQUEST: The retailer has acquired stores in neighbouring countries, and historical CSV dumps mix currencies with timestamps in different timezones. Adapt your aggregation logic to normalize multi-currency transactions using daily FX rates.",
            "passing_score": 70,
        },
    },
    {
        "title": "Junior Cybersecurity & SOC Analyst",
        "slug": "junior-cybersecurity-analyst",
        "description": "SIEM log triage, credential-stuffing detection, POPIA personal data masking, and incident containment for South African banking and telecoms.",
        "market_share_pct": 11,
        "challenge": {
            "title": "Authentication Log Forensics & Incident Containment",
            "scenario": "A Durban regional retail bank detects anomalous login surges at 02:00 AM. Initial triage suspects a credential-stuffing assault targeting graduate accounts. You must parse the access logs, identify attacking IPs, and draft an immediate containment rule.",
            "build": "Write a log parser in Python that extracts IP addresses, failure ratios, targeted accounts, and timestamps. Output an executive summary and a blocklist config.",
            "explain": "Explain how you differentiate distributed attacks from forgotten passwords, and justify your containment thresholds under POPIA guidelines.",
            "adapt": "CHANGE REQUEST: The attacker switches to low-and-slow distributed proxies. Modify your detection algorithm to track geographic velocity and anomalous user-agent patterns.",
            "passing_score": 70,
        },
    },
    {
        "title": "Junior QA & Test Automation Engineer",
        "slug": "junior-qa-automation",
        "description": "Automated API regression testing, boundary value analysis, payment double-debit prevention, and CI test integration using Pytest/Playwright.",
        "market_share_pct": 9,
        "challenge": {
            "title": "Payment Gateway Regression Test Suite",
            "scenario": "A payments platform is releasing an instant-clearing feature. QA must deliver automated test coverage covering idempotency, timeout recovery, and boundary cases.",
            "build": "Write a Pytest test suite covering positive payment flows, duplicate transaction prevention, negative boundary values, and simulated network timeouts.",
            "explain": "Explain your test case prioritization matrix and justify why idempotency tests require explicit race condition verification.",
            "adapt": "CHANGE REQUEST: Integration tests must execute in parallel within GitHub Actions under 90 seconds. Refactor your suite with fixtures and mocks.",
            "passing_score": 70,
        },
    },
    {
        "title": "Junior DevOps & Cloud Native Engineer",
        "slug": "junior-devops-engineer",
        "description": "Docker containerization, multi-stage image hardening, GitHub Actions CI/CD pipelines, and Kubernetes health-probe resilience during load-shedding.",
        "market_share_pct": 8,
        "challenge": {
            "title": "Multi-Stage Docker Hardening & CI Pipeline",
            "scenario": "A containerized Flask API is running as root with an unpinned 800MB image. You must produce an optimized, non-root, multi-stage Dockerfile and a GitHub Actions workflow.",
            "build": "Write a hardened multi-stage Dockerfile using python:3.11-slim, create an unprivileged user, and write a GitHub Actions workflow that builds, scans, and tests the container.",
            "explain": "Explain why running as non-root mitigates container breakout vulnerabilities and defend your caching strategy.",
            "adapt": "CHANGE REQUEST: Deployments must support zero-downtime rolling updates with liveness and readiness health checks. Update your configuration.",
            "passing_score": 70,
        },
    },
    {
        "title": "Junior Mobile App Developer",
        "slug": "junior-mobile-developer",
        "description": "Offline-first Android/Flutter/React Native architecture, local SQLite sync queues, and low-bandwidth resilience for township & rural field operations.",
        "market_share_pct": 7,
        "challenge": {
            "title": "Offline-First Mobile Sync Queue",
            "scenario": "Field workers in low-connectivity areas log client applications on mobile devices. When network drops, data must save locally and safely sync when reconnected.",
            "build": "Implement an offline-first storage and synchronization mechanism with conflict detection and idempotency.",
            "explain": "Defend your synchronization strategy, queue state transitions, and how you prevent duplicate submissions on flaky networks.",
            "adapt": "CHANGE REQUEST: Network payload size must be reduced by 60% over 2G connections. Implement delta-compression and payload batching.",
            "passing_score": 70,
        },
    },
    {
        "title": "Junior Business Intelligence & SQL Developer",
        "slug": "junior-bi-sql-developer",
        "description": "Data warehouse star-schema modelling, complex SQL window functions, and National Credit Act (NCA) arrears cohort reporting.",
        "market_share_pct": 5,
        "challenge": {
            "title": "Arrears Cohort Analysis & Star Schema Modelling",
            "scenario": "Credit risk leaders need a monthly vintage delinquency report to track loan repayment cohorts across South African provinces.",
            "build": "Write an advanced SQL script with window functions (PARTITION BY, LAG/LEAD) to calculate 30/60/90-day arrears rates per origination vintage.",
            "explain": "Explain your SQL window function calculations, dimensional grain selection, and indexing strategy for multi-million row scans.",
            "adapt": "CHANGE REQUEST: The dashboard requires daily dynamic recalculation for executive reporting. Create a materialized view or incremental query design.",
            "passing_score": 70,
        },
    },
    {
        "title": "Junior UI/UX & Frontend Engineer",
        "slug": "junior-frontend-uiux",
        "description": "Accessible WCAG 2.1 AA responsive interfaces, semantic HTML/JS validation, multi-language support, and sub-100KB low-data performance optimization.",
        "market_share_pct": 4,
        "challenge": {
            "title": "Accessible Low-Bandwidth Candidate Onboarding Flow",
            "scenario": "Job seekers on low-end mobile devices report high friction and validation errors during onboarding. You must deliver an accessible, resilient form.",
            "build": "Build a responsive, accessible multi-step form with keyboard navigation, inline ARIA feedback, and zero render-blocking dependencies.",
            "explain": "Explain your accessibility audit findings, keyboard focus trap management, and how your markup adheres to WCAG 2.1 AA criteria.",
            "adapt": "CHANGE REQUEST: Add offline local-storage auto-save so incomplete form entries survive accidental page refreshes or connection drops.",
            "passing_score": 70,
        },
    },
]


def ensure_default_pathways():
    """Ensure baseline pathways and challenges exist in the database (idempotent)."""
    pathways = []
    for item in DEFAULT_PATHWAYS:
        existing = Pathway.query.filter_by(slug=item["slug"]).first()
        if existing:
            pathways.append(existing)
            continue

        p = Pathway(
            title=item["title"],
            slug=item["slug"],
            description=item["description"],
            market_share_pct=item["market_share_pct"],
        )
        db.session.add(p)
        db.session.flush()

        ch = item.get("challenge")
        if ch:
            challenge = WorkProofChallenge(
                pathway_id=p.id,
                title=ch["title"],
                scenario=ch["scenario"],
                build_prompt=ch["build"],
                explain_prompt=ch["explain"],
                adapt_prompt=ch["adapt"],
                passing_score=ch["passing_score"],
            )
            db.session.add(challenge)

        pathways.append(p)

    db.session.commit()
    return Pathway.query.order_by(Pathway.market_share_pct.desc()).all()
