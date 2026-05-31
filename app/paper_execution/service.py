"""Service orchestration for paper-only execution."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import UTC, datetime
import json
from pathlib import Path
from typing import Any

from app.paper_execution.diagnostics import (
    PaperExecutionDiagnostics,
    PaperExecutionRecommendations,
)
from app.paper_execution.engine import PaperExecutionEngine
from app.paper_execution.models import PaperExecutionRun
from app.paper_execution.reports import PaperExecutionReportWriter
from app.paper_execution.storage import PaperExecutionStorage


@dataclass(frozen=True)
class PaperExecutionRunResult:
    """Result of one paper execution run."""

    result: PaperExecutionRun
    storage_paths: dict[str, str]
    report_paths: dict[str, str]


class PaperExecutionService:
    """Run local paper-only execution from readiness candidates."""

    def __init__(self, project_root: Path | str = ".") -> None:
        self.project_root = Path(project_root)
        self.engine = PaperExecutionEngine()
        self.diagnostics = PaperExecutionDiagnostics()
        self.recommendations = PaperExecutionRecommendations()
        self.storage = PaperExecutionStorage(
            self.project_root / "storage" / "paper_execution"
        )
        self.reports = PaperExecutionReportWriter(
            self.project_root / "reports" / "paper_execution"
        )

    def run(self) -> PaperExecutionRunResult:
        candidates = self._execution_candidates()
        context = self._context()
        engine_result = self.engine.run(candidates, context)
        diagnostics = self.diagnostics.evaluate(
            engine_result.orders,
            engine_result.results,
            engine_result.risk_gates,
            engine_result.analytics,
        )
        recommendations = self.recommendations.generate(diagnostics)
        result = PaperExecutionRun(
            timestamp=datetime.now(UTC),
            orders=engine_result.orders,
            lifecycle=engine_result.lifecycle,
            results=engine_result.results,
            risk_gates=engine_result.risk_gates,
            analytics={
                **engine_result.analytics,
                "paper_execution_score": engine_result.score,
                "warning_count": len(diagnostics),
                "recommendation_count": len(recommendations),
            },
            diagnostics=diagnostics,
            recommendations=recommendations,
            score=engine_result.score,
            metadata=self._metadata(),
        )
        storage_paths = self.storage.save(result)
        report_paths = self.reports.export(result)
        return PaperExecutionRunResult(result, storage_paths, report_paths)

    def _execution_candidates(self) -> list[dict[str, Any]]:
        summary = self._read_json(
            "reports",
            "execution_readiness",
            "execution_summary.json",
        )
        latest = summary.get("latest", {}) if isinstance(summary, dict) else {}
        candidates = latest.get("candidates", []) if isinstance(latest, dict) else []
        if isinstance(candidates, list) and candidates:
            return [item for item in candidates if isinstance(item, dict)]
        stored = self._read_json(
            "storage",
            "execution_readiness",
            "execution_candidates.json",
        )
        if isinstance(stored, list) and stored:
            return [item for item in stored if isinstance(item, dict)]
        now = datetime.now(UTC).isoformat()
        return [
            {
                "candidate_id": f"paper_fallback_{index:04d}",
                "signal_id": f"paper_signal_{index:04d}",
                "asset": "paper_asset",
                "direction": direction,
                "confidence": confidence,
                "readiness": readiness,
                "qualification": "مؤهل بشروط",
                "timestamp": now,
            }
            for index, direction, confidence, readiness in (
                (1, "CALL", 78.0, 76.0),
                (2, "PUT", 82.0, 80.0),
                (3, "NO_TRADE", 55.0, 60.0),
                (4, "CALL", 91.0, 88.0),
                (5, "PUT", 66.0, 70.0),
            )
        ]

    def _context(self) -> dict[str, Any]:
        return {
            "signal_stream_score": self._extract_score(
                self._read_json("reports", "signal_stream", "signal_summary.json")
            ),
            "trade_lifecycle_score": self._extract_score(
                self._read_json("reports", "trade_lifecycle", "summary.json")
            ),
            "confluence_score": self._extract_score(
                self._read_json("reports", "confluence", "summary.json")
            ),
            "market_observation_score": self._extract_score(
                self._read_json("reports", "market_observation", "observation_summary.json")
            ),
        }

    def _extract_score(self, payload: Any) -> float:
        if not isinstance(payload, dict):
            return 70.0
        summary = payload.get("summary", payload)
        if not isinstance(summary, dict):
            summary = payload
        for key in (
            "score",
            "readiness_score",
            "quality_score",
            "average_score",
            "validation_score",
        ):
            if key in summary:
                try:
                    return max(0.0, min(100.0, float(summary[key])))
                except (TypeError, ValueError):
                    continue
        return 70.0

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
            "local_simulation_only": True,
            "not_real_execution": True,
            "not_real_order_placement": True,
            "not_buy_sell_action": True,
            "not_broker_access": True,
            "not_broker_api": True,
            "not_pocket_option_integration": True,
            "not_account_login": True,
            "not_authentication": True,
            "not_credential_handling": True,
            "not_browser_automation": True,
            "not_real_money": True,
            "not_position_management": True,
            "not_trading_automation": True,
            "not_broker_control": True,
        }
