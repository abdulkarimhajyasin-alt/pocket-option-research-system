"""Service orchestration for production research architecture audit."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import UTC, datetime
from pathlib import Path

from app.architecture_audit.analytics import ArchitectureAuditAnalytics
from app.architecture_audit.architecture import ArchitectureAuditEngine
from app.architecture_audit.audit import ProductionResearchCertificationEngine
from app.architecture_audit.consistency import ConsistencyEngine
from app.architecture_audit.dependency import DependencyAuditEngine
from app.architecture_audit.diagnostics import ArchitectureDiagnostics
from app.architecture_audit.models import ArchitectureAuditRun
from app.architecture_audit.performance import PerformanceAuditEngine
from app.architecture_audit.recommendations import ArchitectureRecommendations
from app.architecture_audit.reports import ArchitectureAuditReportWriter
from app.architecture_audit.safety import SafetyAuditEngine
from app.architecture_audit.storage import ArchitectureAuditStorage


@dataclass(frozen=True)
class ArchitectureAuditRunResult:
    """Result of one architecture audit run."""

    result: ArchitectureAuditRun
    storage_paths: dict[str, str]
    report_paths: dict[str, str]


class ArchitectureAuditService:
    """Run local architecture hardening audits only."""

    def __init__(self, project_root: Path | str = ".") -> None:
        self.project_root = Path(project_root)
        self.architecture = ArchitectureAuditEngine()
        self.consistency = ConsistencyEngine()
        self.dependency = DependencyAuditEngine()
        self.performance = PerformanceAuditEngine()
        self.safety = SafetyAuditEngine()
        self.certifier = ProductionResearchCertificationEngine()
        self.diagnostics = ArchitectureDiagnostics()
        self.recommendations = ArchitectureRecommendations()
        self.analytics = ArchitectureAuditAnalytics()
        self.storage = ArchitectureAuditStorage(
            self.project_root / "storage" / "architecture_audit"
        )
        self.reports = ArchitectureAuditReportWriter(
            self.project_root / "reports" / "architecture_audit"
        )

    def run(self) -> ArchitectureAuditRunResult:
        metadata = self._metadata()
        architecture = self.architecture.evaluate(self.project_root)
        consistency = self.consistency.evaluate(self.project_root)
        dependency = self.dependency.evaluate(self.project_root)
        performance = self.performance.evaluate(self.project_root)
        safety = self.safety.evaluate(self.project_root, metadata)
        certification = self.certifier.certify(
            architecture,
            consistency,
            dependency,
            performance,
            safety,
            metadata,
        )
        test_count = len(list((self.project_root / "tests").glob("test_*.py")))
        diagnostics = self.diagnostics.evaluate(
            architecture,
            consistency,
            dependency,
            performance,
            safety,
            test_count,
        )
        recommendations = self.recommendations.generate(diagnostics)
        analytics = self.analytics.summarize(
            certification,
            architecture,
            consistency,
            dependency,
            performance,
            safety,
            diagnostics,
            recommendations,
        )
        result = ArchitectureAuditRun(
            timestamp=datetime.now(UTC),
            certification=certification,
            architecture=architecture,
            consistency=consistency,
            dependency=dependency,
            performance=performance,
            safety=safety,
            analytics=analytics,
            diagnostics=diagnostics,
            recommendations=recommendations,
            metadata=metadata,
        )
        storage_paths = self.storage.save(result)
        report_paths = self.reports.export(result)
        return ArchitectureAuditRunResult(result, storage_paths, report_paths)

    def _metadata(self) -> dict[str, bool]:
        return {
            "architecture_audit_only": True,
            "hardening_only": True,
            "research_only": True,
            "local_only": True,
            "not_execution": True,
            "not_real_execution": True,
            "not_order_placement": True,
            "not_real_order_placement": True,
            "not_broker_access": True,
            "not_broker_api": True,
            "not_account_login": True,
            "not_authentication": True,
            "not_credential_handling": True,
            "not_browser_automation": True,
            "not_real_money": True,
            "not_money_handling": True,
            "not_position_management": True,
            "not_live_trading": True,
            "not_external_execution_adapter": True,
            "not_trading_automation": True,
            "not_broker_control": True,
        }
