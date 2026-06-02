"""Service layer for repository hygiene and artifact retention policy."""

from __future__ import annotations

from dataclasses import dataclass
import json
from pathlib import Path
from typing import Any

from app.repository_hygiene.archive_policy import ArchivePolicyEngine
from app.repository_hygiene.artifact_inventory import ArtifactInventoryEngine
from app.repository_hygiene.cleanup_planner import CleanupPlanner
from app.repository_hygiene.diagnostics import RepositoryHygieneDiagnostics
from app.repository_hygiene.duplicate_detection import DuplicateArtifactDetectionEngine
from app.repository_hygiene.git_status_parser import GitStatusParser
from app.repository_hygiene.hygiene_scoring import HygieneScoringEngine
from app.repository_hygiene.ignore_recommendations import IgnoreRecommendationEngine
from app.repository_hygiene.recommendations import RepositoryHygieneRecommendationBuilder
from app.repository_hygiene.report_policy import ReportPolicyEngine
from app.repository_hygiene.reports import RepositoryHygieneReportWriter
from app.repository_hygiene.retention_policy import RetentionPolicyEngine
from app.repository_hygiene.schemas import HYGIENE_ONLY_FLAGS
from app.repository_hygiene.stale_detection import StaleArtifactDetectionEngine
from app.repository_hygiene.storage import RepositoryHygieneStorage
from app.repository_hygiene.storage_policy import StoragePolicyEngine


@dataclass(frozen=True)
class RepositoryHygieneRunResult:
    """Result of one hygiene generation cycle."""

    payloads: dict[str, Any]
    diagnostics: list[dict[str, str]]
    recommendations: list[str]
    summary: dict[str, Any]
    storage_paths: dict[str, str]
    report_paths: dict[str, str]


class RepositoryHygieneService:
    """Generate local non-destructive repository hygiene artifacts."""

    def __init__(self, project_root: Path | str = ".") -> None:
        self.project_root = Path(project_root)
        self.git_parser = GitStatusParser(self.project_root)
        self.inventory_engine = ArtifactInventoryEngine(self.project_root)
        self.retention_engine = RetentionPolicyEngine()
        self.cleanup_planner = CleanupPlanner()
        self.ignore_engine = IgnoreRecommendationEngine(self.project_root)
        self.duplicate_engine = DuplicateArtifactDetectionEngine()
        self.stale_engine = StaleArtifactDetectionEngine()
        self.archive_engine = ArchivePolicyEngine()
        self.report_policy_engine = ReportPolicyEngine()
        self.storage_policy_engine = StoragePolicyEngine()
        self.scoring_engine = HygieneScoringEngine()
        self.diagnostics_builder = RepositoryHygieneDiagnostics()
        self.recommendation_builder = RepositoryHygieneRecommendationBuilder()
        self.storage = RepositoryHygieneStorage(
            self.project_root / "storage" / "repository_hygiene"
        )
        self.reports = RepositoryHygieneReportWriter(
            self.project_root / "reports" / "repository_hygiene"
        )

    def parse_git_status(self) -> dict[str, Any]:
        return self.git_parser.parse()

    def build_artifact_inventory(self) -> dict[str, Any]:
        return self.inventory_engine.inventory()

    def classify_artifacts(self) -> dict[str, Any]:
        return self.inventory_engine.classify(self.build_artifact_inventory())

    def build_retention_policy(self) -> dict[str, Any]:
        return self.retention_engine.build()

    def build_cleanup_plan(self) -> dict[str, Any]:
        return self.cleanup_planner.build(self.classify_artifacts(), self.parse_git_status())

    def build_ignore_recommendations(self) -> dict[str, Any]:
        return self.ignore_engine.build()

    def detect_duplicates(self) -> dict[str, Any]:
        return self.duplicate_engine.detect(self.build_artifact_inventory())

    def detect_stale_artifacts(self) -> dict[str, Any]:
        return self.stale_engine.detect(self.build_artifact_inventory())

    def build_archive_policy(self) -> dict[str, Any]:
        return self.archive_engine.build()

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

    def run_full_repository_hygiene(self) -> RepositoryHygieneRunResult:
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
        return RepositoryHygieneRunResult(
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
            "repository_hygiene",
            "repository_hygiene_summary.json",
        )
        if isinstance(payload, dict) and payload:
            return payload
        return self.run_full_repository_hygiene().summary

    def _build_payloads(self, include_summary: bool = True) -> dict[str, Any]:
        git_status = self.parse_git_status()
        inventory = self.build_artifact_inventory()
        classification = self.inventory_engine.classify(inventory)
        retention = self.build_retention_policy()
        cleanup = self.cleanup_planner.build(classification, git_status)
        ignore = self.build_ignore_recommendations()
        duplicates = self.duplicate_engine.detect(inventory)
        stale = self.stale_engine.detect(inventory)
        archive = self.build_archive_policy()
        scorecard = self.scoring_engine.build(
            git_status,
            classification,
            retention,
            cleanup,
            ignore,
        )
        payloads = {
            "git_status_inventory": git_status,
            "artifact_inventory": inventory,
            "artifact_classification": classification,
            "retention_policy": retention,
            "cleanup_plan": cleanup,
            "ignore_recommendations": ignore,
            "duplicate_artifacts": duplicates,
            "stale_artifacts": stale,
            "archive_policy": archive,
            "report_policy": self.report_policy_engine.build(),
            "storage_policy": self.storage_policy_engine.build(),
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
        git_summary = payloads["git_status_inventory"].get("summary", {})
        cleanup_items = payloads["cleanup_plan"].get("items", [])
        return {
            "hygiene_status": scorecard["score_status"],
            "overall_repository_hygiene_score": scorecard[
                "overall_repository_hygiene_score"
            ],
            "untracked_file_count": int(git_summary.get("untracked", 0)),
            "modified_file_count": int(git_summary.get("modified", 0)),
            "deleted_file_count": int(git_summary.get("deleted", 0)),
            "classified_artifact_count": len(
                payloads["artifact_classification"].get("items", [])
            ),
            "cleanup_plan_count": len(cleanup_items),
            "ignore_recommendation_count": len(
                payloads["ignore_recommendations"].get("items", [])
            ),
            "manual_review_count": sum(
                1 for item in cleanup_items if item.get("requires_manual_review")
            ),
            "diagnostic_count": len(diagnostics),
            "recommendation_count": len(recommendations),
            **HYGIENE_ONLY_FLAGS,
        }

    def _read_json(self, *parts: str) -> Any:
        path = self.project_root.joinpath(*parts)
        if not path.exists():
            return {}
        try:
            return json.loads(path.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError):
            return {}
