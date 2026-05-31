"""Service orchestration for external integration safety boundary."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import UTC, datetime
import json
from pathlib import Path
from typing import Any

from app.integration_safety.analytics import IntegrationSafetyAnalytics
from app.integration_safety.audit import IntegrationSafetyAudit
from app.integration_safety.boundary import IntegrationBoundaryEngine
from app.integration_safety.diagnostics import IntegrationSafetyDiagnostics
from app.integration_safety.models import (
    ALLOWED_CAPABILITIES,
    FORBIDDEN_CAPABILITIES,
    IntegrationSafetyRun,
)
from app.integration_safety.permissions import IntegrationPermissionEngine
from app.integration_safety.policy import IntegrationSafetyPolicyBuilder
from app.integration_safety.recommendations import IntegrationSafetyRecommendations
from app.integration_safety.reports import IntegrationSafetyReportWriter
from app.integration_safety.restrictions import IntegrationRestrictionEngine
from app.integration_safety.storage import IntegrationSafetyStorage
from app.integration_safety.validation import IntegrationComplianceEngine


@dataclass(frozen=True)
class IntegrationSafetyRunResult:
    """Result of one integration safety boundary run."""

    result: IntegrationSafetyRun
    storage_paths: dict[str, str]
    report_paths: dict[str, str]


class IntegrationSafetyService:
    """Define and validate safety boundaries for future integration work only."""

    def __init__(self, project_root: Path | str = ".") -> None:
        self.project_root = Path(project_root)
        self.permissions = IntegrationPermissionEngine()
        self.restrictions = IntegrationRestrictionEngine()
        self.compliance = IntegrationComplianceEngine()
        self.boundary = IntegrationBoundaryEngine()
        self.policy = IntegrationSafetyPolicyBuilder()
        self.diagnostics = IntegrationSafetyDiagnostics()
        self.recommendations = IntegrationSafetyRecommendations()
        self.audit = IntegrationSafetyAudit()
        self.analytics = IntegrationSafetyAnalytics()
        self.storage = IntegrationSafetyStorage(
            self.project_root / "storage" / "integration_safety"
        )
        self.reports = IntegrationSafetyReportWriter(
            self.project_root / "reports" / "integration_safety"
        )

    def run(self) -> IntegrationSafetyRunResult:
        self._sources()
        metadata = self._metadata()
        permissions = self.permissions.evaluate(ALLOWED_CAPABILITIES)
        restrictions = self.restrictions.evaluate(())
        compliance = self.compliance.evaluate(metadata)
        boundary = self.boundary.evaluate(permissions, restrictions, compliance)
        policy = self.policy.build(boundary, compliance, metadata)
        diagnostics = self.diagnostics.evaluate(
            permissions,
            restrictions,
            compliance,
            boundary,
            audit_present=True,
        )
        recommendations = self.recommendations.generate(diagnostics)
        audit = self.audit.build(
            ALLOWED_CAPABILITIES,
            FORBIDDEN_CAPABILITIES,
            restrictions,
            diagnostics,
            recommendations,
            metadata,
        )
        analytics = self.analytics.summarize(
            policy,
            boundary,
            permissions,
            restrictions,
            compliance,
            audit,
            diagnostics,
            recommendations,
        )
        result = IntegrationSafetyRun(
            timestamp=datetime.now(UTC),
            policy=policy,
            boundary=boundary,
            permissions=permissions,
            restrictions=restrictions,
            compliance=compliance,
            audit=audit,
            analytics=analytics,
            diagnostics=diagnostics,
            recommendations=recommendations,
            metadata=metadata,
        )
        storage_paths = self.storage.save(result)
        report_paths = self.reports.export(result)
        return IntegrationSafetyRunResult(result, storage_paths, report_paths)

    def _sources(self) -> dict[str, Any]:
        return {
            "paper_live_readiness": self._read_json(
                "reports",
                "paper_live_readiness",
                "readiness_summary.json",
            ),
            "broker_readiness": self._read_json(
                "reports",
                "broker_readiness",
                "readiness_summary.json",
            ),
            "external_observation": self._read_json(
                "reports",
                "external_observation",
                "sandbox_summary.json",
            ),
            "browser_observation": self._read_json(
                "reports",
                "browser_observation",
                "observation_summary.json",
            ),
            "snapshot_import": self._read_json(
                "reports",
                "snapshot_import",
                "import_summary.json",
            ),
            "observation_intelligence": self._read_json(
                "reports",
                "observation_intelligence",
                "observation_summary.json",
            ),
            "market_observation": self._read_json(
                "reports",
                "market_observation",
                "observation_summary.json",
            ),
            "research_certification": self._read_json(
                "reports",
                "research_certification",
                "certification_summary.json",
            ),
        }

    def _read_json(self, *parts: str) -> Any:
        path = self.project_root.joinpath(*parts)
        if not path.exists():
            return {}
        try:
            return json.loads(path.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError):
            return {}

    def _metadata(self) -> dict[str, bool]:
        return {
            "safety_boundary_only": True,
            "readiness_only": True,
            "research_only": True,
            "observation_only": True,
            "paper_only": True,
            "local_only": True,
            "audit_only": True,
            "not_execution": True,
            "not_real_execution": True,
            "not_order_placement": True,
            "not_real_order_placement": True,
            "not_buy_sell_action": True,
            "not_broker_access": True,
            "not_broker_api": True,
            "not_account_login": True,
            "not_authentication": True,
            "not_credential_handling": True,
            "not_browser_automation": True,
            "not_real_money": True,
            "not_position_management": True,
            "not_live_trading": True,
            "not_external_execution_adapter": True,
            "not_trading_automation": True,
            "not_broker_control": True,
            "not_pocket_option_integration": True,
        }
