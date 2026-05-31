"""Service orchestration for paper-to-live readiness gate."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import UTC, datetime
import json
from pathlib import Path
from typing import Any

from app.paper_live_readiness.analytics import PaperToLiveAnalytics
from app.paper_live_readiness.diagnostics import PaperToLiveDiagnostics
from app.paper_live_readiness.gates import PaperToLiveGateEngine
from app.paper_live_readiness.maturity import PaperToLiveMaturityEngine
from app.paper_live_readiness.models import PaperToLiveReadinessRun
from app.paper_live_readiness.readiness import PaperToLiveReadinessEngine
from app.paper_live_readiness.recommendations import PaperToLiveRecommendations
from app.paper_live_readiness.reports import PaperToLiveReadinessReportWriter
from app.paper_live_readiness.safety import PaperToLiveSafetyEngine
from app.paper_live_readiness.stability import PaperToLiveStabilityEngine
from app.paper_live_readiness.storage import PaperToLiveReadinessStorage


@dataclass(frozen=True)
class PaperToLiveReadinessRunResult:
    """Result of one readiness-only run."""

    result: PaperToLiveReadinessRun
    storage_paths: dict[str, str]
    report_paths: dict[str, str]


class PaperToLiveReadinessService:
    """Assess readiness for a future observation-preparation phase only."""

    def __init__(self, project_root: Path | str = ".") -> None:
        self.project_root = Path(project_root)
        self.safety = PaperToLiveSafetyEngine()
        self.maturity = PaperToLiveMaturityEngine()
        self.stability = PaperToLiveStabilityEngine()
        self.readiness = PaperToLiveReadinessEngine()
        self.gates = PaperToLiveGateEngine()
        self.diagnostics = PaperToLiveDiagnostics()
        self.recommendations = PaperToLiveRecommendations()
        self.analytics = PaperToLiveAnalytics()
        self.storage = PaperToLiveReadinessStorage(
            self.project_root / "storage" / "paper_live_readiness"
        )
        self.reports = PaperToLiveReadinessReportWriter(
            self.project_root / "reports" / "paper_live_readiness"
        )

    def run(self) -> PaperToLiveReadinessRunResult:
        metadata = self._metadata()
        sources = self._sources()
        safety = self.safety.evaluate(metadata)
        maturity = self.maturity.evaluate(sources)
        stability = self.stability.evaluate(sources)
        readiness = self.readiness.evaluate(
            sources,
            safety,
            maturity,
            stability,
            metadata,
        )
        readiness_scores = {
            "paper_health": readiness.paper_health,
            "paper_stability": readiness.paper_stability,
            "paper_governance": readiness.paper_governance,
            "execution_readiness": readiness.execution_readiness,
            "observation_readiness": readiness.observation_readiness,
            "certification_score": readiness.certification_score,
            "safety_score": readiness.safety_score,
        }
        gates = self.gates.evaluate(readiness_scores, safety)
        diagnostics = self.diagnostics.evaluate(
            readiness_scores,
            gates,
            safety,
            maturity,
            stability,
        )
        recommendations = self.recommendations.generate(diagnostics)
        analytics = self.analytics.summarize(
            readiness,
            gates,
            safety,
            maturity,
            stability,
            diagnostics,
        )
        result = PaperToLiveReadinessRun(
            timestamp=datetime.now(UTC),
            readiness=readiness,
            gates=gates,
            safety=safety,
            maturity=maturity,
            stability=stability,
            analytics=analytics,
            diagnostics=diagnostics,
            recommendations=recommendations,
            metadata=metadata,
        )
        storage_paths = self.storage.save(result)
        report_paths = self.reports.export(result)
        return PaperToLiveReadinessRunResult(result, storage_paths, report_paths)

    def readiness_explanation(self, score: float) -> str:
        """Return Arabic explanation for a readiness score."""
        return self.readiness.explanation_for_score(score)

    def _sources(self) -> dict[str, Any]:
        return {
            "paper_control_center": self._read_json(
                "reports",
                "paper_control_center",
                "control_center_summary.json",
            ),
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
            "research_certification": self._read_json(
                "reports",
                "research_certification",
                "certification_summary.json",
            ),
            "broker_readiness": self._read_json(
                "reports",
                "broker_readiness",
                "readiness_summary.json",
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
            "readiness_only": True,
            "paper_only": True,
            "research_only": True,
            "assessment_only": True,
            "recommendation_only": True,
            "not_execution": True,
            "not_real_execution": True,
            "not_order_placement": True,
            "not_real_order_placement": True,
            "not_buy_sell_action": True,
            "not_live_trading": True,
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
            "not_pocket_option_integration": True,
        }
