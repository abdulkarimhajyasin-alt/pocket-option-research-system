"""Typed models for research archive and versioning."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from app.research_archive.schemas import SCHEMA_VERSION

CREATED_AT = "deterministic-local-research-archive"


@dataclass(frozen=True)
class ResearchSnapshot:
    """Deterministic snapshot of the current local research state."""

    snapshot_id: str
    version: str
    created_at: str
    source_summary: dict[str, Any]
    included_sources: list[dict[str, Any]]
    missing_sources: list[dict[str, Any]]
    checksum: str
    safety_status: dict[str, Any]
    research_only: bool = True
    schema_version: str = SCHEMA_VERSION

    def to_dict(self) -> dict[str, Any]:
        return {
            "snapshot_id": self.snapshot_id,
            "version": self.version,
            "created_at": self.created_at,
            "source_summary": self.source_summary,
            "included_sources": self.included_sources,
            "missing_sources": self.missing_sources,
            "checksum": self.checksum,
            "safety_status": self.safety_status,
            "research_only": self.research_only,
            "schema_version": self.schema_version,
        }


@dataclass(frozen=True)
class ResearchVersion:
    """Stable version record for an archived research state."""

    version_id: str
    version_label: str
    snapshot_id: str
    created_at: str
    previous_version_id: str | None
    checksum: str
    metadata: dict[str, Any]
    safety_boundary: dict[str, Any]

    def to_dict(self) -> dict[str, Any]:
        return {
            "version_id": self.version_id,
            "version_label": self.version_label,
            "snapshot_id": self.snapshot_id,
            "created_at": self.created_at,
            "previous_version_id": self.previous_version_id,
            "checksum": self.checksum,
            "metadata": self.metadata,
            "safety_boundary": self.safety_boundary,
        }


@dataclass(frozen=True)
class ResearchArchiveRecord:
    """Stored archive package metadata."""

    archive_id: str
    version_id: str
    snapshot_id: str
    archive_path: str
    report_path: str
    source_count: int
    file_count: int
    archive_status: str
    diagnostics_count: int

    def to_dict(self) -> dict[str, Any]:
        return {
            "archive_id": self.archive_id,
            "version_id": self.version_id,
            "snapshot_id": self.snapshot_id,
            "archive_path": self.archive_path,
            "report_path": self.report_path,
            "source_count": self.source_count,
            "file_count": self.file_count,
            "archive_status": self.archive_status,
            "diagnostics_count": self.diagnostics_count,
        }


@dataclass(frozen=True)
class ResearchDiff:
    """Comparison between two archived research snapshots."""

    from_version: str | None
    to_version: str | None
    added_keys: list[str]
    removed_keys: list[str]
    changed_values: list[dict[str, Any]]
    improved_metrics: list[dict[str, Any]]
    degraded_metrics: list[dict[str, Any]]
    stable_metrics: list[str]
    missing_comparison_areas: list[str]
    summary_ar: list[str]
    research_only: bool = True

    def to_dict(self) -> dict[str, Any]:
        return {
            "from_version": self.from_version,
            "to_version": self.to_version,
            "added_keys": self.added_keys,
            "removed_keys": self.removed_keys,
            "changed_values": self.changed_values,
            "improved_metrics": self.improved_metrics,
            "degraded_metrics": self.degraded_metrics,
            "stable_metrics": self.stable_metrics,
            "missing_comparison_areas": self.missing_comparison_areas,
            "summary_ar": self.summary_ar,
            "research_only": self.research_only,
        }


@dataclass(frozen=True)
class ResearchEvolution:
    """Historical intelligence view across archived versions."""

    version_count: int
    readiness_trend: str
    knowledge_score_trend: str
    graph_density_trend: str
    diagnostics_trend: str
    recommendation_trend: str
    source_coverage_trend: str
    research_quality_trend: str
    recurring_diagnostics: list[str]
    research_only: bool = True

    def to_dict(self) -> dict[str, Any]:
        return {
            "version_count": self.version_count,
            "readiness_trend": self.readiness_trend,
            "knowledge_score_trend": self.knowledge_score_trend,
            "graph_density_trend": self.graph_density_trend,
            "diagnostics_trend": self.diagnostics_trend,
            "recommendation_trend": self.recommendation_trend,
            "source_coverage_trend": self.source_coverage_trend,
            "research_quality_trend": self.research_quality_trend,
            "recurring_diagnostics": self.recurring_diagnostics,
            "research_only": self.research_only,
        }
