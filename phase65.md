# Phase 65 — Release Baseline Reconciliation & Manual Cleanup Plan

You are now implementing Phase 65 — Release Baseline Reconciliation & Manual Cleanup Plan.

CRITICAL RULES

This phase is BASELINE-RECONCILIATION-ONLY and MANUAL-CLEANUP-PLANNING-ONLY.

This phase does NOT implement trading.

This phase does NOT implement execution.

This phase does NOT implement broker integration.

This phase does NOT implement Pocket Option connectivity.

This phase does NOT implement browser automation.

This phase does NOT implement authentication, credentials, login, real account access, or money handling.

This phase does NOT implement real operational control over any external system.

This phase must NOT delete files automatically.

This phase must NOT run destructive git commands.

This phase must NOT rewrite previous phase outputs unless explicitly generating its own reconciliation reports/storage.

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

This phase must remain STRICTLY BASELINE-RECONCILIATION-ONLY, MANUAL-CLEANUP-PLANNING-ONLY, REPOSITORY-HYGIENE-ONLY, ARTIFACT-POLICY-ONLY, GOVERNANCE-ONLY, DESIGN-ONLY, ARCHITECTURE-ONLY, LOCAL-ONLY, and RESEARCH-ONLY.

====================================================
PHASE 65 — RELEASE BASELINE RECONCILIATION & MANUAL CLEANUP PLAN
===============================================================

OBJECTIVE

Create a formal release baseline reconciliation layer that uses Phase 64 repository hygiene outputs to produce a safe human-reviewable baseline decision package.

Phase 64 identified repository churn and generated artifact complexity.

Phase 65 must decide, by classification and recommendation only, what should be committed, what should be reviewed manually, what should be ignored, what should be retained as release evidence, and what should be kept out of the release baseline.

This phase must NOT perform cleanup automatically.

This phase must NOT modify .gitignore automatically.

This phase must NOT delete, restore, reset, checkout, or clean files.

The goal is to document and manage:

- release baseline inventory
- commit candidate classification
- generated artifact reconciliation
- manual cleanup checklist
- release evidence selection
- ignore rule proposal review
- phase prompt file handling
- validation artifact handling
- archive artifact handling
- report/storage churn decision matrix
- baseline readiness score
- final human action checklist

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
- Phase 64 — Repository Hygiene & Artifact Retention Policy

Current Phase 64 findings:

- Hygiene status: مقبول
- Overall hygiene score: 74.0
- Untracked files: 8
- Modified files: 98
- Cleanup plan items: 855
- Manual review items: 828
- Diagnostics: 95

Phase 65 must turn these findings into a clear baseline reconciliation package.

====================================================
ARCHITECTURE
============

Create a new module:

app/release_baseline/

Required files:
- __init__.py
- models.py
- schemas.py
- source_loader.py
- baseline_inventory.py
- commit_classification.py
- artifact_reconciliation.py
- evidence_selection.py
- cleanup_checklist.py
- ignore_review.py
- prompt_file_policy.py
- validation_churn.py
- archive_reconciliation.py
- decision_matrix.py
- baseline_scoring.py
- diagnostics.py
- recommendations.py
- storage.py
- reports.py
- service.py

Create scripts:
- scripts/run_release_baseline.py
- scripts/check_release_baseline.py

Create tests:
- tests/test_release_baseline.py

Create dashboard page:
- app/templates/dashboard/release_baseline.html

Update dashboard integration only as needed:
- app/dashboard/routes.py
- app/dashboard/analytics.py
- app/dashboard/actions.py
- app/templates/dashboard/base.html
- app/i18n/ar.py

====================================================
BASELINE SOURCES
================

Consume local JSON outputs only from:

- storage/repository_hygiene/
- reports/repository_hygiene/
- storage/release_packaging/
- reports/release_packaging/
- storage/platform_certification/
- reports/platform_certification/
- storage/review_board_simulation/
- reports/review_board_simulation/

Allowed direct local inspection:

- git status output if safely available
- reports/
- storage/
- phase*.md files
- .gitignore if present
- README.md if present

Do not call external services.

Do not delete files.

Do not run destructive git commands.

Do not run git clean.

Do not reset or checkout files.

Do not modify .gitignore automatically.

====================================================
CORE CATEGORIES
===============

Implement the following baseline-reconciliation-only categories:

1. Release Baseline Inventory

Build a full inventory of files relevant to the next commit baseline:

