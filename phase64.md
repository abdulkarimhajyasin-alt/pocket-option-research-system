# Phase 64 — Repository Hygiene & Artifact Retention Policy

You are now implementing Phase 64 — Repository Hygiene & Artifact Retention Policy.

CRITICAL RULES

This phase is REPOSITORY-HYGIENE-ONLY and ARTIFACT-POLICY-ONLY.

This phase does NOT implement trading, execution, broker integration, Pocket Option connectivity, browser automation, authentication, credentials, login, real account access, money handling, or real operational control over any external system.

DO NOT add:
- Broker APIs
- Broker adapters
- Pocket Option login
- Credential handling
- Browser automation
- Selenium
- Playwright
- Order placement
- Execution engines
- Live trading
- Money handling
- Account monitoring
- Deposits
- Withdrawals
- External connectivity
- Real execution gateways
- Real broker sessions
- Real production control plane
- Real user authentication
- Real approval workflow connected to external systems
- Any code that can interact with a real broker or real account

This phase must remain STRICTLY REPOSITORY-HYGIENE-ONLY, ARTIFACT-POLICY-ONLY, GOVERNANCE-ONLY, DESIGN-ONLY, ARCHITECTURE-ONLY, LOCAL-ONLY, and RESEARCH-ONLY.

====================================================
PHASE 64 — REPOSITORY HYGIENE & ARTIFACT RETENTION POLICY
=========================================================

OBJECTIVE

Create a formal repository hygiene and artifact retention policy layer.

Phase 63 revealed that validation generated untracked research archive snapshot/diff artifacts and Windows denied cleanup attempts.

Phase 64 must define and implement safe local repository hygiene inspection, generated artifact inventory, retention policy, ignore recommendations, cleanup planning, and dashboard/API reporting.

This phase must NOT delete files automatically.

This phase must NOT rewrite previous generated artifacts.

This phase must NOT alter research formulas, trading logic, paper logic, certification scoring, or safety boundaries.

The goal is to document and manage:
- generated artifact inventory
- tracked vs untracked artifact classification
- stale artifact detection
- duplicate artifact detection
- archive retention policy
- report retention policy
- storage retention policy
- cleanup plan
- .gitignore recommendation report
- Windows cleanup limitation notes
- release hygiene score
- repository hygiene readiness

====================================================
CURRENT CONTEXT
===============

The project has completed:

- Research Platform v1.0
- Phase 56 — Post-Research Strategic Architecture
- Phase 57 — Trading System Architecture Program Foundation
- Phase 58 — Trading Requirements & Constraints Specification
- Phase 59 — Production System Design Blueprint
- Phase 60 — Operational Governance & Control Framework
- Phase 61 — Governance Traceability & Control Mapping
- Phase 62 — Control Assurance & Review Readiness
- Phase 63 — Review Board Simulation & Decision Gate Dry Run

Current Phase 63 known limitation:

Validation generated untracked research archive snapshot/diff artifacts unrelated to Phase 63. Codex restored tracked report/storage churn, but Windows denied cleanup of the untracked archive files despite approved removal attempts. They remain visible in git status.

Phase 64 must address this through policy, inventory, diagnostics, and safe cleanup planning only.

====================================================
ARCHITECTURE
============

Create a new module:

app/repository_hygiene/

Required files:
- __init__.py
- models.py
- schemas.py
- git_status_parser.py
- artifact_inventory.py
- retention_policy.py
- cleanup_planner.py
- ignore_recommendations.py
- duplicate_detection.py
- stale_detection.py
- archive_policy.py
- report_policy.py
- storage_policy.py
- hygiene_scoring.py
- diagnostics.py
- recommendations.py
- storage.py
- reports.py
- service.py

Create scripts:
- scripts/run_repository_hygiene.py
- scripts/check_repository_hygiene.py

Create tests:
- tests/test_repository_hygiene.py

Create dashboard page:
- app/templates/dashboard/repository_hygiene.html

Update dashboard integration only as needed:
- app/dashboard/routes.py
- app/dashboard/analytics.py
- app/dashboard/actions.py
- app/templates/dashboard/base.html
- app/i18n/ar.py

====================================================
HYGIENE SOURCES
===============

Inspect local project structure only.

