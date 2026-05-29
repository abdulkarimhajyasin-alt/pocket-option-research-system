"""Monitoring service for read-only external feed integrations."""

from __future__ import annotations

from datetime import datetime

from loguru import logger

from app.external_data.models import (
    ExternalDataPayload,
    FeedLatencyMetrics,
    FeedQualityMetrics,
    FeedSnapshot,
    FeedStatus,
    utc_now,
)
from app.external_data.quality_analyzer import FeedQualityAnalyzer


class ExternalFeedMonitor:
    """Track feed uptime, health, latency trends, reconnects, and quality degradation."""

    def __init__(
        self,
        source: str,
        analyzer: FeedQualityAnalyzer | None = None,
        quality_threshold: float = 80.0,
    ) -> None:
        self.source = source
        self.analyzer = analyzer or FeedQualityAnalyzer()
        self.quality_threshold = quality_threshold
        self.started_at: datetime | None = None
        self.stopped_at: datetime | None = None
        self.status = FeedStatus.STOPPED
        self.reconnect_attempts = 0
        self.payloads: list[ExternalDataPayload] = []
        self.latency_trend_ms: list[float] = []

    def start(self) -> None:
        """Start feed monitoring."""
        self.started_at = utc_now()
        self.status = FeedStatus.RUNNING
        logger.bind(component="external_data").info("External feed monitor started {}", self.source)

    def stop(self) -> None:
        """Stop feed monitoring."""
        self.stopped_at = utc_now()
        self.status = FeedStatus.STOPPED
        logger.bind(component="external_data").info("External feed monitor stopped {}", self.source)

    def record_payload(self, payload: ExternalDataPayload) -> None:
        """Record a normalized payload sample."""
        self.payloads.append(payload)
        self.latency_trend_ms.append(payload.latency_ms)
        quality = self.analyzer.analyze(self.payloads[-200:])
        if quality.quality_score < self.quality_threshold:
            self.status = FeedStatus.DEGRADED
            logger.bind(component="external_data").warning(
                "External feed quality degraded source={} score={}",
                self.source,
                quality.quality_score,
            )

    def record_reconnect(self) -> None:
        """Record a reconnect attempt."""
        self.reconnect_attempts += 1
        self.status = FeedStatus.RECONNECTING
        logger.bind(component="external_data").warning(
            "External feed reconnect attempt source={} attempts={}",
            self.source,
            self.reconnect_attempts,
        )

    def snapshot(
        self,
        symbols: tuple[str, ...] = (),
        timeframes: tuple[str, ...] = (),
    ) -> FeedSnapshot:
        """Return current feed diagnostics."""
        quality = self.analyzer.analyze(self.payloads[-200:])
        latency = self.analyzer.latency_metrics(self.payloads[-200:])
        status = self.status
        message = "ok"
        if quality.quality_score < self.quality_threshold:
            status = FeedStatus.DEGRADED
            message = "quality degradation"
        if latency.threshold_breached:
            status = FeedStatus.DEGRADED
            message = "latency threshold breached"
        return FeedSnapshot(
            source=self.source,
            status=status,
            running=status in {FeedStatus.RUNNING, FeedStatus.DEGRADED, FeedStatus.RECONNECTING},
            symbols=symbols,
            timeframes=timeframes,
            last_event_at=self.payloads[-1].timestamp if self.payloads else None,
            uptime_seconds=self.uptime_seconds(),
            reconnect_attempts=self.reconnect_attempts,
            latency=latency if self.payloads else FeedLatencyMetrics(),
            quality=quality if self.payloads else FeedQualityMetrics(sample_count=0),
            message=message,
        )

    def uptime_seconds(self) -> float:
        """Return monitor uptime in seconds."""
        if not self.started_at:
            return 0.0
        end = self.stopped_at or utc_now()
        return max(0.0, (end - self.started_at).total_seconds())