- source files
- dashboard files
- tests
- scripts
- generated reports
- generated storage files
- phase prompt files
- archive snapshots
- diff artifacts
- release evidence artifacts
- untracked artifacts
- modified artifacts
- deleted prompt files

2. Commit Candidate Classification

Classify files as:

- commit recommended
- commit after review
- keep uncommitted
- ignore recommended
- retain as release evidence
- manual cleanup candidate
- manual decision required
- excluded from baseline

3. Generated Artifact Reconciliation

Reconcile generated report/storage artifacts:

- which generated outputs belong to the current phase
- which outputs are validation churn
- which outputs are release evidence
- which outputs are archive evidence
- which outputs are transient
- which outputs need manual review

4. Release Evidence Selection

Identify files that should likely remain committed as release evidence:

- release manifests
- certification reports
- platform summaries
- baseline reports
- governance reports
- safety reports
- final readiness reports

5. Manual Cleanup Checklist

Generate a safe human checklist.

Each checklist item must include:

- path
- issue
- recommended action
- reason
- safety level
- command suggestion if safe
- destructive_action_forbidden
- requires_human_confirmation

Allowed action labels:

- review
- keep
- commit
- ignore proposal
- manual cleanup candidate
- archive externally
- do not touch

No cleanup execution.

6. Ignore Review

Generate .gitignore review proposal only.

Do not edit .gitignore automatically.

Classify proposed ignore rules as:

- high confidence
- medium confidence
- low confidence
- requires human decision

7. Phase Prompt File Policy

Define handling rules for phase prompt files:

- whether phase*.md should be committed
- whether deleted phase files are expected
- whether current phase prompt should remain untracked
- whether prompt files should be archived externally

Do not delete phase prompt files.

8. Validation Churn Analysis

Analyze files likely modified because of validation runs.

Classify:

- expected validation churn
- suspicious churn
- release evidence churn
- disposable churn
- manual review required

9. Archive Reconciliation

Analyze research archive snapshots/diffs.

Classify:

- latest archive snapshot
- release evidence snapshot
- stale snapshot
- transient diff
- manual cleanup candidate

No automatic deletion.

10. Decision Matrix

Generate a human-readable decision matrix:

- file category
- risk
- recommended handling
- commit recommendation
- cleanup recommendation
- ignore recommendation
- evidence value

11. Baseline Scoring

Calculate:

- baseline clarity score
- commit readiness score
- artifact reconciliation score
- manual cleanup readiness score
- evidence selection score
- ignore review score
- overall baseline readiness score

====================================================
CORE MODELS
===========

Create models for:

- BaselineInventoryItem
- CommitClassification
- ArtifactReconciliationItem
- ReleaseEvidenceItem
- CleanupChecklistItem
- IgnoreReviewItem
- PromptFilePolicyItem
- ValidationChurnItem
- ArchiveReconciliationItem
- BaselineDecisionMatrixItem
- BaselineScorecard
- ReleaseBaselineSummary
- ReleaseBaselineDiagnostic
- ReleaseBaselineRecommendation

Each checklist item should include:

- item_id
- path
- issue
- recommended_action
- reason
- safety_level
- command_suggestion
- destructive_action_forbidden
- requires_human_confirmation

Safety levels:

- آمن
- يحتاج مراجعة
- حساس
- ممنوع تلقائياً

====================================================
ENGINES
=======

Create these engines:

1. BaselineSourceLoader

Responsibilities:
- load Phase 64 hygiene outputs
- load release packaging outputs
- load certification outputs
- load review simulation outputs when available
- safely read git status if available
- handle missing files gracefully

2. BaselineInventoryEngine

Responsibilities:
- build release baseline inventory
- classify artifact families
- identify current phase artifacts
- identify validation churn families
- identify prompt files and archive files

3. CommitClassificationEngine

Responsibilities:
- classify commit candidates
- classify manual review candidates
- classify release evidence
- classify ignore candidates
- classify cleanup candidates

4. ArtifactReconciliationEngine

Responsibilities:
- reconcile generated reports/storage
- identify validation churn
- identify current phase outputs
- identify release evidence outputs
- identify archive snapshot/diff outputs

5. EvidenceSelectionEngine

Responsibilities:
- select likely release evidence files
- explain evidence value
- avoid automatic commit decisions
- flag human review needs

6. ManualCleanupChecklistEngine

