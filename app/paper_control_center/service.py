"""Service orchestration for paper trading control center."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import UTC, datetime
import json
from pathlib import Path
from typing import Any

from app.paper_control_center.analytics import PaperControlAnalytics
from app.paper_control_center.control_center import PaperControlCenterEngine
from app.paper_control_center.diagnostics import PaperControlDiagnostics
from app.paper_control_center.governance import (
    PaperControlDecisionEngine,
    PaperControlGovernanceEngine,
)
from app.paper_control_center.health import PaperHealthEngine
from app.paper_control_center.models import FAIL, WARNING, PaperControlCenterRun
from app.paper_control_center.monitoring import PaperMonitoringEngine
from app.paper_control_center.recommendations import PaperControlRecommendations
from app.paper_control_center.reports import PaperControlReportWriter
from app.paper_control_center.storage import PaperControlStorage


@dataclass(frozen=True)
class PaperControlCenterRunResult:
    """Result of one paper control center run."""

    result: PaperControlCenterRun
    storage_paths: dict[str, str]
    report_paths: dict[str, str]


class PaperControlCenterService:
    """Consolidate paper trading research layers into an executive view."""

    def __init__(self, project_root: Path | str = ".") -> None:
        self.project_root = Path(project_root)
        self.health = PaperHealthEngine()
        self.monitoring = PaperMonitoringEngine()
        self.governance = PaperControlGovernanceEngine()
        self.decision = PaperControlDecisionEngine()
        self.control = PaperControlCenterEngine()
        self.diagnostics = PaperControlDiagnostics()
        self.recommendations = PaperControlRecommendations()
        self.analytics = PaperControlAnalytics()
        self.storage = PaperControlStorage(
            self.project_root / "storage" / "paper_control_center"
        )
        self.reports = PaperControlReportWriter(
            self.project_root / "reports" / "paper_control_center"
        )

    def run(self) -> PaperControlCenterRunResult:
        sources = self._sources()
        health = self.health.evaluate(sources)
        monitoring = self.monitoring.evaluate(sources)
        governance = self.governance.evaluate(health, monitoring)
        decision = self.decision.decide(health, governance)
        diagnostics = self.diagnostics.evaluate(sources, health, governance)
        recommendations = self.recommendations.generate(diagnostics)
        governance_status = self._aggregate_status(governance)
        control = self.control.build(
            health,
            monitoring,
            governance_status,
            decision,
            len(diagnostics),
            len(recommendations),
            self._metadata(),
        )
        analytics = self.analytics.summarize(
            control,
            health,
            monitoring,
            governance,
            decision,
            diagnostics,
        )
        result = PaperControlCenterRun(
            timestamp=datetime.now(UTC),
            control=control,
            health=health,
            monitoring=monitoring,
            governance=governance,
            decision=decision,
            analytics=analytics,
            diagnostics=diagnostics,
            recommendations=recommendations,
            metadata=self._metadata(),
        )
        storage_paths = self.storage.save(result)
        report_paths = self.reports.export(result)
        return PaperControlCenterRunResult(result, storage_paths, report_paths)

    def _sources(self) -> dict[str, Any]:
        return {
            "paper_portfolio": self._read_json(
                "reports",
                "paper_portfolio",
                "portfolio_summary.json",
            ),
            "paper_execution": self._read_json(
                "reports",
                "paper_execution",
                "paper_execution_summary.json",
            ),
            "execution_readiness": self._read_json(
                "reports",
                "execution_readiness",
                "execution_summary.json",
            ),
            "signal_stream": self._read_json(
                "reports",
                "signal_stream",
                "signal_summary.json",
            ),
            "trade_lifecycle": self._read_json(
                "reports",
                "trade_lifecycle",
                "summary.json",
            ),
            "confluence": self._read_json("reports", "confluence", "summary.json"),
            "research_ops": self._read_json(
                "reports",
                "research_ops",
                "operations_summary.json",
            ),
        }

    def _aggregate_status(self, governance: tuple[Any, ...]) -> str:
        if any(item.status == FAIL for item in governance):
            return FAIL
        if any(item.status == WARNING for item in governance):
            return WARNING
        return "PASS"

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
            "paper_only": True,
            "research_only": True,
            "control_center_only": True,
            "monitoring_only": True,
            "recommendation_only": True,
            "not_control_action": True,
            "not_real_execution": True,
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
            "not_trading_automation": True,
            "not_broker_control": True,
        }
