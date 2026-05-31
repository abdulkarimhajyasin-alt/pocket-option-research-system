"""Release notes builder for Research Platform v1.0."""

from __future__ import annotations

from typing import Any


class ReleaseNotesBuilder:
    """Generate final research-only release notes."""

    def build(self, manifest: dict[str, Any], status: dict[str, Any]) -> dict[str, Any]:
        return {
            "release_title": "Research Platform v1.0",
            "summary": (
                "This release is research-only and does not provide live trading, "
                "broker integration, order placement, or real-money execution."
            ),
            "completed_phase_milestones": manifest.get("completed_phases", []),
            "core_capabilities": [
                "Research intelligence",
                "Observation reporting",
                "Paper-only simulation governance",
                "Readiness analysis",
                "Archive and versioning",
                "Final research certification",
            ],
            "dashboard_capabilities": status.get("dashboard_pages", []),
            "api_capabilities": status.get("api_endpoints", []),
            "archive_versioning_capabilities": [
                "deterministic snapshots",
                "version history",
                "research diffs",
                "evolution summaries",
            ],
            "certification_capabilities": [
                "architecture integrity",
                "safety integrity",
                "research completeness",
                "platform maturity",
            ],
            "validation_summary": {
                "latest_reported_tests": manifest.get("test_count", 260),
                "release_status": manifest.get("release_status"),
            },
            "safety_boundary_summary": manifest.get("safety_boundary", {}),
            "known_limitations": status.get("known_limitations", []),
            "not_included_explicitly_forbidden": [
                "live trading",
                "broker integration",
                "Pocket Option login",
                "order placement",
                "real-money execution",
                "external execution adapters",
            ],
            "next_roadmap_options": [
                "Freeze as Research Platform v1.0",
                "Run targeted cleanup before release",
                "Continue only with a separate post-research roadmap",
            ],
            "research_only": True,
            "local_only": True,
        }
