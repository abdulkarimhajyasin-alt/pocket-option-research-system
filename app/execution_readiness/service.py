"""Service orchestration for the research-only execution readiness framework."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import UTC, datetime
import json
from pathlib import Path
from typing import Any

from app.execution_readiness.analytics import ExecutionReadinessAnalytics
from app.execution_readiness.diagnostics import (
    ExecutionReadinessDiagnostics,
    ExecutionReadinessRecommendations,
)
from app.execution_readiness.gates import ExecutionGateEngine
from app.execution_readiness.models import ExecutionCandidate, ExecutionReadinessRun
from app.execution_readiness.qualification import ExecutionQualificationEngine
from app.execution_readiness.readiness import ExecutionReadinessEngine
from app.execution_readiness.reports import ExecutionReadinessReportWriter
from app.execution_readiness.scoring import ExecutionScoringEngine, average, clamp_score
from app.execution_readiness.storage import ExecutionReadinessStorage
from app.execution_readiness.validation import ExecutionReadinessValidation


@dataclass(frozen=True)
class ExecutionReadinessRunResult:
    """Result of one execution-readiness run."""

    result: ExecutionReadinessRun
    analytics: dict[str, Any]
    storage_paths: dict[str, str]
    report_paths: dict[str, str]


class ExecutionReadinessService:
    """Evaluate research signal readiness without execution capability."""

    def __init__(self, project_root: Path | str = ".") -> None:
        self.project_root = Path(project_root)
        self.readiness = ExecutionReadinessEngine()
        self.qualification = ExecutionQualificationEngine()
        self.gates = ExecutionGateEngine()
        self.scoring = ExecutionScoringEngine()
        self.validation = ExecutionReadinessValidation()
        self.diagnostics = ExecutionReadinessDiagnostics()
        self.recommendations = ExecutionReadinessRecommendations()
        self.analytics = ExecutionReadinessAnalytics()
        self.storage = ExecutionReadinessStorage(
            self.project_root / "storage" / "execution_readiness"
        )
        self.reports = ExecutionReadinessReportWriter(
            self.project_root / "reports" / "execution_readiness"
        )

    def run(self) -> ExecutionReadinessRunResult:
        context = self._context()
        candidates = self._load_candidates(context)
        readiness = self.readiness.evaluate(candidates, context)
        gates = self.gates.evaluate(candidates, readiness, context)
        scoring = self.scoring.evaluate(candidates, readiness)
        validation = self.validation.validate(candidates, readiness, gates, scoring)
        diagnostics = self.diagnostics.evaluate(candidates, readiness, gates)
        recommendations = self.recommendations.generate(diagnostics)
        result = ExecutionReadinessRun(
            timestamp=datetime.now(UTC),
            candidates=candidates,
            readiness=readiness,
            qualification=self.qualification.evaluate(candidates),
            gates=gates,
            scoring=scoring,
            validation=validation,
            diagnostics=diagnostics,
            recommendations=recommendations,
            metadata=self._metadata(),
        )
        analytics = self.analytics.summarize(result)
        storage_paths = self.storage.save(result, analytics)
        report_paths = self.reports.export(analytics)
        return ExecutionReadinessRunResult(result, analytics, storage_paths, report_paths)

    def _load_candidates(self, context: dict[str, Any]) -> tuple[ExecutionCandidate, ...]:
        events = self._signal_events()
        if not events:
            events = self._fallback_events()
        candidates: list[ExecutionCandidate] = []
        for index, event in enumerate(events, start=1):
            confidence = clamp_score(event.get("confidence", 0.0))
            quality = clamp_score(event.get("quality", confidence))
            confluence = average(
                [
                    context.get("confluence_score", 70.0),
                    context.get("multi_timeframe_score", 70.0),
                    context.get("opportunity_score", 70.0),
                    confidence,
                    quality,
                ]
            )
            readiness = average(
                [
                    confidence,
                    quality,
                    confluence,
                    context.get("regime_score", 75.0),
                    context.get("pattern_score", 75.0),
                ]
            )
            qualification = self.qualification.qualify_score(readiness)
            candidates.append(
                ExecutionCandidate(
                    candidate_id=f"execution_candidate_{index:04d}",
                    signal_id=str(event.get("signal_id") or f"signal_{index:04d}"),
                    asset=str(event.get("asset") or "research_asset"),
                    direction=str(event.get("direction") or "NO_TRADE"),
                    confidence=confidence,
                    quality=quality,
                    confluence=confluence,
                    readiness=readiness,
                    qualification=qualification,
                    timestamp=str(event.get("timestamp") or datetime.now(UTC).isoformat()),
                    metadata={**self._metadata(), "source": event.get("source", "local_report")},
                )
            )
        return tuple(candidates)

    def _signal_events(self) -> list[dict[str, Any]]:
        payload = self._read_json("reports", "signal_stream", "signal_summary.json")
        latest = payload.get("latest", {}) if isinstance(payload, dict) else {}
        stream = latest.get("stream", {}) if isinstance(latest, dict) else {}
        events = stream.get("events", []) if isinstance(stream, dict) else []
        return [item for item in events if isinstance(item, dict)]

    def _fallback_events(self) -> list[dict[str, Any]]:
        now = datetime.now(UTC).isoformat()
        return [
            {
                "signal_id": f"fallback_signal_{index:04d}",
                "asset": f"research_asset_{index}",
                "direction": direction,
                "confidence": confidence,
                "quality": quality,
                "timestamp": now,
                "source": "fallback_local_readiness",
            }
            for index, direction, confidence, quality in (
                (1, "CALL", 78.0, 74.0),
                (2, "PUT", 82.0, 80.0),
                (3, "NO_TRADE", 55.0, 60.0),
                (4, "CALL", 91.0, 88.0),
                (5, "NO_TRADE", 42.0, 50.0),
            )
        ]

    def _context(self) -> dict[str, Any]:
        return {
            "signal_intelligence_score": self._extract_score(
                self._read_json("reports", "signals_intelligence", "summary.json")
            ),
            "performance_score": self._extract_score(
                self._read_json("reports", "signal_performance", "summary.json")
            ),
            "opportunity_score": self._extract_score(
                self._read_json("reports", "opportunities", "summary.json")
            ),
            "multi_timeframe_score": self._extract_score(
                self._read_json("reports", "multi_timeframe", "alignment_summary.json")
            ),
            "confluence_score": self._extract_score(
                self._read_json("reports", "confluence", "summary.json")
            ),
            "lifecycle_score": self._extract_score(
                self._read_json("reports", "trade_lifecycle", "summary.json")
            ),
            "pattern_score": self._extract_score(
                self._read_json("reports", "pattern_memory", "summary.json")
            ),
            "regime_score": self._extract_score(
                self._read_json("reports", "market_regime", "summary.json")
            ),
            "certification_score": self._extract_score(
                self._read_json("reports", "research_certification", "summary.json")
            ),
        }

    def _extract_score(self, payload: Any) -> float:
        if not isinstance(payload, dict):
            return 75.0
        candidates = []
        for key in (
            "score",
            "average_score",
            "readiness_score",
            "quality_score",
            "certification_score",
            "validation_score",
        ):
            if key in payload:
                candidates.append(payload.get(key))
        summary = payload.get("summary")
        if isinstance(summary, dict):
            for key in (
                "score",
                "average_score",
                "readiness_score",
                "quality_score",
                "certification_score",
                "validation_score",
            ):
                if key in summary:
                    candidates.append(summary.get(key))
        for value in candidates:
            try:
                return clamp_score(float(value))
            except (TypeError, ValueError):
                continue
        return 75.0

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
            "research_only": True,
            "readiness_only": True,
            "future_paper_execution_readiness_only": True,
            "not_execution": True,
            "not_order_placement": True,
            "not_buy_sell_action": True,
            "not_money_management": True,
            "not_position_management": True,
            "not_account_login": True,
            "not_broker_authentication": True,
            "not_credential_handling": True,
            "not_browser_automation": True,
            "not_broker_control": True,
        }
