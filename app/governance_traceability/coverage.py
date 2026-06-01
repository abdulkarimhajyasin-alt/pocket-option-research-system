"""Traceability coverage scoring engine."""

from __future__ import annotations

from typing import Any

from app.governance_traceability.models import TraceabilityCoverageSummary
from app.governance_traceability.schemas import TRACEABILITY_ONLY_FLAGS


class GovernanceTraceabilityCoverageEngine:
    """Calculate deterministic traceability coverage scores."""

    def build(self, payloads: dict[str, Any]) -> dict[str, Any]:
        mappings = payloads.get("control_mappings", {}).get("items", [])
        evidence = payloads.get("evidence_matrix", {}).get("items", [])
        readiness = payloads.get("readiness_mapping", {}).get("items", [])
        policies = payloads.get("policy_mapping", {}).get("items", [])
        strong = sum(1 for item in mappings if item.get("strength") == "قوي")
        weak = sum(1 for item in mappings if item.get("strength") == "ضعيف")
        missing = sum(1 for item in mappings if item.get("strength") == "مفقود")
        total = len(mappings) or 1
        control_score = round(((total - missing) / total) * 100, 2)
        evidence_score = round((len(evidence) / max(total, 1)) * 100, 2)
        readiness_score = round((len(readiness) / 9) * 100, 2)
        policy_score = round((len(policies) / 8) * 100, 2)
        overall = round(
            (control_score + min(evidence_score, 100) + readiness_score + policy_score) / 4,
            2,
        )
        summary = TraceabilityCoverageSummary(
            readiness_state="Traceability Incomplete",
            mapped_design_areas=total - missing,
            unmapped_design_areas=missing,
            strong_mappings=strong,
            weak_mappings=weak,
            missing_controls=missing,
            control_coverage_score=control_score,
            evidence_coverage_score=min(evidence_score, 100),
            readiness_traceability_score=min(readiness_score, 100),
            policy_coverage_score=min(policy_score, 100),
            overall_traceability_score=overall,
        ).to_dict()
        summary.update(TRACEABILITY_ONLY_FLAGS)
        return summary
