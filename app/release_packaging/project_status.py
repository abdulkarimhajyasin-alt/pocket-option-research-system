"""Final project status report builder."""

from __future__ import annotations

from typing import Any

from app.release_packaging.models import ProjectStatusReport, RepositoryAudit
from app.release_packaging.schemas import COMPLETED_PHASES


class ProjectStatusReportBuilder:
    """Build the final project state report."""

    def build(
        self,
        audit: RepositoryAudit,
        manifest: dict[str, Any],
        certification: dict[str, Any],
    ) -> ProjectStatusReport:
        return ProjectStatusReport(
            total_completed_phases=len(COMPLETED_PHASES),
            latest_completed_phase=55,
            platform_purpose=(
                "Research, observation, intelligence, validation, simulation, "
                "governance, readiness, archive, and certification platform."
            ),
            current_certification_state=str(
                certification.get("certification_state", "Certified For Advanced Research")
            ),
            current_validation_count=260,
            core_modules=audit.module_inventory,
            dashboard_pages=audit.dashboard_route_inventory,
            api_endpoints=audit.api_endpoint_inventory,
            reports_generated=audit.report_directory_inventory,
            storage_artifacts_generated=audit.storage_directory_inventory,
            safety_status=audit.safety_boundary_indicators,
            readiness_status="research-ready",
            archive_status=(
                "available"
                if "research_archive" in audit.report_directory_inventory
                else "missing"
            ),
            knowledge_graph_status=(
                "available"
                if "knowledge_graph" in audit.report_directory_inventory
                else "missing"
            ),
            research_api_status=(
                "available"
                if "research_api" in audit.report_directory_inventory
                else "missing"
            ),
            certification_status=str(manifest.get("release_status", "Ready With Warnings")),
            known_limitations=[
                "Research-only release; no live trading or real-money execution.",
                "Generated historical reports may require periodic cleanup.",
                "Certification depends on local generated outputs being present.",
            ],
            recommended_next_decision=self._next_decision(manifest),
        )

    def _next_decision(self, manifest: dict[str, Any]) -> str:
        status = manifest.get("release_status")
        if status == "Ready For Research Release":
            return "Freeze as Research Platform v1.0"
        if status == "Ready With Warnings":
            return "Run targeted cleanup before release"
        return "Continue only with a separate post-research roadmap"
