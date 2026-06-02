"""Service layer for release baseline reconciliation."""

from __future__ import annotations

from dataclasses import dataclass
import json
from pathlib import Path
from typing import Any

from app.release_baseline.archive_reconciliation import ArchiveReconciliationEngine
from app.release_baseline.artifact_reconciliation import ArtifactReconciliationEngine
from app.release_baseline.baseline_inventory import BaselineInventoryEngine
from app.release_baseline.baseline_scoring import BaselineScoringEngine
from app.release_baseline.cleanup_checklist import ManualCleanupChecklistEngine
from app.release_baseline.commit_classification import CommitClassificationEngine
from app.release_baseline.decision_matrix import BaselineDecisionMatrixEngine
from app.release_baseline.diagnostics import ReleaseBaselineDiagnostics
from app.release_baseline.evidence_selection import EvidenceSelectionEngine
from app.release_baseline.ignore_review import IgnoreReviewEngine
from app.release_baseline.prompt_file_policy import PromptFilePolicyEngine
from app.release_baseline.recommendations import ReleaseBaselineRecommendationBuilder
from app.release_baseline.reports import ReleaseBaselineReportWriter
from app.release_baseline.schemas import BASELINE_ONLY_FLAGS
from app.release_baseline.source_loader import BaselineSourceLoader
from app.release_baseline.storage import ReleaseBaselineStorage
from app.release_baseline.validation_churn import ValidationChurnAnalysisEngine


@dataclass(frozen=True)
class ReleaseBaselineRunResult:
    """Result of one baseline reconciliation generation cycle."""

    payloads: dict[str, Any]
    diagnostics: list[dict[str, str]]
    recommendations: list[str]
    summary: dict[str, Any]
    storage_paths: dict[str, str]
    report_paths: dict[str, str]


