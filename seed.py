import json
import random
from datetime import datetime, timezone
from faker import Faker
from app import create_app, db
from app.models import (
    User,
    Pathway,
    WorkProofChallenge,
    WorkProofSubmission,
    SkillsPassport,
    EmployerShortlist,
)

# FIXED: Using default locale to avoid en_ZA AttributeError
fake = Faker()

def seed_database():
    app = create_app()
    with app.app_context():
        print("Dropping old database...")
        db.drop_all()
        db.create_all()

        # ---------------------------------------------------------------------
        # 1. Create 9 South African IT Pathways (Total = 100% Market Share)
        # ---------------------------------------------------------------------
        pathway_dev = Pathway(
            title="Junior Software Developer",
            slug="junior-software-developer",
            description=(
                "Backend & full-stack application engineering focused on clean API design, "
                "input validation, error handling, and production bug resolution."
            ),
            market_share_pct=26,
        )
        pathway_cloud = Pathway(
            title="IT Support / Cloud",
            slug="it-support-cloud",
            description=(
                "Linux server administration, automated bash diagnostics, network firewall "
                "hardening (UFW), and cloud infrastructure incident response."
            ),
            market_share_pct=18,
        )
        pathway_data = Pathway(
            title="Junior Data Analyst",
            slug="junior-data-analyst",
            description=(
                "Data cleaning, SQL/Python aggregation, missing-record imputation, and KPI "
                "reporting for South African retail and financial operations."
            ),
            market_share_pct=12,
        )
        pathway_cyber = Pathway(
            title="Junior Cybersecurity & SOC Analyst",
            slug="junior-cybersecurity-analyst",
            description=(
                "SIEM log triage, credential-stuffing detection, POPIA personal data masking, "
                "and incident containment for South African banking and telecoms."
            ),
            market_share_pct=11,
        )
        pathway_qa = Pathway(
            title="Junior QA & Test Automation Engineer",
            slug="junior-qa-automation",
            description=(
                "Automated API regression testing, boundary value analysis, payment double-debit "
                "prevention, and CI test integration using Pytest/Playwright."
            ),
            market_share_pct=9,
        )
        pathway_devops = Pathway(
            title="Junior DevOps & Cloud Native Engineer",
            slug="junior-devops-engineer",
            description=(
                "Docker containerization, multi-stage image hardening, GitHub Actions CI/CD "
                "pipelines, and Kubernetes health-probe resilience during load-shedding."
            ),
            market_share_pct=8,
        )
        pathway_mobile = Pathway(
            title="Junior Mobile App Developer",
            slug="junior-mobile-developer",
            description=(
                "Offline-first Android/Flutter/React Native architecture, local SQLite sync queues, "
                "and low-bandwidth resilience for township & rural field operations."
            ),
            market_share_pct=7,
        )
        pathway_bi = Pathway(
            title="Junior Business Intelligence & SQL Developer",
            slug="junior-bi-sql-developer",
            description=(
                "Data warehouse star-schema modelling, complex SQL window functions, and "
                "National Credit Act (NCA) arrears cohort reporting."
            ),
            market_share_pct=5,
        )
        pathway_frontend = Pathway(
            title="Junior UI/UX & Frontend Engineer",
            slug="junior-frontend-uiux",
            description=(
                "Accessible WCAG 2.1 AA responsive interfaces, semantic HTML/JS validation, "
                "multi-language support, and sub-100KB low-data performance optimization."
            ),
            market_share_pct=4,
        )

        db.session.add_all([
            pathway_dev, pathway_cloud, pathway_data, pathway_cyber, pathway_qa,
            pathway_devops, pathway_mobile, pathway_bi, pathway_frontend,
        ])
        db.session.flush()

        # ---------------------------------------------------------------------
        # 2. Create 1 Complete WorkProof Challenge per Pathway (9 Challenges)
        # ---------------------------------------------------------------------
        challenge_dev = WorkProofChallenge(
            pathway_id=pathway_dev.id,
            title="RESTful API & Bug Resolution",
            scenario=(
                "You have joined a Cape Town fintech startup building a voucher disbursement API. "
                "Production logs show duplicate redemptions and unhandled 500 crashes when malformed "
                "payloads hit the `/api/v1/vouchers/redeem` endpoint. You need to implement a resilient "
                "endpoint with strict validation, explain your architectural choices, and adapt it for scale."
            ),
            build_prompt=(
                "Implement the `POST /api/v1/vouchers/redeem` endpoint in Python (Flask/FastAPI). "
                "Include input payload validation (voucher_code, user_id, amount_zar), idempotency or "
                "state checks to prevent double-redemption, and appropriate HTTP status codes. "
                "Provide your GitHub repository link and core endpoint code snippet."
            ),
            explain_prompt=(
                "Justify your choice of data structures, transaction locking/idempotency strategy, "
                "and why you selected specific HTTP status codes (e.g., 400 vs 409 vs 422) for each failure mode."
            ),
            adapt_prompt=(
                "CHANGE REQUEST: A retail partner now queries `GET /api/v1/vouchers/history` during month-end "
                "spikes, causing database timeouts and abusive scraping. Modify or extend your solution to "
                "handle cursor/offset pagination and rate-limiting (e.g., 60 requests/min per API key)."
            ),
            passing_score=70,
        )

        challenge_cloud = WorkProofChallenge(
            pathway_id=pathway_cloud.id,
            title="Linux Server Diagnostics & Firewall Config",
            scenario=(
                "An Ubuntu 22.04 cloud VM hosting a student portal in a Johannesburg data center is experiencing "
                "high CPU load and unauthorized SSH brute-force attempts. You must automate system health "
                "diagnostics and lock down network access without disrupting HTTPS traffic."
            ),
            build_prompt=(
                "Write a Bash diagnostic script that captures CPU/memory usage, disk I/O, top 5 processes, "
                "and failed SSH logins, plus a set of UFW firewall rules that enforce least-privilege access. "
                "Provide your repository link and full script."
            ),
            explain_prompt=(
                "Explain your port security choices, why default deny policies matter, and how your diagnostic "
                "script isolates root causes during an active production incident."
            ),
            adapt_prompt=(
                "CHANGE REQUEST: Attackers are rotating IPs to bypass simple static blocks. Update your bash "
                "workflow and configuration to integrate automated `fail2ban` jail rules and dispatch a webhook "
                "alert whenever an IP is banned more than 3 times in 10 minutes."
            ),
            passing_score=70,
        )

        challenge_data = WorkProofChallenge(
            pathway_id=pathway_data.id,
            title="Retail Sales Data Cleaning & Aggregation",
            scenario=(
                "A national grocery retailer in Gauteng exports daily POS transaction logs from 140 stores. "
                "Due to intermittent load-shedding sync issues, 8% of records have missing `unit_price` "
                "or duplicate `transaction_id` entries. Finance needs an accurate provincial KPI summary."
            ),
            build_prompt=(
                "Write a Python (Pandas) or SQL pipeline that deduplicates transaction records, handles "
                "missing `unit_price` and `store_region` values, and computes total revenue, average basket "
                "size, and top 5 categories per province. Attach your repository URL and code."
            ),
            explain_prompt=(
                "Defend your imputation strategy (e.g., category median vs mean vs dropping rows) and explain "
                "how your choice prevents distortion of provincial revenue KPIs."
            ),
            adapt_prompt=(
                "CHANGE REQUEST: The retailer has acquired stores in Namibia (NAD) and Botswana (BWP), and "
                "historical CSV dumps now mix ZAR, NAD, and BWP with timestamps in different timezones. "
                "Adapt your aggregation logic to normalize multi-currency transactions using daily FX rates."
            ),
            passing_score=70,
        )

        challenge_cyber = WorkProofChallenge(
            pathway_id=pathway_cyber.id,
            title="POPIA Breach Triage & Phishing Log Investigation",
            scenario=(
                "A Sandton digital bank's SOC alerts on a spike in `/api/auth/login` failures followed by "
                "unusual customer profile exports containing South African ID numbers. Under POPIA, you must "
                "parse the authentication logs, identify credential-stuffing IPs, and redact PII before "
                "exporting the incident report."
            ),
            build_prompt=(
                "Write a Python log-triage script that parses JSON auth logs, flags source IPs with >10 failed "
                "logins followed by a 200 OK within 5 minutes, and masks 13-digit SA ID numbers and emails "
                "using SHA-256 or partial redaction for POPIA compliance."
            ),
            explain_prompt=(
                "Explain how your detection threshold distinguishes normal forgotten-password retries from "
                "automated credential stuffing, and why PII masking is mandatory under POPIA Section 19 & 22 "
                "before sharing logs with third-party responders."
            ),
            adapt_prompt=(
                "CHANGE REQUEST: The attacker switches to distributed residential proxies (max 2 requests per IP) "
                "sharing a single custom User-Agent fingerprint and stolen JWT refresh tokens. Adapt your "
                "detection script to correlate by User-Agent/ASN and trigger automated JWT session revocation."
            ),
            passing_score=70,
        )

        challenge_qa = WorkProofChallenge(
            pathway_id=pathway_qa.id,
            title="EFT Payment Gateway Regression & API Test Suite",
            scenario=(
                "A Durban e-commerce platform integrating Instant EFT & PayShap suffered a production bug where "
                "clicking 'Pay Now' twice on a slow 3G connection double-debited customers or accepted negative "
                "ZAR amounts. You must build an automated Pytest regression suite."
            ),
            build_prompt=(
                "Write an automated `pytest` test suite covering `POST /api/v1/payments/eft` for happy-path ZAR "
                "settlement, negative/zero amount rejection, missing reference fields, and duplicate idempotency-key "
                "replay protection. Provide your GitHub repo and test code."
            ),
            explain_prompt=(
                "Explain how you applied Boundary Value Analysis (BVA) and Equivalence Partitioning to select your "
                "test cases, and why mocking external bank webhooks is essential for deterministic tests."
            ),
            adapt_prompt=(
                "CHANGE REQUEST: The engineering team wants your test suite to run on every Pull Request in GitHub "
                "Actions, fail the build if coverage drops below 80%, and automatically quarantine flaky network "
                "tests. Write the GitHub Actions workflow YAML and pytest configuration."
            ),
            passing_score=70,
        )

        challenge_devops = WorkProofChallenge(
            pathway_id=pathway_devops.id,
            title="Containerized Microservice & CI/CD Pipeline Recovery",
            scenario=(
                "A Johannesburg logistics startup deploys its Python tracking API manually via SSH. Image sizes "
                "exceed 1.2GB, containers run as `root`, and whenever a municipal power trip restarts the node, "
                "traffic routes to the container before the database connection pool is ready."
            ),
            build_prompt=(
                "Write a production-grade, multi-stage `Dockerfile` (using a slim/alpine base, non-root user, and "
                "`HEALTHCHECK`) along with a GitHub Actions workflow that lints, tests, and builds the container image."
            ),
            explain_prompt=(
                "Explain why running containers as a non-root user and separating build dependencies from runtime "
                "layers reduces attack surface and speeds up image pulls across South African cloud regions."
            ),
            adapt_prompt=(
                "CHANGE REQUEST: The team is migrating to Kubernetes (EKS/AKS) and experiencing 502 Bad Gateway "
                "errors during deployments. Write a Kubernetes `Deployment` manifest with `readinessProbe`, "
                "`livenessProbe`, resource limits, and a zero-downtime `RollingUpdate` strategy."
            ),
            passing_score=70,
        )

        challenge_mobile = WorkProofChallenge(
            pathway_id=pathway_mobile.id,
            title="Offline-First Spaza Field-Agent Inventory Sync",
            scenario=(
                "Field agents visiting spaza shops in KwaZulu-Natal and Limpopo record stock orders on mobile "
                "devices where cellular connectivity frequently drops between 3G and offline mode. Orders are "
                "currently lost whenever the app closes without signal."
            ),
            build_prompt=(
                "Implement an offline-first synchronization module (JavaScript/TypeScript or Python client logic) "
                "that persists stock orders to a local queue with a client-generated UUID, tracks sync state "
                "(`PENDING`, `SYNCED`, `FAILED`), and flushes queued records when connectivity returns."
            ),
            explain_prompt=(
                "Explain how client-generated UUIDs and idempotency keys prevent duplicate stock orders when "
                "a 2G connection drops mid-flight after the server has already committed the request."
            ),
            adapt_prompt=(
                "CHANGE REQUEST: Two field agents occasionally update the same spaza shop's stock count while "
                "offline, causing last-write-wins data loss, and battery drain is high from constant polling. "
                "Adapt your sync engine to use exponential backoff with jitter and vector/timestamp conflict resolution."
            ),
            passing_score=70,
        )

        challenge_bi = WorkProofChallenge(
            pathway_id=pathway_bi.id,
            title="Credit Risk Cohort & Arrears Warehouse Modelling",
            scenario=(
                "A micro-lender regulated under South Africa's National Credit Act (NCA) needs a monthly vintage "
                "arrears report showing 30-, 60-, and 90-day delinquency rates across provinces and income bands "
                "from raw loan repayment ledger tables."
            ),
            build_prompt=(
                "Write a structured SQL query using Common Table Expressions (CTEs) and Window Functions (`SUM() OVER`, "
                "`ROW_NUMBER()`) that joins `loans`, `repayments`, and `customers` to classify accounts into Current, "
                "30-DPD, 60-DPD, and 90+ DPD arrears buckets per origination month."
            ),
            explain_prompt=(
                "Explain why CTEs and window functions outperform correlated subqueries on multi-million-row ledger "
                "tables, and how you handled customers with zero repayment rows (`LEFT JOIN` + `COALESCE`)."
            ),
            adapt_prompt=(
                "CHANGE REQUEST: Executive dashboards in Power BI are timing out because the query scans 5 years of "
                "historical ledger rows on every refresh. Redesign the target into an incremental Star Schema "
                "(`fact_loan_snapshots` + `dim_customer` SCD Type 2) with partitioning and composite indexes."
            ),
            passing_score=70,
        )

        challenge_frontend = WorkProofChallenge(
            pathway_id=pathway_frontend.id,
            title="Low-Bandwidth Accessible e-Government Portal",
            scenario=(
                "A provincial clinic appointment booking portal suffers a 65% drop-off rate among mobile users on "
                "prepaid data bundles and fails WCAG 2.1 AA accessibility audits for visually impaired citizens "
                "using screen readers."
            ),
            build_prompt=(
                "Build a semantic, accessible appointment booking form component (HTML5 + Vanilla JS/Tailwind) "
                "featuring proper `<label>`, `aria-live` validation error announcements, keyboard focus management, "
                "and South African ID / mobile number client-side validation."
            ),
            explain_prompt=(
                "Explain how your semantic markup, ARIA attributes, and color-contrast choices satisfy WCAG 2.1 AA, "
                "and why avoiding heavy third-party JS bundles is critical for users on costly prepaid mobile data."
            ),
            adapt_prompt=(
                "CHANGE REQUEST: Users frequently lose their form inputs when their browser tab refreshes on low-memory "
                "devices, and clinics require instant switching between English, isiZulu, and Afrikaans labels. "
                "Adapt your component to auto-save draft state in `localStorage` and support dynamic i18n dictionary switching."
            ),
            passing_score=70,
        )

        db.session.add_all([
            challenge_dev, challenge_cloud, challenge_data, challenge_cyber, challenge_qa,
            challenge_devops, challenge_mobile, challenge_bi, challenge_frontend,
        ])
        db.session.flush()

        all_challenges = [challenge_dev, challenge_cloud, challenge_data, challenge_cyber, challenge_qa, challenge_devops, challenge_mobile, challenge_bi, challenge_frontend]

        # ---------------------------------------------------------------------
        # 3. Create Specific Demo Candidates & Employers
        # ---------------------------------------------------------------------
        cand_sipho = User(email="sipho.dlamini@richfield.ac.za", full_name="Sipho Dlamini", role="candidate", institution="Richfield Graduate Institute of Technology", graduation_year=2026, location="Johannesburg", is_open_to_work=True)
        cand_sipho.set_password("password123")

        cand_zanele = User(email="zanele.khumalo@wits.ac.za", full_name="Zanele Khumalo", role="candidate", institution="University of the Witwatersrand (Wits)", graduation_year=2026, location="Cape Town", is_open_to_work=True)
        cand_zanele.set_password("password123")

        cand_thabo = User(email="thabo.nkosi@uct.ac.za", full_name="Thabo Nkosi", role="candidate", institution="University of Cape Town (UCT)", graduation_year=2026, location="Cape Town", is_open_to_work=True)
        cand_thabo.set_password("password123")

        cand_pieter = User(email="pieter.vdm@sun.ac.za", full_name="Pieter van der Merwe", role="candidate", institution="Stellenbosch University", graduation_year=2026, location="Stellenbosch", is_open_to_work=False)
        cand_pieter.set_password("password123")

        cand_ayanda = User(email="ayanda.zulu@dut.ac.za", full_name="Ayanda Zulu", role="candidate", institution="Durban University of Technology (DUT)", graduation_year=2026, location="Durban", is_open_to_work=True)
        cand_ayanda.set_password("password123")

        cand_amahle = User(email="amahle.ndlovu@ukzn.ac.za", full_name="Amahle Ndlovu", role="candidate", institution="University of KwaZulu-Natal (UKZN)", graduation_year=2026, location="Durban", is_open_to_work=True)
        cand_amahle.set_password("password123")

        cand_kabelo = User(email="kabelo.mahlangu@uj.ac.za", full_name="Kabelo Mahlangu", role="candidate", institution="University of Johannesburg (UJ)", graduation_year=2026, location="Johannesburg", is_open_to_work=True)
        cand_kabelo.set_password("password123")

        cand_lerato = User(email="lerato.mokoena@tut.ac.za", full_name="Lerato Mokoena", role="candidate", institution="Tshwane University of Technology (TUT)", graduation_year=2026, location="Pretoria", is_open_to_work=True)
        cand_lerato.set_password("password123")

        employer_payflow = User(email="talent@paystack-sa.co.za", full_name="Nomsa Dlamini (Tech Recruiter)", role="employer", institution="PayFlow FinTech SA", location="Johannesburg")
        employer_payflow.set_password("password123")

        employer_cloud = User(email="careers@cloudsmiths.co.za", full_name="Gareth Naidoo (Engineering Manager)", role="employer", institution="CloudSmiths South Africa", location="Cape Town")
        employer_cloud.set_password("password123")

        # NEW: Additional Employers for the massive dataset
        employer_takealot = User(email="techjobs@takealot.com", full_name="Sarah Jenkins", role="employer", institution="Takealot", location="Cape Town")
        employer_takealot.set_password("password123")
        
        employer_standardbank = User(email="careers@standardbank.co.za", full_name="Thabo Mokoena", role="employer", institution="Standard Bank", location="Johannesburg")
        employer_standardbank.set_password("password123")

        db.session.add_all([
            cand_sipho, cand_zanele, cand_thabo, cand_pieter, cand_ayanda, cand_amahle, cand_kabelo, cand_lerato,
            employer_payflow, employer_cloud, employer_takealot, employer_standardbank
        ])
        db.session.flush()

        employers_list = [employer_payflow, employer_cloud, employer_takealot, employer_standardbank]

        # ---------------------------------------------------------------------
        # 4. Seed Specific Submissions & Passports (For the Demo Accounts)
        # ---------------------------------------------------------------------
        now = datetime.now(timezone.utc)

        sipho_sub_dev = WorkProofSubmission(
            user_id=cand_sipho.id, challenge_id=challenge_dev.id, build_repo_url="https://github.com/sipho-dlamini/fintech-voucher-service",
            build_code_snippet="@voucher_bp.route('/api/v1/vouchers/redeem', methods=['POST'])\ndef redeem_voucher():\n    # ... production code ...",
            explain_notes="Used pessimistic row-level locking (`with_for_update`) inside an atomic transaction to guarantee idempotency.",
            adapt_solution="Implemented cursor-based pagination and a Redis sliding-window rate limiter.",
            status="verified", evidence_score=94, readiness_feedback="Score Breakdown — Build: 38/40 | Explain: 28/30 | Adapt: 28/30.",
            next_best_action="You have achieved Trust Level 5 (Employer Verified).", completed_at=now
        )

        sipho_passport = SkillsPassport(
            user_id=cand_sipho.id, readiness_score=94, highest_trust_level=5,
            verified_skills_json=json.dumps([{
                "pathway": "Junior Software Developer", "challenge_title": "RESTful API & Bug Resolution", "score": 94, "trust_level": 5,
                "skills": ["RESTful API Implementation", "Payload Validation", "Database Concurrency", "Rate-Limiting"],
                "verified_at": "2026-10-20"
            }])
        )

        zanele_sub = WorkProofSubmission(
            user_id=cand_zanele.id, challenge_id=challenge_data.id, build_repo_url="https://github.com/zanele-khumalo/data-pipeline",
            build_code_snippet="import pandas as pd\n# ... pandas logic ...",
            explain_notes="I chose category-level median imputation over global mean because retail unit prices are right-skewed.",
            adapt_solution="Normalized timestamps to UTC and performed a left merge against daily FX rates.",
            status="verified", evidence_score=89, readiness_feedback="Score Breakdown — Build: 36/40 | Explain: 27/30 | Adapt: 26/30.",
            next_best_action="Share your Level 4 Verified Data & BI Passport.", completed_at=now
        )

        zanele_passport = SkillsPassport(
            user_id=cand_zanele.id, readiness_score=89, highest_trust_level=4,
            verified_skills_json=json.dumps([{
                "pathway": "Junior Data Analyst", "challenge_title": "Retail Sales Data Cleaning", "score": 89, "trust_level": 4,
                "skills": ["Data Cleaning", "Statistical Imputation", "Pandas", "KPI Aggregation"],
                "verified_at": "2026-10-21"
            }])
        )

        # Add the rest of the specific demo submissions for Thabo, Pieter, etc.
        thabo_passport = SkillsPassport(user_id=cand_thabo.id, readiness_score=86, highest_trust_level=4, verified_skills_json=json.dumps([{"pathway": "Junior Software Developer", "skills": ["RESTful API Implementation", "Database Concurrency"]}]))
        pieter_passport = SkillsPassport(user_id=cand_pieter.id, readiness_score=84, highest_trust_level=4, verified_skills_json=json.dumps([{"pathway": "Cybersecurity", "skills": ["POPIA PII Masking", "SIEM Log Parsing"]}]))
        ayanda_passport = SkillsPassport(user_id=cand_ayanda.id, readiness_score=81, highest_trust_level=4, verified_skills_json=json.dumps([{"pathway": "Mobile Dev", "skills": ["Offline-First", "Idempotent Sync"]}]))
        amahle_passport = SkillsPassport(user_id=cand_amahle.id, readiness_score=65, highest_trust_level=3, verified_skills_json=json.dumps([]))
        kabelo_passport = SkillsPassport(user_id=cand_kabelo.id, readiness_score=54, highest_trust_level=2, verified_skills_json=json.dumps([]))
        lerato_passport = SkillsPassport(user_id=cand_lerato.id, readiness_score=20, highest_trust_level=1, verified_skills_json=json.dumps([]))

        db.session.add_all([
            sipho_sub_dev, sipho_passport, zanele_sub, zanele_passport,
            thabo_passport, pieter_passport, ayanda_passport, amahle_passport, kabelo_passport, lerato_passport
        ])
        db.session.flush()


        # ---------------------------------------------------------------------
        # 5. GENERATE 200 FAKE CANDIDATES & 100+ APPLICATIONS (MASSIVE DATASET)
        # ---------------------------------------------------------------------
        print("Generating 200 fake candidates and simulated applications...")
        
        sa_locations = ["Johannesburg", "Cape Town", "Durban", "Pretoria", "Port Elizabeth", "Bloemfontein", "Remote", "Stellenbosch", "Soweto", "Sandton"]
        sa_institutions = ["Wits", "UCT", "UJ", "TUT", "DUT", "Stellenbosch University", "UP", "UNISA", "Rhodes", "UKZN", "CPUT", "VUT"]
        tech_skills = ["Python", "Java", "C#", "JavaScript", "React", "SQL", "Docker", "Kubernetes", "AWS", "Azure", "Linux", "Flask", "Django", "REST APIs", "CI/CD", "Git", "Agile", "HTML/CSS", "Node.js", "Spring Boot"]

        fake_candidates = []
        fake_passports = []
        fake_submissions = []
        fake_shortlists = []

        for _ in range(200):
            # 1. Create the User
            fake_name = fake.name()
            fake_email = f"{fake_name.replace(' ', '').lower()}_{random.randint(1,99)}@example.com"
            
            cand = User(
                email=fake_email,
                full_name=fake_name,
                role="candidate",
                institution=random.choice(sa_institutions),
                graduation_year=random.randint(2021, 2026),
                location=random.choice(sa_locations),
                is_open_to_work=random.choice([True, True, True, False]) # 75% chance they are open
            )
            cand.set_password("password123")
            fake_candidates.append(cand)
            db.session.add(cand)
            db.session.flush() # Get the ID

            # 2. Create their Skills Passport
            trust = random.randint(1, 5)
            score = random.randint(10, 98)
            
            # Assign 3 to 6 random skills
            assigned_skills = random.sample(tech_skills, random.randint(3, 6))
            
            # Randomly assign them to one of the 9 pathways
            random_pathway = random.choice([pathway_dev, pathway_cloud, pathway_data, pathway_cyber, pathway_qa, pathway_devops, pathway_mobile, pathway_bi, pathway_frontend])

            passport = SkillsPassport(
                user_id=cand.id,
                readiness_score=score,
                highest_trust_level=trust,
                verified_skills_json=json.dumps([{
                    "pathway": random_pathway.title,
                    "challenge_title": f"{random_pathway.title} Assessment",
                    "score": score,
                    "trust_level": trust,
                    "skills": assigned_skills,
                    "verified_at": datetime.now().strftime("%Y-%m-%d")
                }]) if trust > 1 else json.dumps([])
            )
            fake_passports.append(passport)
            db.session.add(passport)

            # 3. Create a WorkProof Submission for them (if they are Level 3+)
            if trust >= 3:
                random_challenge = random.choice(all_challenges)
                sub = WorkProofSubmission(
                    user_id=cand.id,
                    challenge_id=random_challenge.id,
                    status="verified" if trust >= 4 else "submitted",
                    evidence_score=score,
                    build_repo_url=f"https://github.com/{fake_name.replace(' ', '').lower()}/project",
                    build_code_snippet="// Simulated code submission",
                    explain_notes="I chose this architecture because it is scalable.",
                    adapt_solution="Added Redis cache to handle the load.",
                    readiness_feedback="The AI evaluated this submission and found it to be solid.",
                    completed_at=now
                )
                fake_submissions.append(sub)
                db.session.add(sub)

                # 4. Simulate Applications (Shortlists) for the good candidates
                if random.random() < 0.8: # 80% of good candidates applied somewhere
                    emp = random.choice(employers_list)
                    
                    sl = EmployerShortlist(
                        employer_id=emp.id,
                        candidate_id=cand.id,
                        notes=random.choice([
                            "Strong technical skills, good culture fit.",
                            "Excellent explanation of their code. Moving to interview.",
                            "Good database knowledge, weak frontend. Suitable for backend.",
                            "Highly recommended for the Cloud team.",
                            "Needs a bit of mentoring, but shows great potential."
                        ]),
                        status=random.choice(["shortlisted", "invited", "rejected"])
                    )
                    fake_shortlists.append(sl)
                    db.session.add(sl)

        # Add some specific shortlists for your main demo accounts so they show up in the pipeline
        shortlist_1 = EmployerShortlist(employer_id=employer_payflow.id, candidate_id=cand_sipho.id, notes="Endorsed to Trust Level 5!", status="invited")
        shortlist_2 = EmployerShortlist(employer_id=employer_takealot.id, candidate_id=cand_zanele.id, notes="Top Data candidate.", status="shortlisted")
        shortlist_3 = EmployerShortlist(employer_id=employer_standardbank.id, candidate_id=cand_zanele.id, notes="Great SQL skills.", status="shortlisted")
        
        db.session.add_all([shortlist_1, shortlist_2, shortlist_3])

        db.session.commit()

        print("=========================================================================")
        print("✅ MASSIVE DATABASE SEEDED SUCCESSFULLY!")
        print("-------------------------------------------------------------------------")
        print(f"Created 9 IT Pathways (Departments)")
        print(f"Created 4 Employers (PayFlow, CloudSmiths, Takealot, Standard Bank)")
        print(f"Created 8 Specific Demo Candidates + 200 Generated Candidates = 208 Total")
        print(f"Generated {len(fake_shortlists) + 3} 'Applications' (Employer Shortlists)")
        print("-------------------------------------------------------------------------")
        print("To log in as an employer:")
        print("Email: talent@paystack-sa.co.za | Password: password123")
        print("=========================================================================")


if __name__ == "__main__":
    seed_database()