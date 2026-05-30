"""Analytics for provider-based market data integration."""

from __future__ import annotations

from collections import Counter
from statistics import mean
from typing import Any

from app.market_data.health import MarketHealthScorer
from app.market_data.models import MarketSnapshot


class MarketAnalytics:
    """Generate deterministic market-data infrastructure metrics."""

    def summarize(self, snapshot: MarketSnapshot) -> dict[str, Any]:
        """Return market-data analytics for reports and dashboards."""
        health = MarketHealthScorer().score(snapshot)
        active_assets = [asset for asset in snapshot.assets if asset.is_active]
        latency_values = [latency.latency_ms for latency in snapshot.latencies]
        coverage_values = [status.coverage_score for status in snapshot.statuses]
        asset_quality = {
            asset.asset: round(asset.quality_score, 2)
            for asset in sorted(snapshot.assets, key=lambda item: item.asset)
        }
        session_activity = {
            session.name: round(session.activity_score, 2)
            for session in snapshot.sessions
        }
        status_distribution = Counter(status.status for status in snapshot.statuses)
        update_frequency = round(
            mean([status.update_frequency for status in snapshot.statuses]),
            4,
        ) if snapshot.statuses else 0.0
        feed_quality_score = round(
            (mean(coverage_values) if coverage_values else 0.0) * 0.6
            + (mean(asset_quality.values()) if asset_quality else 0.0) * 0.4,
            2,
        )
        return {
            "summary": {
                "timestamp": snapshot.timestamp.isoformat(),
                "provider": snapshot.provider,
                "research_only": True,
                "active_assets": len(active_assets),
                "asset_count": len(snapshot.assets),
                "market_status": self._market_status(status_distribution),
                "market_coverage": round(mean(coverage_values), 2)
                if coverage_values
                else 0.0,
                "update_frequency": update_frequency,
                "average_latency_ms": round(mean(latency_values), 2)
                if latency_values
                else 0.0,
                "asset_quality_score": round(mean(asset_quality.values()), 2)
                if asset_quality
                else 0.0,
                "feed_quality_score": feed_quality_score,
                "readiness_score": health.readiness_score,
                "readiness_label": health.readiness_label,
                "provider_health": health.label,
                "provider_health_score": health.score,
            },
            "health": health.to_dict(),
            "latency": [latency.to_dict() for latency in snapshot.latencies],
            "assets": [asset.to_dict() for asset in snapshot.assets],
            "sessions": [session.to_dict() for session in snapshot.sessions],
            "quality": {
                "asset_quality": asset_quality,
                "feed_quality": {
                    "جودة الأصول": round(mean(asset_quality.values()), 2)
                    if asset_quality
                    else 0.0,
                    "تغطية السوق": round(mean(coverage_values), 2)
                    if coverage_values
                    else 0.0,
                    "جودة البث": feed_quality_score,
                    "جاهزية البنية": health.readiness_score,
                },
                "market_status": dict(status_distribution),
                "session_activity": session_activity,
                "time_activity": self._time_activity(snapshot),
            },
        }

    def _market_status(self, distribution: Counter[str]) -> str:
        if distribution.get("مفتوح", 0) >= 1:
            return "مفتوح"
        if distribution:
            return "مراقبة فقط"
        return "غير متاح"

    def _time_activity(self, snapshot: MarketSnapshot) -> dict[str, int]:
        buckets = Counter(candle.timestamp.strftime("%H:%M") for candle in snapshot.candles)
        return dict(sorted(buckets.items()))