Responsibilities:
- create non-destructive checklist
- include safe command suggestions only when applicable
- mark destructive actions forbidden
- require human confirmation for cleanup

7. IgnoreReviewEngine

Responsibilities:
- inspect current ignore recommendations
- generate .gitignore review proposal
- avoid editing .gitignore automatically

8. BaselineScoringEngine

Responsibilities:
- calculate baseline readiness scores
- classify baseline readiness state
- detect blockers
- produce scorecard

Allowed baseline states:

- Not Ready
- Needs Manual Review
- Ready For Baseline Commit Review

Forbidden states:

- Ready For Live Trading
- Ready For Execution
- Broker Ready
- Production Trading Approved
- Approved For Real Trading

====================================================
DIAGNOSTICS
===========

Create:

ReleaseBaselineDiagnostics

Detect:

- missing repository hygiene outputs
- missing release packaging outputs
- missing certification outputs
- unclassified artifacts
- excessive manual review count
- untracked archive artifacts
- deleted phase prompt files
- modified generated reports
- modified generated storage files
- missing cleanup checklist
- missing decision matrix
- low baseline readiness score
- unsafe wording
- destructive cleanup wording
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

- مراجعة خط الأساس قبل commit
- تحديد الملفات التي يجب تضمينها في الإصدار
- فصل ملفات الأدلة عن الملفات المؤقتة
- عدم حذف الملفات تلقائياً
- مراجعة ملفات phase المحذوفة
- مراجعة artifacts الناتجة عن validation
- اعتماد سياسة واضحة للـ reports و storage
- تحديث .gitignore بعد موافقة بشرية
- إجراء commit فقط بعد مراجعة checklist
- الحفاظ على حدود البحث فقط

====================================================
SERVICE LAYER
=============

Create:

ReleaseBaselineService

Must provide:

- load_sources()
- build_baseline_inventory()
- classify_commit_candidates()
- reconcile_artifacts()
- select_release_evidence()
- build_cleanup_checklist()
- build_ignore_review()
- build_prompt_file_policy()
- analyze_validation_churn()
- reconcile_archives()
- build_decision_matrix()
- build_scorecard()
- generate_diagnostics()
- generate_recommendations()
- run_full_release_baseline()
- get_summary()

The service must be deterministic, local-only, JSON-first, baseline-reconciliation-only, manual-cleanup-planning-only, non-destructive, and safe.

====================================================
DASHBOARD
=========

Add dashboard page:

/release-baseline

Arabic navigation label:

خط أساس الإصدار

Dashboard title:

مصالحة خط أساس الإصدار وخطة التنظيف اليدوي

Display:

- حالة خط الأساس
- درجة الجاهزية العامة
- عدد عناصر الجرد
- عدد مرشحات commit
- عدد عناصر المراجعة اليدوية
- عدد عناصر cleanup اليدوي
- عدد أدلة الإصدار
- عدد توصيات .gitignore
- عدد عناصر validation churn
- عدد عناصر archive reconciliation
- التحذيرات
- التوصيات

The dashboard must clearly state:

هذه الصفحة مصالحة خط أساس وخطة تنظيف يدوية فقط ولا تحذف الملفات تلقائياً ولا تضيف تداولاً حقيقياً أو اتصالاً بوسيط.

====================================================
API ENDPOINTS
=============

Add safe local endpoints:

- /api/release-baseline
- /api/release-baseline/inventory
- /api/release-baseline/commit-classification
- /api/release-baseline/artifact-reconciliation
- /api/release-baseline/evidence
- /api/release-baseline/cleanup-checklist
- /api/release-baseline/ignore-review
- /api/release-baseline/prompt-policy
- /api/release-baseline/validation-churn
- /api/release-baseline/archive-reconciliation
- /api/release-baseline/decision-matrix
- /api/release-baseline/scorecard
- /api/release-baseline/diagnostics
- /api/release-baseline/recommendations

All endpoints must return local reconciliation/planning data only.

No external calls.

No destructive actions.

No broker interaction.

No real operational control.

====================================================
CHARTS
======

Add Arabic dashboard-ready charts for:

- تصنيف خط الأساس
- تصنيف commit
- عناصر المراجعة اليدوية
- validation churn
- archive reconciliation
- أدلة الإصدار
- درجات الجاهزية
- التحذيرات
- التوصيات

Preserve current dashboard design and RTL Arabic style.