Allowed local sources:
- git status output if safely available
- reports/
- storage/
- scripts/
- tests/
- app/
- phase*.md files
- .gitignore if present
- pyproject.toml if present
- README.md if present

Do not call external services.
Do not delete files.
Do not run destructive git commands.
Do not run git clean.
Do not reset or checkout files.
Do not modify .gitignore automatically unless explicitly required by tests; instead generate recommendations.

====================================================
CORE CATEGORIES
===============

Implement the following repository-hygiene-only categories:

1. Git Status Inventory

Detect and classify:
- tracked modified files
- deleted files
- untracked files
- generated report changes
- generated storage changes
- prompt files
- cache files
- archive snapshots
- diff artifacts

2. Generated Artifact Inventory

Inventory:
- reports/
- storage/
- archive snapshots
- generated summaries
- diagnostics reports
- recommendations reports
- release artifacts
- certification artifacts
- dashboard generated data

3. Artifact Classification

Classify artifacts as:
- source-controlled candidate
- generated disposable
- generated retained
- release artifact
- archive artifact
- prompt artifact
- cache artifact
- unknown

4. Retention Policy

Define retention rules for:
- research archive snapshots
- latest snapshots
- diffs
- release reports
- certification reports
- dashboard reports
- diagnostics reports
- validation artifacts
- prompt files
- temporary files

5. Cleanup Plan

Generate a safe cleanup plan with:
- file path
- classification
- recommended action
- safety level
- requires_manual_review
- reason
- windows_note if applicable

Allowed recommended actions:
- keep
- review manually
- add to ignore recommendation
- archive externally
- eligible for manual cleanup
- do not delete automatically

No automatic deletion.

6. Ignore Recommendations

Generate .gitignore recommendations only.

Do not modify .gitignore automatically unless current project conventions already do so safely.

7. Duplicate Detection

Detect duplicate report/storage filenames across domains.

Do not delete duplicates.

8. Stale Artifact Detection

Detect stale artifacts based on naming/version patterns and generated timestamps if available.

Do not delete stale artifacts.

9. Archive Retention Policy

Define how many archive snapshots should be retained locally and which should be preserved as release evidence.

10. Hygiene Scoring

Calculate:
- git status cleanliness score
- artifact classification score
- retention policy coverage score
- cleanup plan completeness score
- ignore recommendation score
- overall repository hygiene score

====================================================
CORE MODELS
===========

Create models for:
- GitStatusItem
- ArtifactInventoryItem
- ArtifactClassification
- RetentionRule
- CleanupPlanItem
- IgnoreRecommendation
- DuplicateArtifactFinding
- StaleArtifactFinding
- ArchiveRetentionRule
- HygieneScorecard
- RepositoryHygieneSummary
- RepositoryHygieneDiagnostic
- RepositoryHygieneRecommendation

Each cleanup plan item should include:
- item_id
- path
- classification
- recommended_action
- safety_level
- requires_manual_review
- reason
- windows_note
- destructive_action_forbidden

Safety levels:
- آمن
- يحتاج مراجعة
- حساس
- ممنوع تلقائياً

====================================================
ENGINES
=======

Create these engines:

1. GitStatusParser

Responsibilities:
- safely read git status --porcelain if git is available
- parse status lines
- classify status entries
- handle git unavailable gracefully
- never mutate repository state

2. ArtifactInventoryEngine

Responsibilities:
- inventory reports and storage artifacts
- classify generated artifact families
- identify archive snapshots and diffs
- identify prompt files
- identify cache/temp files
- build inventory summary

3. RetentionPolicyEngine

Responsibilities:
- define retention rules
- map artifact types to retention rules
- define manual review requirements
- define release evidence preservation rules

4. CleanupPlanner

Responsibilities:
- generate non-destructive cleanup plan
- flag manual review items
- identify Windows cleanup risk notes
- avoid automatic deletion

5. IgnoreRecommendationEngine

Responsibilities:
- inspect current ignore patterns when available
- generate recommended ignore additions
- avoid modifying .gitignore automatically
- classify recommendations by confidence

6. HygieneScoringEngine

Responsibilities:
- score repository hygiene
- score artifact policy coverage
- score cleanup plan completeness
- score retention coverage
- produce hygiene scorecard

====================================================
DIAGNOSTICS
===========

Create:

