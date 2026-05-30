"""Confidence model validation for research signals."""

from __future__ import annotations

from app.signal_performance.models import ConfidenceValidationReport, PaperOutcome, PaperTradeResult


class ConfidenceValidationEngine:
    """Compare confidence buckets with historical paper outcomes."""

    def validate(self, results: list[PaperTradeResult]) -> ConfidenceValidationReport:
        buckets = {
            "80-100": self._bucket(results, 80, 100),
            "60-79": self._bucket(results, 60, 79.999),
            "40-59": self._bucket(results, 40, 59.999),
            "0-39": self._bucket(results, 0, 39.999),
        }
        high = buckets["80-100"]["win_rate"]
        mid = buckets["60-79"]["win_rate"]
        low = buckets["40-59"]["win_rate"]
        overconfidence = high < mid and buckets["80-100"]["count"] > 0
        underconfidence = low > mid and buckets["40-59"]["count"] > 0
        balanced = not overconfidence and not underconfidence
        assessment = (
            "ثقة متوازنة"
            if balanced
            else "ثقة مفرطة"
            if overconfidence
            else "ثقة أقل من الأداء"
        )
        return ConfidenceValidationReport(
            buckets=buckets,
            assessment=assessment,
            overconfidence=overconfidence,
            underconfidence=underconfidence,
            balanced=balanced,
        )

    def _bucket(
        self,
        results: list[PaperTradeResult],
        minimum: float,
        maximum: float,
    ) -> dict[str, float]:
        items = [
            result
            for result in results
            if minimum <= result.signal.confidence <= maximum
        ]
        wins = sum(1 for result in items if result.outcome.outcome == PaperOutcome.WIN)
        count = len(items)
        return {
            "count": float(count),
            "wins": float(wins),
            "win_rate": round(wins / count, 4) if count else 0.0,
        }
