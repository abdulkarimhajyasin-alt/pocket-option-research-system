"""Analytics for multi-timeframe confirmation."""

from __future__ import annotations

from collections import Counter, defaultdict
from statistics import mean
from typing import Any

from app.multi_timeframe.models import ConfirmationResult


class MultiTimeframeAnalytics:
    """Aggregate confirmation, alignment, conflict, and contribution metrics."""

    def summarize(self, results: list[ConfirmationResult]) -> dict[str, Any]:
        scores = [item.confirmation_score for item in results]
        confirmed = [item for item in results if item.confirmation_state in {"مؤكد بقوة", "مؤكد"}]
        conflicts = [item for item in results if item.conflict.has_conflict]
        return {
            "summary": {
                "confirmed_count": len(confirmed),
                "conflicting_count": len(conflicts),
                "average_alignment": round(mean(scores), 2) if scores else 0.0,
                "highest_alignment": round(max(scores), 2) if scores else 0.0,
                "lowest_alignment": round(min(scores), 2) if scores else 0.0,
                "research_only": True,
            },
            "alignment_distribution": self._counter(
                item.alignment.state_ar for item in results
            ),
            "confirmation_distribution": self._counter(
                item.confirmation_state for item in results
            ),
            "conflict_distribution": self._counter(
                item.conflict.severity for item in results
            ),
            "asset_alignment": self._average_by(results, "asset"),
            "session_alignment": self._session_alignment(results),
            "timeframe_contribution": self._timeframe_contribution(results),
            "timeline": self._timeline(results),
            "latest": [item.to_dict() for item in results[:20]],
            "best_confirmation": max(results, key=lambda item: item.confirmation_score).to_dict()
            if results
            else {},
        }

    def _counter(self, values) -> dict[str, int]:
        return dict(Counter(values))

    def _average_by(self, results: list[ConfirmationResult], field: str) -> dict[str, float]:
        grouped: dict[str, list[float]] = defaultdict(list)
        for item in results:
            grouped[str(getattr(item, field))].append(item.confirmation_score)
        return {key: round(mean(values), 2) for key, values in grouped.items()}

    def _session_alignment(self, results: list[ConfirmationResult]) -> dict[str, float]:
        grouped: dict[str, list[float]] = defaultdict(list)
        for item in results:
            grouped[item.session].append(item.confirmation_score)
        return {key: round(mean(values), 2) for key, values in grouped.items()}

    def _timeframe_contribution(self, results: list[ConfirmationResult]) -> dict[str, float]:
        grouped: dict[str, list[float]] = defaultdict(list)
        for item in results:
            for state in item.timeframe_states:
                grouped[state.timeframe].append(state.confidence)
        return {key: round(mean(values), 2) for key, values in sorted(grouped.items())}

    def _timeline(self, results: list[ConfirmationResult]) -> dict[str, float]:
        grouped: dict[str, list[float]] = defaultdict(list)
        for item in results:
            grouped[item.timestamp.strftime("%H:%M")].append(item.confirmation_score)
        return {key: round(mean(values), 2) for key, values in sorted(grouped.items())}