class ReleaseBaselineService:
    """Generate local non-destructive release baseline artifacts."""

    def __init__(self, project_root: Path | str = ".") -> None:
        self.project_root = Path(project_root)
        self.loader = BaselineSourceLoader(self.project_root)
        self.inventory_engine = BaselineInventoryEngine(self.project_root)
        self.commit_engine = CommitClassificationEngine()
        self.reconciliation_engine = ArtifactReconciliationEngine()
        self.evidence_engine = EvidenceSelectionEngine()
        self.checklist_engine = ManualCleanupChecklistEngine()
        self.ignore_engine = IgnoreReviewEngine()
        self.prompt_engine = PromptFilePolicyEngine(self.project_root)
        self.churn_engine = ValidationChurnAnalysisEngine()
        self.archive_engine = ArchiveReconciliationEngine()
        self.matrix_engine = BaselineDecisionMatrixEngine()
        self.scoring_engine = BaselineScoringEngine()
        self.diagnostics_builder = ReleaseBaselineDiagnostics()
        self.recommendation_builder = ReleaseBaselineRecommendationBuilder()
        self.storage = ReleaseBaselineStorage(self.project_root / "storage" / "release_baseline")
        self.reports = ReleaseBaselineReportWriter(
            self.project_root / "reports" / "release_baseline"
        )

    def load_sources(self) -> dict[str, Any]:
        return self.loader.load()

    def build_baseline_inventory(self) -> dict[str, Any]:
        return self.inventory_engine.build(self.load_sources())

    def classify_commit_candidates(self) -> dict[str, Any]:
        return self.commit_engine.classify(self.build_baseline_inventory())

    def reconcile_artifacts(self) -> dict[str, Any]:
        return self.reconciliation_engine.reconcile(self.build_baseline_inventory())

    def select_release_evidence(self) -> dict[str, Any]:
        return self.evidence_engine.select(self.build_baseline_inventory())

    def build_cleanup_checklist(self) -> dict[str, Any]:
        return self.checklist_engine.build(self.classify_commit_candidates())

    def build_ignore_review(self) -> dict[str, Any]:
        return self.ignore_engine.build(self.load_sources())

    def build_prompt_file_policy(self) -> dict[str, Any]:
        return self.prompt_engine.build(self.load_sources())

    def analyze_validation_churn(self) -> dict[str, Any]:
        return self.churn_engine.analyze(self.load_sources())

    def reconcile_archives(self) -> dict[str, Any]:
        return self.archive_engine.reconcile(self.build_baseline_inventory())

    def build_decision_matrix(self) -> dict[str, Any]:
        return self.matrix_engine.build()

    def build_scorecard(self) -> dict[str, Any]:
        payloads = self._build_payloads(include_summary=False)
        return payloads["scorecard"]

    def generate_diagnostics(self) -> list[dict[str, str]]:
        return self.diagnostics_builder.evaluate(
            self.project_root,
            self._build_payloads(include_summary=False),
        )

    def generate_recommendations(self) -> list[str]:
        return self.recommendation_builder.build()

    def run_full_release_baseline(self) -> ReleaseBaselineRunResult:
        payloads = self._build_payloads(include_summary=False)
        diagnostics = self.diagnostics_builder.evaluate(self.project_root, payloads)
        recommendations = self.generate_recommendations()
        summary = self._summary(payloads, diagnostics, recommendations)
        payloads = {
            **payloads,
            "diagnostics": diagnostics,
            "recommendations": recommendations,
            "summary": summary,
        }
        storage_paths = self.storage.save(payloads)
        report_paths = self.reports.export(payloads)
        return ReleaseBaselineRunResult(
            payloads=payloads,
            diagnostics=diagnostics,
            recommendations=recommendations,
            summary=summary,
            storage_paths=storage_paths,
            report_paths=report_paths,
        )

    def get_summary(self) -> dict[str, Any]:
        payload = self._read_json(
            "reports",
            "release_baseline",
            "release_baseline_summary.json",
        )
        if isinstance(payload, dict) and payload:
            return payload
        return self.run_full_release_baseline().summary

    def _build_payloads(self, include_summary: bool = True) -> dict[str, Any]:
        sources = self.load_sources()
        inventory = self.inventory_engine.build(sources)
        classification = self.commit_engine.classify(inventory)
        reconciliation = self.reconciliation_engine.reconcile(inventory)
        evidence = self.evidence_engine.select(inventory)
        checklist = self.checklist_engine.build(classification)
        ignore = self.ignore_engine.build(sources)
        prompt = self.prompt_engine.build(sources)
        churn = self.churn_engine.analyze(sources)
        archive = self.archive_engine.reconcile(inventory)
        matrix = self.matrix_engine.build()
        scorecard = self.scoring_engine.build(
            inventory,
            classification,
            reconciliation,
            checklist,
            evidence,
            ignore,
        )
        payloads = {
            "source_inventory": sources,
            "baseline_inventory": inventory,
            "commit_classification": classification,
            "artifact_reconciliation": reconciliation,
            "evidence_selection": evidence,
            "cleanup_checklist": checklist,
            "ignore_review": ignore,
            "prompt_file_policy": prompt,
            "validation_churn": churn,
            "archive_reconciliation": archive,
            "decision_matrix": matrix,
            "scorecard": scorecard,
        }
        if include_summary:
            diagnostics = self.diagnostics_builder.evaluate(self.project_root, payloads)
            payloads["summary"] = self._summary(
                payloads,
                diagnostics,
                self.generate_recommendations(),
            )
        return payloads

    def _summary(
        self,
        payloads: dict[str, Any],
        diagnostics: list[dict[str, str]],
        recommendations: list[str],
    ) -> dict[str, Any]:
        scorecard = payloads["scorecard"]
        classifications = payloads["commit_classification"].get("items", [])
        checklist = payloads["cleanup_checklist"].get("items", [])
        return {
            "baseline_state": scorecard["baseline_state"],
            "overall_baseline_readiness_score": scorecard[
                "overall_baseline_readiness_score"
            ],
            "inventory_count": len(payloads["baseline_inventory"].get("items", [])),
            "commit_candidate_count": sum(
                1
                for item in classifications
                if item.get("classification")
                in {"commit recommended", "commit after review", "retain as release evidence"}
            ),
            "manual_review_count": sum(
                1 for item in classifications if item.get("requires_human_review")
            ),
            "manual_cleanup_count": sum(
                1
                for item in checklist
                if item.get("recommended_action") == "manual cleanup candidate"
            ),
            "release_evidence_count": len(payloads["evidence_selection"].get("items", [])),
            "ignore_recommendation_count": len(payloads["ignore_review"].get("items", [])),
            "validation_churn_count": len(payloads["validation_churn"].get("items", [])),
            "archive_reconciliation_count": len(
                payloads["archive_reconciliation"].get("items", [])
            ),
            "diagnostic_count": len(diagnostics),
            "recommendation_count": len(recommendations),
            **BASELINE_ONLY_FLAGS,
        }

    def _read_json(self, *parts: str) -> Any:
        path = self.project_root.joinpath(*parts)
        if not path.exists():
            return {}
        try:
            return json.loads(path.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError):
            return {}