RepositoryHygieneDiagnostics

Detect:
- untracked generated artifacts
- deleted phase prompt files
- modified generated reports
- modified generated storage files
- duplicate generated artifact names
- stale archive snapshots
- missing retention policy
- missing cleanup plan
- missing ignore recommendations
- git unavailable
- Windows cleanup limitation
- unsafe wording
- implementation artifacts outside hygiene scope
- broker/execution/trading capability introduction
- missing Arabic labels
- missing dashboard/API integration

Severity:
- مرتفع
- متوسط
- منخفض

====================================================
RECOMMENDATIONS
===============

Generate Arabic recommendations for:
- مراجعة الملفات غير المتتبعة
- تثبيت سياسة الاحتفاظ بالأرشيف
- عدم حذف الملفات تلقائياً
- مراجعة ملفات phase المحذوفة
- إضافة قواعد تجاهل للملفات المؤقتة
- تقليل تضخم reports و storage
- حفظ أدلة الإصدار المهمة
- تنظيف يدوي آمن بعد المراجعة
- توثيق قيود Windows في التنظيف
- الحفاظ على حدود البحث فقط

====================================================
SERVICE LAYER
=============

Create:

RepositoryHygieneService

Must provide:
- parse_git_status()
- build_artifact_inventory()
- classify_artifacts()
- build_retention_policy()
- build_cleanup_plan()
- build_ignore_recommendations()
- detect_duplicates()
- detect_stale_artifacts()
- build_archive_policy()
- build_scorecard()
- generate_diagnostics()
- generate_recommendations()
- run_full_repository_hygiene()
- get_summary()

The service must be deterministic, local-only, JSON-first, repository-hygiene-only, artifact-policy-only, non-destructive, and safe.

====================================================
DASHBOARD
=========

Add dashboard page:

/repository-hygiene

Arabic navigation label:

نظافة المستودع

Dashboard title:

نظافة المستودع وسياسة الاحتفاظ بالملفات

Display:
- حالة النظافة
- درجة النظافة العامة
- عدد الملفات غير المتتبعة
- عدد الملفات المعدلة
- عدد الملفات المحذوفة
- عدد artifacts المصنفة
- عدد عناصر خطة التنظيف
- عدد توصيات .gitignore
- عدد العناصر التي تحتاج مراجعة يدوية
- عدد التحذيرات
- التوصيات

The dashboard must clearly state:

هذه الصفحة فحص وتنظيم مستودع فقط ولا تحذف الملفات تلقائياً ولا تضيف تداولاً حقيقياً أو اتصالاً بوسيط.

====================================================
API ENDPOINTS
=============

Add safe local endpoints:
- /api/repository-hygiene
- /api/repository-hygiene/git-status
- /api/repository-hygiene/artifacts
- /api/repository-hygiene/retention-policy
- /api/repository-hygiene/cleanup-plan
- /api/repository-hygiene/ignore-recommendations
- /api/repository-hygiene/duplicates
- /api/repository-hygiene/stale
- /api/repository-hygiene/archive-policy
- /api/repository-hygiene/scorecard
- /api/repository-hygiene/diagnostics
- /api/repository-hygiene/recommendations

All endpoints must return local hygiene/planning data only.

No external calls.
No destructive actions.
No broker interaction.
No real operational control.

====================================================
CHARTS
======

Add Arabic dashboard-ready charts for:
- توزيع حالة Git
- تصنيف artifacts
- خطة التنظيف
- توصيات التجاهل
- العناصر المتكررة
- العناصر القديمة
- درجات النظافة
- التحذيرات
- التوصيات

Preserve current dashboard design and RTL Arabic style.

====================================================
STORAGE
=======

Create:

storage/repository_hygiene/

Generate:
- git_status_inventory.json
- artifact_inventory.json
- artifact_classification.json
- retention_policy.json
- cleanup_plan.json
- ignore_recommendations.json
- duplicate_artifacts.json
- stale_artifacts.json
- archive_policy.json
- scorecard.json
- diagnostics.json
- recommendations.json
- summary.json

====================================================
REPORTS
=======

Create:

reports/repository_hygiene/

