"""Safety policy construction."""

from __future__ import annotations

from datetime import UTC, datetime
from typing import Any

from app.integration_safety.models import (
    ALLOWED_CAPABILITIES,
    FORBIDDEN_CAPABILITIES,
    IntegrationSafetyPolicy,
)


class IntegrationSafetyPolicyBuilder:
    """Build a strict safety policy for future integration work."""

    def build(
        self,
        boundary: dict[str, Any],
        compliance: dict[str, Any],
        metadata: dict[str, bool],
    ) -> IntegrationSafetyPolicy:
        now = datetime.now(UTC)
        return IntegrationSafetyPolicy(
            policy_id=f"integration_safety_{now.strftime('%Y%m%d%H%M%S')}",
            generated_at=now.isoformat(),
            allowed_capabilities=ALLOWED_CAPABILITIES,
            forbidden_capabilities=FORBIDDEN_CAPABILITIES,
            boundary_status=str(boundary.get("boundary_status", "")),
            safety_score=float(boundary.get("safety_score", 0.0)),
            compliance_score=float(compliance.get("compliance_score", 0.0)),
            metadata=metadata,
        )
