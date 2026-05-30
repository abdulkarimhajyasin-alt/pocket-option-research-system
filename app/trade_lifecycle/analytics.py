"""Analytics for research trade lifecycle simulation."""

from __future__ import annotations

from collections import Counter, defaultdict
from statistics import mean
from typing import Any

from app.trade_lifecycle.models import TradeLifecycleRecord


class TradeLifecycleAnalytics:
    """Aggregate lifecycle, outcome, quality, and factor impact metrics."""

    def summarize(self, records: list[TradeLifecycleRecord]) -> dict[str, Any]:
        quality_scores = [item.quality.score for item in records]
        outcomes = [item.outcome.outcome for item in records]
        wins = outcomes.count("WIN")
        losses = outcomes.count("LOSS")
        breakeven = outcomes.count("BREAKEVEN")
        return {
            "summary": {
                "total_lifecycles": len(records),
                "wins": wins,
                "losses": losses,
                "breakeven": breakeven,
                "average_quality": round(mean(quality_scores), 2)
                if quality_scores
                else 0.0,
                "best_asset": self._best(self._asset_performance(records)),
                "best_session": self._best(self._session_performance(records)),
                "research_only": True,
            },
            "lifecycle_distribution": self._state_distribution(records),
            "state_distribution": self._state_distribution(records),
            "outcome_distribution": dict(Counter(outcomes)),
            "entry_quality_distribution": self._bucket(
                [item.entry.readiness_score for item in records]
            ),
            "expiry_distribution": dict(Counter(item.expiry.expiry for item in records)),
            "asset_performance": self._asset_performance(records),
            "session_performance": self._session_performance(records),
            "confluence_performance": self._impact(records, "confluence_score"),
            "confidence_performance": self._impact(records, "confidence"),
            "quality_distribution": self._bucket(quality_scores),
            "timeframe_impact": self._impact(records, "timeframe_score"),
            "success_factors": self._success_factors(records),
            "failure_factors": self._failure_factors(records),
            "timeline": self._timeline(records),
            "latest": [item.to_dict() for item in records[:20]],
            "best_lifecycle": max(records, key=lambda item: item.quality.score).to_dict()
            if records
            else {},
        }

    def _state_distribution(self, records: list[TradeLifecycleRecord]) -> dict[str, int]:
        return dict(Counter(item.state.current for item in records))

    def _asset_performance(self, records: list[TradeLifecycleRecord]) -> dict[str, float]:
        return self._average_by(records, "asset")

    def _session_performance(self, records: list[TradeLifecycleRecord]) -> dict[str, float]:
        values: dict[str, list[float]] = defaultdict(list)
        for record in records:
            session = record.expiry.expiry
            values[session].append(record.quality.score)
        return {key: round(mean(items), 2) for key, items in values.items()}

    def _average_by(
        self,
        records: list[TradeLifecycleRecord],
        field: str,
    ) -> dict[str, float]:
        values: dict[str, list[float]] = defaultdict(list)
        for record in records:
            values[str(getattr(record, field))].append(record.quality.score)
        return {key: round(mean(items), 2) for key, items in values.items()}

    def _impact(self, records: list[TradeLifecycleRecord], field: str) -> dict[str, float]:
        values = [float(getattr(record, field)) for record in records]
        return self._bucket(values)

    def _bucket(self, values: list[float]) -> dict[str, int]:
        buckets = {
            "استثنائية": 0,
            "قوية جدا": 0,
            "قوية": 0,
            "متوسطة": 0,
            "ضعيفة": 0,
            "مرفوضة": 0,
        }
        for value in values:
            if value >= 95:
                buckets["استثنائية"] += 1
            elif value >= 85:
                buckets["قوية جدا"] += 1
            elif value >= 75:
                buckets["قوية"] += 1
            elif value >= 60:
                buckets["متوسطة"] += 1
            elif value >= 40:
                buckets["ضعيفة"] += 1
            else:
                buckets["مرفوضة"] += 1
        return buckets

    def _success_factors(self, records: list[TradeLifecycleRecord]) -> dict[str, int]:
        counter: Counter[str] = Counter()
        for record in records:
            if record.outcome.outcome == "WIN":
                for item in record.post_trade.success_reasons:
                    counter[item] += 1
        return dict(counter)

    def _failure_factors(self, records: list[TradeLifecycleRecord]) -> dict[str, int]:
        counter: Counter[str] = Counter()
        for record in records:
            if record.outcome.outcome in {"LOSS", "UNRESOLVED"}:
                for item in record.post_trade.failure_reasons:
                    counter[item] += 1
        return dict(counter)

    def _timeline(self, records: list[TradeLifecycleRecord]) -> dict[str, float]:
        values: dict[str, list[float]] = defaultdict(list)
        for record in records:
            values[record.created_at.strftime("%H:%M")].append(record.quality.score)
        return {key: round(mean(items), 2) for key, items in sorted(values.items())}

    def _best(self, values: dict[str, float]) -> str:
        return max(values, key=values.get) if values else "غير متاح"