Generate:
- repository_hygiene_summary.json
- git_status_inventory_report.json
- artifact_inventory_report.json
- artifact_classification_report.json
- retention_policy_report.json
- cleanup_plan_report.json
- ignore_recommendations_report.json
- duplicate_artifacts_report.json
- stale_artifacts_report.json
- archive_policy_report.json
- scorecard_report.json
- diagnostics_report.json
- recommendations_report.json

====================================================
SCRIPTS
=======

Create:

scripts/run_repository_hygiene.py
scripts/check_repository_hygiene.py

scripts/run_repository_hygiene.py must:
- parse git status if available
- inventory artifacts
- classify artifacts
- build retention policy
- build cleanup plan
- build ignore recommendations
- detect duplicates
- detect stale artifacts
- build archive policy
- build scorecard
- generate diagnostics
- generate recommendations
- write storage outputs
- write reports outputs

scripts/check_repository_hygiene.py must validate:
- app/repository_hygiene exists
- required module files exist
- required scripts exist
- required tests exist
- required dashboard template exists
- reports/repository_hygiene outputs exist
- storage/repository_hygiene outputs exist
- JSON outputs are valid
- summary confirms repository-hygiene-only
- summary confirms artifact-policy-only
- summary confirms non-destructive
- no destructive cleanup actions are performed
- no broker/execution/browser/auth/money-handling capability was introduced
- dashboard route exists
- API routes exist
- Arabic labels exist

====================================================
TESTING
=======

Create:

tests/test_repository_hygiene.py

Tests must verify:
- git status parser handles sample porcelain output
- git status parser handles unavailable git gracefully
- artifact inventory works
- artifact classification works
- retention policy generation works
- cleanup plan is non-destructive
- ignore recommendations are recommendations only
- duplicate detection works
- stale detection works
- archive policy generation works
- scorecard generation works
- diagnostics detect unsafe/destructive wording
- recommendations are Arabic
- dashboard endpoints work
- API endpoints work
- generated JSON files are valid
- safety boundary remains intact
- no broker/execution/browser/auth/money-handling capability exists in repository_hygiene module

====================================================
VALIDATION
==========

Run:

python -m compileall app
python -m pytest -q
python -m flake8 app

python scripts/check_repository_hygiene.py

Also run available existing validation suites for:
- review board simulation
- control assurance
- governance traceability
- operational governance
- production system design
- trading requirements
- trading architecture program
- post-research architecture
- release packaging
- platform certification
- research archive
- research API
- knowledge graph
- architecture audit
- dashboard
- dashboard UX
- Arabic dashboard
- safety
- readiness
- observation
- signal stream
- paper modules

If some validation script does not exist, mention it clearly and continue with available validations.

====================================================
IMPLEMENTATION RULES
====================

Preserve all existing architecture.
Preserve all existing dashboards.
Preserve all existing APIs.

Extend only with repository hygiene and artifact retention policy.

Do not add trading features.
Do not add execution code.
Do not add broker access.
Do not add live trading.
Do not add automation.
Do not add external connectivity.
Do not add real authentication.
Do not add real permissions.
Do not delete files automatically.
Do not run destructive git commands.
Do not modify signal formulas.
Do not modify paper trading logic.
Do not modify certification scoring.
Do not delete existing release artifacts.

====================================================
QUALITY RULES
=============

The implementation must be deterministic, local-only, JSON-first, dashboard-friendly, Arabic-first, backward-compatible, production-structured, repository-hygiene-only, artifact-policy-only, non-destructive, safe, and roadmap-oriented.

Handle missing prior outputs gracefully.

Do not fail catastrophically if optional reports are absent.

====================================================
DELIVERABLE FORMAT
==================

Return:

1. Phase 64 Implementation Summary
2. Changed Files
3. Repository Hygiene Layer
4. Git Status Inventory
5. Artifact Inventory
6. Artifact Classification
7. Retention Policy
8. Cleanup Plan
9. Ignore Recommendations
10. Duplicate Detection
11. Stale Detection
12. Archive Policy
13. Hygiene Scorecard
14. Dashboard Additions
15. API Endpoints Added
16. Reports Generated
17. Storage Generated
18. Safety Boundary Confirmation
19. Strategic Recommendation
20. Validation Results
21. Known Limitations
22. Worktree Notes
23. Git Commands

Git Commands:

git add .
git commit -m "Add repository hygiene retention policy"
git push origin main
