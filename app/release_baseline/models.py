"""Models for release baseline reconciliation."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from app.release_baseline.schemas import SCHEMA_VERSION


@dataclass(frozen=True)
class SerializableModel:
    schema_version: str = SCHEMA_VERSION
    baseline_reconciliation_only: bool = True
    manual_cleanup_planning_only: bool = True
    repository_hygiene_only: bool = True
    artifact_policy_only: bool = True
    local_only: bool = True
    research_only: bool = True
    non_destructive: bool = True

    def to_dict(self) -> dict[str, Any]:
        return self.__dict__.copy()


@dataclass(frozen=True)
class BaselineInventoryItem(SerializableModel):
    path: str = ""
    source: str = ""
    file_category: str = "unknown"
    git_status: str = ""
    artifact_family: str = "unknown"


@dataclass(frozen=True)
class CommitClassification(SerializableModel):
    path: str = ""
    classification: str = "manual decision required"
    rationale: str = ""
    requires_human_review: bool = True


@dataclass(frozen=True)
class ArtifactReconciliationItem(SerializableModel):
    path: str = ""
    artifact_type: str = "unknown"
    reconciliation: str = "manual review required"
    reason: str = ""


@dataclass(frozen=True)
class ReleaseEvidenceItem(SerializableModel):
    path: str = ""
    evidence_type: str = ""
    evidence_value: str = ""
    requires_human_review: bool = True


@dataclass(frozen=True)
class CleanupChecklistItem(SerializableModel):
    item_id: str = ""
    path: str = ""
    issue: str = ""
    recommended_action: str = "review"
    reason: str = ""
    safety_level: str = "يحتاج مراجعة"
    command_suggestion: str = ""
    destructive_action_forbidden: bool = True
    requires_human_confirmation: bool = True


@dataclass(frozen=True)
class IgnoreReviewItem(SerializableModel):
    pattern: str = ""
    confidence: str = "medium confidence"
    reason: str = ""
    review_only: bool = True


@dataclass(frozen=True)
class PromptFilePolicyItem(SerializableModel):
    path: str = ""
    handling: str = "review"
    reason: str = ""


@dataclass(frozen=True)
class ValidationChurnItem(SerializableModel):
    path: str = ""
    churn_type: str = "manual review required"
    reason: str = ""


@dataclass(frozen=True)
class ArchiveReconciliationItem(SerializableModel):
    path: str = ""
    archive_classification: str = "manual cleanup candidate"
    reason: str = ""


@dataclass(frozen=True)
class BaselineDecisionMatrixItem(SerializableModel):
    file_category: str = ""
    risk: str = "يحتاج مراجعة"
    recommended_handling: str = "review"
    commit_recommendation: str = "manual decision required"
    cleanup_recommendation: str = "do not touch"
    ignore_recommendation: str = "manual decision required"
    evidence_value: str = "unknown"


@dataclass(frozen=True)
class BaselineScorecard(SerializableModel):
    baseline_clarity_score: float = 0.0
    commit_readiness_score: float = 0.0
    artifact_reconciliation_score: float = 0.0
    manual_cleanup_readiness_score: float = 0.0
    evidence_selection_score: float = 0.0
    ignore_review_score: float = 0.0
    overall_baseline_readiness_score: float = 0.0
    baseline_state: str = "Needs Manual Review"


@dataclass(frozen=True)
class ReleaseBaselineSummary(SerializableModel):
    baseline_state: str = "Needs Manual Review"
    overall_baseline_readiness_score: float = 0.0
    inventory_count: int = 0
    commit_candidate_count: int = 0
    manual_review_count: int = 0
    manual_cleanup_count: int = 0
    release_evidence_count: int = 0
    ignore_recommendation_count: int = 0
    validation_churn_count: int = 0
    archive_reconciliation_count: int = 0
    diagnostic_count: int = 0
    recommendation_count: int = 0


@dataclass(frozen=True)
class ReleaseBaselineDiagnostic(SerializableModel):
    code: str = ""
    severity: str = "متوسط"
    message: str = ""


@dataclass(frozen=True)
class ReleaseBaselineRecommendation(SerializableModel):
    recommendation_id: str = ""
    text: str = ""
    priority: str = "متوسط"


def count_by(items: list[dict[str, Any]], field_name: str) -> dict[str, int]:
    counts: dict[str, int] = {}
    for item in items:
        key = str(item.get(field_name, "unknown"))
        counts[key] = counts.get(key, 0) + 1
    return counts
