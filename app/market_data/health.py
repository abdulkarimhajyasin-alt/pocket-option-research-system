"""Health scoring for research-only market data providers."""

from __future__ import annotations

from statistics import mean

from app.market_data.models import MarketDataHealth, MarketSnapshot


class MarketHealthScorer:
    """Score infrastructure readiness without trading or profitability claims."""

    def score(self, snapshot: MarketSnapshot) -> MarketDataHealth:
        """Return deterministic provider health."""
        asset_quality = [asset.quality_score for asset in snapshot.assets]
        coverage = [status.coverage_score for status in snapshot.statuses]
        latencies = [latency.latency_ms for latency in snapshot.latencies]
        quality_score = mean(asset_quality) if asset_quality else 0.0
        coverage_score = mean(coverage) if coverage else 0.0
        average_latency = mean(latencies) if latencies else 0.0
        latency_penalty = max(0.0, average_latency - 35.0) * 0.25
        raw_score = quality_score * 0.55 + coverage_score * 0.45 - latency_penalty
        score = round(max(0.0, min(100.0, raw_score)), 2)
        return MarketDataHealth(
            timestamp=snapshot.timestamp,
            provider=snapshot.provider,
            asset="ALL",
            timeframe="provider",
            metadata={"research_only": True},
            score=score,
            label=self.label(score),
            readiness_score=score,
            readiness_label=self.readiness(score),
        )

    def label(self, score: float) -> str:
        if score >= 90:
            return "ممتاز"
        if score >= 75:
            return "جيد"
        if score >= 55:
            return "متوسط"
        return "ضعيف"

    def readiness(self, score: float) -> str:
        if score >= 85:
            return "جاهز للبحث"
        if score >= 70:
            return "مستقر للبحث"
        if score >= 50:
            return "يحتاج مراقبة"
        return "غير جاهز"
