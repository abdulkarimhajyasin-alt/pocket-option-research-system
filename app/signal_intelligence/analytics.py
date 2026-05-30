"""Analytics for research-only signal intelligence."""

from __future__ import annotations

from collections import Counter
from statistics import mean
from typing import Any

from app.signal_intelligence.models import SignalIntelligenceResult


class SignalAnalytics:
    """Aggregate signal intelligence outputs."""

    def summarize(self, signals: list[SignalIntelligenceResult]) -> dict[str, Any]:
        scores = [signal.confidence.score for signal in signals]
        classifications = Counter(signal.classification_ar for signal in signals)
        structures = Counter(signal.structure.state for signal in signals)
        cisd = Counter(signal.cisd.direction for signal in signals)
        fvg = Counter(signal.fvg.direction if signal.fvg else "لا يوجد" for signal in signals)
        liquidity = Counter(signal.liquidity.sweep_direction for signal in signals)
        sessions = {
            key: round(mean(values), 2)
            for key, values in self._session_scores(signals).items()
        }
        return {
            "summary": {
                "signal_count": len(signals),
                "average_confidence": round(mean(scores), 2) if scores else 0.0,
                "highest_confidence": round(max(scores), 2) if scores else 0.0,
                "signal_quality": self._quality(scores),
                "research_only": True,
            },
            "distribution": dict(classifications),
            "confidence_distribution": self._confidence_distribution(scores),
            "structure_distribution": dict(structures),
            "cisd_statistics": dict(cisd),
            "fvg_statistics": dict(fvg),
            "liquidity_statistics": dict(liquidity),
            "session_performance": sessions,
            "latest_signals": [signal.to_dict() for signal in signals[-10:]],
            "best_signal": self._best_signal(signals),
        }

    def _confidence_distribution(self, scores: list[float]) -> dict[str, int]:
        buckets = Counter({"ضعيفة": 0, "متوسطة": 0, "قوية": 0, "عالية الاقتناع": 0})
        for score in scores:
            if score < 40:
                buckets["ضعيفة"] += 1
            elif score < 60:
                buckets["متوسطة"] += 1
            elif score < 80:
                buckets["قوية"] += 1
            else:
                buckets["عالية الاقتناع"] += 1
        return dict(buckets)

    def _session_scores(
        self,
        signals: list[SignalIntelligenceResult],
    ) -> dict[str, list[float]]:
        grouped: dict[str, list[float]] = {}
        for signal in signals:
            grouped.setdefault(signal.session.session_name, []).append(
                signal.session.quality_score
            )
        return grouped

    def _quality(self, scores: list[float]) -> str:
        average = mean(scores) if scores else 0.0
        if average >= 80:
            return "عالية"
        if average >= 60:
            return "جيدة"
        if average >= 40:
            return "متوسطة"
        return "ضعيفة"

    def _best_signal(self, signals: list[SignalIntelligenceResult]) -> dict[str, Any]:
        if not signals:
            return {}
        return max(signals, key=lambda signal: signal.confidence.score).to_dict()
