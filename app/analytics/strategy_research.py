"""Analytics for explainable strategy research decisions."""

from __future__ import annotations

import csv
import json
from collections import Counter, defaultdict
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

from loguru import logger

from app.strategies.research.models import StrategyDecision


@dataclass(frozen=True)
class StrategyResearchSnapshot:
    """Aggregated analytics for strategy research decisions."""

    strategy_name: str
    total_decisions: int
    generated_signals: int
    evidence_frequency: dict[str, int]
    average_confidence_by_evidence: dict[str, float]
    rejection_reasons: dict[str, int]
    decision_distribution: dict[str, int]
    bullish_signals: int
    bearish_signals: int
    session_quality: dict[str, dict[str, float | int]] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        """Return serializable research analytics."""
        return {
            "strategy_name": self.strategy_name,
            "total_decisions": self.total_decisions,
            "generated_signals": self.generated_signals,
            "evidence_frequency": self.evidence_frequency,
            "average_confidence_by_evidence": self.average_confidence_by_evidence,
            "rejection_reasons": self.rejection_reasons,
            "decision_distribution": self.decision_distribution,
            "bullish_signals": self.bullish_signals,
            "bearish_signals": self.bearish_signals,
            "session_quality": self.session_quality,
        }


class StrategyResearchAnalyzer:
    """Analyze evidence, rejections, direction balance, and session quality."""

    def analyze(self, decisions: list[StrategyDecision]) -> StrategyResearchSnapshot:
        """Build a research analytics snapshot."""
        strategy_name = decisions[-1].strategy_name if decisions else "unknown"
        evidence_frequency: Counter[str] = Counter()
        confidence_by_evidence: dict[str, list[float]] = defaultdict(list)
        rejections: Counter[str] = Counter()
        distribution: Counter[str] = Counter()
        session_counts: dict[str, dict[str, float | int]] = defaultdict(
            lambda: {"decisions": 0, "signals": 0, "confidence_total": 0.0}
        )

        for decision in decisions:
            key = "signal" if decision.generated_signal else "rejected"
            distribution[key] += 1
            session = "unknown"
            for evidence in decision.evidence:
                evidence_frequency[evidence.name] += 1
                confidence_by_evidence[evidence.name].append(decision.confidence)
                if evidence.name == "session_allowed":
                    session = str(evidence.metadata.get("session", "allowed"))
            for rejection in decision.rejections:
                rejections[rejection.reason] += 1
            session_counts[session]["decisions"] += 1
            if decision.generated_signal:
                session_counts[session]["signals"] += 1
                session_counts[session]["confidence_total"] += decision.confidence

        averages = {
            name: round(sum(values) / len(values), 4)
            for name, values in confidence_by_evidence.items()
            if values
        }
        session_quality = {}
        for session, values in session_counts.items():
            signals = int(values["signals"])
            session_quality[session] = {
                "decisions": int(values["decisions"]),
                "signals": signals,
                "average_confidence": (
                    round(float(values["confidence_total"]) / signals, 4) if signals else 0.0
                ),
            }

        return StrategyResearchSnapshot(
            strategy_name=strategy_name,
            total_decisions=len(decisions),
            generated_signals=sum(1 for decision in decisions if decision.generated_signal),
            evidence_frequency=dict(evidence_frequency),
            average_confidence_by_evidence=averages,
            rejection_reasons=dict(rejections),
            decision_distribution=dict(distribution),
            bullish_signals=sum(
                1
                for decision in decisions
                if decision.direction and decision.direction.value == "call"
            ),
            bearish_signals=sum(
                1
                for decision in decisions
                if decision.direction and decision.direction.value == "put"
            ),
            session_quality=session_quality,
        )


class StrategyResearchExporter:
    """Export strategy research reports."""

    def __init__(self, export_dir: Path | str = "reports/strategy_research") -> None:
        self.export_dir = Path(export_dir)
        self.export_dir.mkdir(parents=True, exist_ok=True)

    def export(
        self,
        snapshot: StrategyResearchSnapshot,
        decisions: list[StrategyDecision],
        run_name: str,
    ) -> dict[str, Path]:
        """Export snapshot and decision rows."""
        json_path = self.export_dir / f"{run_name}_summary.json"
        decisions_path = self.export_dir / f"{run_name}_decisions.json"
        csv_path = self.export_dir / f"{run_name}_decisions.csv"
        json_path.write_text(json.dumps(snapshot.to_dict(), indent=2), encoding="utf-8")
        decisions_path.write_text(
            json.dumps([decision.to_dict() for decision in decisions], indent=2),
            encoding="utf-8",
        )
        rows = [
            {
                "timestamp": decision.timestamp.isoformat(),
                "symbol": decision.symbol,
                "timeframe": decision.timeframe,
                "direction": decision.direction.value if decision.direction else "",
                "confidence": round(decision.confidence, 4),
                "generated_signal": decision.generated_signal,
                "rejections": "|".join(item.reason for item in decision.rejections),
                "evidence": "|".join(item.name for item in decision.evidence),
            }
            for decision in decisions
        ]
        with csv_path.open("w", encoding="utf-8", newline="") as file:
            writer = csv.DictWriter(
                file, fieldnames=list(rows[0].keys()) if rows else ["timestamp"]
            )
            writer.writeheader()
            writer.writerows(rows)
        logger.bind(component="strategy_research").info(
            "Strategy research reports exported to {}",
            self.export_dir,
        )
        return {"summary": json_path, "decisions": decisions_path, "csv": csv_path}
