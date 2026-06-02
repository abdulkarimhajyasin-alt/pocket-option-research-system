"""Models for repository hygiene and artifact retention policy."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

from app.repository_hygiene.schemas import SCHEMA_VERSION


@dataclass(frozen=True)
class SerializableModel:
    schema_version: str = SCHEMA_VERSION
    repository_hygiene_only: bool = True
    artifact_policy_only: bool = True
    governance_only: bool = True
    design_only: bool = True
    architecture_only: bool = True
    research_only: bool = True
    local_only: bool = True
    non_destructive: bool = True

    def to_dict(self) -> dict[str, Any]:
        return self.__dict__.copy()


@dataclass(frozen=True)
class GitStatusItem(SerializableModel):
    path: str = ""
    index_status: str = ""
    worktree_status: str = ""
    status_label: str = ""
    category: str = "unknown"


@dataclass(frozen=True)
class ArtifactInventoryItem(SerializableModel):
    path: str = ""
    artifact_family: str = "unknown"
    file_name: str = ""
    suffix: str = ""
    size_bytes: int = 0
    version_number: int | None = None


@dataclass(frozen=True)
class ArtifactClassification(SerializableModel):
    path: str = ""
    classification: str = "unknown"
    reason: str = ""
    source_control_candidate: bool = False


@dataclass(frozen=True)
class RetentionRule(SerializableModel):
    rule_id: str = ""
    artifact_type: str = ""
    retention: str = ""
    manual_review_required: bool = True
    preserve_as_release_evidence: bool = False


@dataclass(frozen=True)
class CleanupPlanItem(SerializableModel):
    item_id: str = ""
    path: str = ""
    classification: str = ""
    recommended_action: str = "review manually"
    safety_level: str = "يحتاج مراجعة"
    requires_manual_review: bool = True
    reason: str = ""
    windows_note: str = ""
    destructive_action_forbidden: bool = True


@dataclass(frozen=True)
class IgnoreRecommendation(SerializableModel):
    pattern: str = ""
    reason: str = ""
    confidence: str = "متوسط"
    recommendation_only: bool = True


@dataclass(frozen=True)
class DuplicateArtifactFinding(SerializableModel):
    file_name: str = ""
    paths: list[str] = field(default_factory=list)
    count: int = 0
    action: str = "review manually"


@dataclass(frozen=True)
class StaleArtifactFinding(SerializableModel):
    path: str = ""
    reason: str = ""
    version_number: int | None = None
    action: str = "review manually"


@dataclass(frozen=True)
class ArchiveRetentionRule(SerializableModel):
    snapshot_pattern: str = "research-vNNNN"
    retain_latest_count: int = 5
    preserve_release_evidence: bool = True
    cleanup_mode: str = "manual review only"


@dataclass(frozen=True)
class HygieneScorecard(SerializableModel):
    git_status_cleanliness_score: float = 0.0
    artifact_classification_score: float = 0.0
    retention_policy_coverage_score: float = 0.0
    cleanup_plan_completeness_score: float = 0.0
    ignore_recommendation_score: float = 0.0
    overall_repository_hygiene_score: float = 0.0
    score_status: str = "غير جاهز"


@dataclass(frozen=True)
class RepositoryHygieneSummary(SerializableModel):
    hygiene_status: str = "يحتاج مراجعة"
    overall_repository_hygiene_score: float = 0.0
    untracked_file_count: int = 0
    modified_file_count: int = 0
    deleted_file_count: int = 0
    classified_artifact_count: int = 0
    cleanup_plan_count: int = 0
    ignore_recommendation_count: int = 0
    manual_review_count: int = 0
    diagnostic_count: int = 0
    recommendation_count: int = 0


@dataclass(frozen=True)
class RepositoryHygieneDiagnostic(SerializableModel):
    code: str = ""
    severity: str = "متوسط"
    message: str = ""


@dataclass(frozen=True)
class RepositoryHygieneRecommendation(SerializableModel):
    recommendation_id: str = ""
    text: str = ""
    priority: str = "متوسط"