====================================================
STORAGE
=======

Create:

storage/release_baseline/

Generate:

- source_inventory.json
- baseline_inventory.json
- commit_classification.json
- artifact_reconciliation.json
- evidence_selection.json
- cleanup_checklist.json
- ignore_review.json
- prompt_file_policy.json
- validation_churn.json
- archive_reconciliation.json
- decision_matrix.json
- scorecard.json
- diagnostics.json
- recommendations.json
- summary.json

====================================================
REPORTS
=======

Create:

reports/release_baseline/

Generate:

- release_baseline_summary.json
- source_inventory_report.json
- baseline_inventory_report.json
- commit_classification_report.json
- artifact_reconciliation_report.json
- evidence_selection_report.json
- cleanup_checklist_report.json
- ignore_review_report.json
- prompt_file_policy_report.json
- validation_churn_report.json
- archive_reconciliation_report.json
- decision_matrix_report.json
- scorecard_report.json
- diagnostics_report.json
- recommendations_report.json

====================================================
SCRIPTS
=======

Create:

scripts/run_release_baseline.py
scripts/check_release_baseline.py

scripts/run_release_baseline.py must:

- load sources
- build baseline inventory
- classify commit candidates
- reconcile artifacts
- select release evidence
- build cleanup checklist
- build ignore review
- build prompt file policy
- analyze validation churn
- reconcile archives
- build decision matrix
- build scorecard
- generate diagnostics
- generate recommendations
- write storage outputs
- write reports outputs

scripts/check_release_baseline.py must validate:

- app/release_baseline exists
- required module files exist
- required scripts exist
- required tests exist
- required dashboard template exists
- reports/release_baseline outputs exist
- storage/release_baseline outputs exist
- JSON outputs are valid
- summary confirms baseline-reconciliation-only
- summary confirms manual-cleanup-planning-only
- summary confirms non-destructive
- no destructive cleanup actions are performed
- no broker/execution/browser/auth/money-handling capability was introduced
- dashboard route exists
- API routes exist
- Arabic labels exist
- forbidden readiness states are absent

====================================================
TESTING
=======

Create:

tests/test_release_baseline.py

Tests must verify:

- source loading works with missing optional files
- baseline inventory generation works
- commit classification works
- artifact reconciliation works
- evidence selection works
- cleanup checklist is non-destructive
- ignore review does not modify .gitignore
- prompt file policy works
- validation churn analysis works
- archive reconciliation works
- decision matrix works
- scorecard generation works
- forbidden readiness states never appear
- diagnostics detect unsafe/destructive wording
- recommendations are Arabic
- dashboard endpoints work
- API endpoints work
- generated JSON files are valid
- safety boundary remains intact
- no broker/execution/browser/auth/money-handling capability exists in release_baseline module

====================================================
VALIDATION
==========

Run:

python -m compileall app
python -m pytest -q
python -m flake8 app

python scripts/check_release_baseline.py

Also run available existing validation suites for:

- repository hygiene
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

Extend only with release baseline reconciliation and manual cleanup planning.

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

Do not modify .gitignore automatically.

Do not modify signal formulas.

Do not modify paper trading logic.

Do not modify certification scoring.

Do not delete existing release artifacts.

====================================================
QUALITY RULES
=============

The implementation must be deterministic, local-only, JSON-first, dashboard-friendly, Arabic-first, backward-compatible, production-structured, baseline-reconciliation-only, manual-cleanup-planning-only, non-destructive, safe, and roadmap-oriented.

Handle missing prior outputs gracefully.

Do not fail catastrophically if optional reports are absent.

====================================================
DELIVERABLE FORMAT
==================

Return:

1. Phase 65 Implementation Summary
2. Changed Files
3. Release Baseline Layer
4. Source Loading
5. Baseline Inventory
6. Commit Classification
7. Artifact Reconciliation
8. Evidence Selection
9. Cleanup Checklist
10. Ignore Review
11. Prompt File Policy
12. Validation Churn Analysis
13. Archive Reconciliation
14. Decision Matrix
15. Baseline Scorecard
16. Dashboard Additions
17. API Endpoints Added
18. Reports Generated
19. Storage Generated
20. Safety Boundary Confirmation
21. Strategic Recommendation
22. Validation Results
23. Known Limitations
24. Worktree Notes
25. Git Commands

Git Commands:

git add .
git commit -m "Add release baseline reconciliation"
git push origin main
