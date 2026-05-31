"""Models for final release packaging outputs."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from app.release_packaging.schemas import SCHEMA_VERSION


@dataclass(frozen=True)
class RepositoryAudit:
    """Repository stabilization audit output."""

    module_inventory: list[str]
    dashboard_route_inventory: list[str]
    api_endpoint_inventory: list[str]
    script_inventory: list[str]
    test_inventory: list[str]
    report_directory_inventory: list[str]
    storage_directory_inventory: list[str]
    validation_script_inventory: list[str]
    generated_artifact_inventory: list[str]
    safety_boundary_indicators: dict[str, bool]
    missing_expected: dict[str, list[str]]
    duplicate_reports: list[str]
    empty_json_files: list[str]
    invalid_json_files: list[str]
    stale_release_files: list[str]
    unsafe_module_terms: list[str]
    schema_version: str = SCHEMA_VERSION
    research_only: bool = True
    local_only: bool = True

    def to_dict(self) -> dict[str, Any]:
        return self.__dict__.copy()


@dataclass(frozen=True)
class ReleaseManifest:
    """Release manifest for Research Platform v1.0."""

    release_id: str
    release_label: str
    release_version: str
    created_at: str
    project_name: str
    platform_type: str
    certification_state: str
    platform_score: float
    test_count: int
    phase_range: str
    completed_phases: list[int]
    dashboard_pages: list[str]
    api_endpoints: list[str]
    scripts: list[str]
    tests: list[str]
    reports: list[str]
    storage_outputs: list[str]
    safety_boundary: dict[str, bool]
    forbidden_capabilities_absent: dict[str, bool]
    checksum: str
    release_status: str
    schema_version: str = SCHEMA_VERSION
    research_only: bool = True
    local_only: bool = True

    def to_dict(self) -> dict[str, Any]:
        return self.__dict__.copy()


@dataclass(frozen=True)
class ProjectStatusReport:
    """Final project state report."""

    total_completed_phases: int
    latest_completed_phase: int
    platform_purpose: str
    current_certification_state: str
    current_validation_count: int
    core_modules: list[str]
    dashboard_pages: list[str]
    api_endpoints: list[str]
    reports_generated: list[str]
    storage_artifacts_generated: list[str]
    safety_status: dict[str, bool]
    readiness_status: str
    archive_status: str
    knowledge_graph_status: str
    research_api_status: str
    certification_status: str
    known_limitations: list[str]
    recommended_next_decision: str
    schema_version: str = SCHEMA_VERSION
    research_only: bool = True

    def to_dict(self) -> dict[str, Any]:
        return self.__dict__.copy()
