"""Signal performance analytics and research statistics."""

from __future__ import annotations

from collections import Counter, defaultdict
from statistics import mean
from typing import Any

from app.signal_performance.models import PaperOutcome, PaperTradeResult


class SignalPerformanceAnalytics:
    """Build deterministic performance analytics for research classifications."""

    def summarize(
        self,
        results: list[PaperTradeResult],
        confidence_validation: dict[str, Any],
    ) -> dict[str, Any]:
        total = len(results)
        wins = sum(1 for item in results if item.outcome.outcome == PaperOutcome.WIN)
        losses = sum(1 for item in results if item.outcome.outcome == PaperOutcome.LOSS)
        breakeven = sum(
            1 for item in results if item.outcome.outcome == PaperOutcome.BREAKEVEN
        )
        unresolved = sum(
            1 for item in results if item.outcome.outcome == PaperOutcome.UNRESOLVED
        )
        confidence = [item.signal.confidence for item in results]
        outcome_scores = [item.outcome.outcome_score for item in results]
        asset_perf = self._group_win_rate(results, "asset")
        session_perf = self._group_win_rate(results, "session_state")
        structure_perf = self._group_win_rate(results, "structure_state")
        confidence_perf = self._confidence_performance(results)
        stats = self._statistics(results, confidence_validation)
        return {
            "summary": {
                "total_signals": total,
                "wins": wins,
                "losses": losses,
                "breakeven": breakeven,
                "unresolved": unresolved,
                "win_rate": round(wins / total, 4) if total else 0.0,
                "loss_rate": round(losses / total, 4) if total else 0.0,
                "average_confidence": round(mean(confidence), 2) if confidence else 0.0,
                "average_outcome_score": round(mean(outcome_scores), 4)
                if outcome_scores
                else 0.0,
                "best_asset": self._best(asset_perf),
                "worst_asset": self._worst(asset_perf),
                "best_session": self._best(session_perf),
                "worst_session": self._worst(session_perf),
                "best_structure": self._best(structure_perf),
                "worst_structure": self._worst(structure_perf),
                "best_confidence_range": self._best(confidence_perf),
                "worst_confidence_range": self._worst(confidence_perf),
                **stats,
            },
            "outcomes": {
                "رابحة": wins,
                "خاسرة": losses,
                "تعادل": breakeven,
                "غير محسومة": unresolved,
            },
            "asset_performance": asset_perf,
            "session_performance": session_perf,
            "structure_performance": structure_perf,
            "confidence_performance": confidence_perf,
            "confidence_validation": confidence_validation,
            "timeline": self._timeline(results),
        }

    def _group_win_rate(
        self,
        results: list[PaperTradeResult],
        field: str,
    ) -> dict[str, float]:
        grouped: dict[str, list[PaperTradeResult]] = defaultdict(list)
        for result in results:
            key = getattr(result.signal, field)
            grouped[str(key)].append(result)
        return {
            key: self._win_rate(items)
            for key, items in sorted(grouped.items())
        }

    def _confidence_performance(self, results: list[PaperTradeResult]) -> dict[str, float]:
        ranges = {"0-39": [], "40-59": [], "60-79": [], "80-100": []}
        for result in results:
            score = result.signal.confidence
            if score < 40:
                ranges["0-39"].append(result)
            elif score < 60:
                ranges["40-59"].append(result)
            elif score < 80:
                ranges["60-79"].append(result)
            else:
                ranges["80-100"].append(result)
        return {key: self._win_rate(items) for key, items in ranges.items()}

    def _statistics(
        self,
        results: list[PaperTradeResult],
        confidence_validation: dict[str, Any],
    ) -> dict[str, Any]:
        scores = [item.outcome.outcome_score for item in results]
        signal_quality = round((mean(scores) if scores else 0.0) * 100, 2)
        consistency = round((1.0 - self._variance(scores)) * 100, 2) if scores else 0.0
        stability = round((signal_quality * 0.6 + consistency * 0.4), 2)
        confidence_accuracy = 85.0 if confidence_validation.get("balanced") else 62.0
        readiness = round(
            signal_quality * 0.35
            + consistency * 0.25
            + stability * 0.2
            + confidence_accuracy * 0.2,
            2,
        )
        return {
            "signal_quality_score": signal_quality,
            "consistency_score": max(0.0, min(100.0, consistency)),
            "stability_score": stability,
            "confidence_accuracy_score": confidence_accuracy,
            "validation_readiness_score": readiness,
            "readiness_label": self._readiness_label(readiness),
        }

    def _timeline(self, results: list[PaperTradeResult]) -> dict[str, float]:
        grouped = Counter(
            result.outcome.evaluation_timestamp.strftime("%H:%M")
            for result in results
            if result.outcome.outcome != PaperOutcome.UNRESOLVED
        )
        return dict(sorted(grouped.items()))

    def _win_rate(self, results: list[PaperTradeResult]) -> float:
        if not results:
            return 0.0
        wins = sum(1 for item in results if item.outcome.outcome == PaperOutcome.WIN)
        return round(wins / len(results), 4)

    def _best(self, values: dict[str, float]) -> str:
        return max(values, key=values.get) if values else "غير متاح"

    def _worst(self, values: dict[str, float]) -> str:
        return min(values, key=values.get) if values else "غير متاح"

    def _variance(self, values: list[float]) -> float:
        if not values:
            return 0.0
        average = mean(values)
        return mean([(value - average) ** 2 for value in values])

    def _readiness_label(self, score: float) -> str:
        if score >= 85:
            return "ممتاز"
        if score >= 70:
            return "جيد"
        if score >= 50:
            return "متوسط"
        return "ضعيف"
