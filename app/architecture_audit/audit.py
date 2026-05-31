"""Final certification builder for architecture audit."""

from __future__ import annotations

from datetime import UTC, datetime
from typing import Any

from app.architecture_audit.models import (
    CERT_CONDITIONALLY_READY,
    CERT_FULLY_READY,
    CERT_NEEDS_RESTRUCTURE,
    CERT_NEEDS_REVIEW,
    ProductionResearchCertification,
)


class ProductionResearchCertificationEngine:
    """Build final research-platform certification."""

    def certify(
        self,
        architecture: dict[str, Any],
        consistency: dict[str, Any],
        dependency: dict[str, Any],
        performance: dict[str, Any],
        safety: dict[str, Any],
        metadata: dict[str, bool],
    ) -> ProductionResearchCertification:
        scores = (
            float(architecture.get("architecture_score", 0.0)),
            float(consistency.get("consistency_score", 0.0)),
            float(dependency.get("dependency_score", 0.0)),
            float(performance.get("performance_score", 0.0)),
            float(safety.get("safety_score", 0.0)),
        )
        overall = round(sum(scores) / len(scores), 2)
        if overall >= 95:
            state = CERT_FULLY_READY
        elif overall >= 85:
            state = CERT_CONDITIONALLY_READY
        elif overall >= 70:
            state = CERT_NEEDS_REVIEW
        else:
            state = CERT_NEEDS_RESTRUCTURE
        now = datetime.now(UTC)
        return ProductionResearchCertification(
            certification_id=f"architecture_audit_{now.strftime('%Y%m%d%H%M%S')}",
            generated_at=now.isoformat(),
            architecture_score=scores[0],
            consistency_score=scores[1],
            dependency_score=scores[2],
            performance_score=scores[3],
            safety_score=scores[4],
            overall_score=overall,
            certification_state=state,
            metadata=metadata,
        )
