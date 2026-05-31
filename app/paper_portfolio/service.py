"""Service orchestration for paper portfolio governance."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import UTC, datetime
import json
from pathlib import Path
from typing import Any

from app.paper_portfolio.analytics import PaperPortfolioAnalytics
from app.paper_portfolio.diagnostics import (
    PaperPortfolioDiagnostics,
    PaperPortfolioRecommendations,
)
from app.paper_portfolio.drawdown import PaperDrawdownEngine
from app.paper_portfolio.exposure import PaperExposureEngine
from app.paper_portfolio.governance import PaperRiskGovernanceEngine
from app.paper_portfolio.limits import PaperLimitEngine
from app.paper_portfolio.models import PaperPortfolioRun
from app.paper_portfolio.portfolio import PaperPortfolioEngine
from app.paper_portfolio.reports import PaperPortfolioReportWriter
from app.paper_portfolio.storage import PaperPortfolioStorage


@dataclass(frozen=True)
class PaperPortfolioRunResult:
    """Result of one paper portfolio governance run."""

    result: PaperPortfolioRun
    storage_paths: dict[str, str]
    report_paths: dict[str, str]


class PaperPortfolioService:
    """Evaluate paper execution results as a simulated portfolio."""

    def __init__(self, project_root: Path | str = ".") -> None:
        self.project_root = Path(project_root)
        self.exposure = PaperExposureEngine()
        self.drawdown = PaperDrawdownEngine()
        self.portfolio = PaperPortfolioEngine()
        self.governance = PaperRiskGovernanceEngine()
        self.limits = PaperLimitEngine()
        self.analytics = PaperPortfolioAnalytics()
        self.diagnostics = PaperPortfolioDiagnostics()
        self.recommendations = PaperPortfolioRecommendations()
        self.storage = PaperPortfolioStorage(
            self.project_root / "storage" / "paper_portfolio"
        )
        self.reports = PaperPortfolioReportWriter(
            self.project_root / "reports" / "paper_portfolio"
        )

    def run(self) -> PaperPortfolioRunResult:
        orders = self._paper_orders()
        results = self._paper_results()
        exposure = self.exposure.evaluate(orders)
        drawdown = self.drawdown.evaluate(results)
        portfolio = self.portfolio.evaluate(
            orders,
            results,
            drawdown,
            exposure,
            self._metadata(),
        )
        governance = self.governance.evaluate(portfolio, exposure, orders, results)
        limits = self.limits.evaluate(portfolio, exposure, drawdown, results)
        analytics = self.analytics.summarize(
            portfolio,
            exposure,
            drawdown,
            governance,
            limits,
        )
        diagnostics = self.diagnostics.evaluate(
            portfolio,
            exposure,
            drawdown,
            governance,
            limits,
        )
        recommendations = self.recommendations.generate(diagnostics)
        score = self._score(portfolio, exposure, drawdown, governance, limits)
        run = PaperPortfolioRun(
            timestamp=datetime.now(UTC),
            portfolio=portfolio,
            exposure=exposure,
            drawdown=drawdown,
            governance=governance,
            limits=limits,
            analytics={
                **analytics,
                "portfolio_score": score,
                "warning_count": len(diagnostics),
                "recommendation_count": len(recommendations),
                "summary": portfolio.to_dict(),
            },
            diagnostics=diagnostics,
            recommendations=recommendations,
            score=score,
            metadata=self._metadata(),
        )
        storage_paths = self.storage.save(run)
        report_paths = self.reports.export(run)
        return PaperPortfolioRunResult(run, storage_paths, report_paths)

    def _paper_orders(self) -> list[dict[str, Any]]:
        return self._json_list("storage", "paper_execution", "paper_orders.json")

    def _paper_results(self) -> list[dict[str, Any]]:
        return self._json_list("storage", "paper_execution", "paper_results.json")

    def _json_list(self, *parts: str) -> list[dict[str, Any]]:
        payload = self._read_json(*parts)
        if isinstance(payload, list):
            return [item for item in payload if isinstance(item, dict)]
        return []

    def _read_json(self, *parts: str) -> Any:
        path = self.project_root.joinpath(*parts)
        if not path.exists():
            return {}
        try:
            return json.loads(path.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError):
            return {}

    def _score(
        self,
        portfolio: Any,
        exposure: dict[str, Any],
        drawdown: dict[str, Any],
        governance: tuple[Any, ...],
        limits: tuple[Any, ...],
    ) -> float:
        gate_scores = [item.score for item in governance + limits]
        governance_score = sum(gate_scores) / len(gate_scores) if gate_scores else 0.0
        score = (
            portfolio.health_score
            + portfolio.stability_score
            + portfolio.risk_score
            + float(exposure.get("exposure_score", 0.0))
            + float(drawdown.get("drawdown_score", 0.0))
            + governance_score
        ) / 6
        return round(max(0.0, min(100.0, score)), 2)

    def _metadata(self) -> dict[str, bool]:
        return {
            "paper_only": True,
            "research_only": True,
            "portfolio_simulation_only": True,
            "not_real_execution": True,
            "not_real_order_placement": True,
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
