"""Market data provider interfaces and static research implementation."""

from __future__ import annotations

from abc import ABC, abstractmethod
from datetime import UTC, datetime, timedelta

from app.market_data.models import (
    MarketAsset,
    MarketCandle,
    MarketDataHealth,
    MarketLatency,
    MarketProviderInfo,
    MarketSession,
    MarketSnapshot,
    MarketStatus,
)


class BaseMarketDataProvider(ABC):
    """Provider contract for research-only market data sources."""

    @abstractmethod
    def provider_info(self) -> MarketProviderInfo:
        """Return provider metadata."""

    @abstractmethod
    def assets(self) -> list[MarketAsset]:
        """Return available market assets."""

    @abstractmethod
    def candles(self, asset: str | None = None, timeframe: str = "1m") -> list[MarketCandle]:
        """Return normalized candles."""

    @abstractmethod
    def timestamps(self) -> list[datetime]:
        """Return available update timestamps."""

    @abstractmethod
    def sessions(self) -> list[MarketSession]:
        """Return market sessions."""

    @abstractmethod
    def market_status(self) -> list[MarketStatus]:
        """Return market status observations."""

    @abstractmethod
    def provider_health(self) -> MarketDataHealth:
        """Return provider health."""

    @abstractmethod
    def provider_latency(self) -> list[MarketLatency]:
        """Return provider latency metrics."""

    @abstractmethod
    def snapshot(self) -> MarketSnapshot:
        """Return one complete market-data snapshot."""


class StaticResearchProvider(BaseMarketDataProvider):
    """Deterministic static provider for reproducible market-data research."""

    def __init__(
        self,
        timestamp: datetime | None = None,
        name: str = "static_research_provider",
    ) -> None:
        self.timestamp = timestamp or datetime(2026, 1, 1, 12, 0, tzinfo=UTC)
        self.name = name
        self._assets = ("EURUSD", "GBPUSD", "USDJPY", "AUDUSD", "EURJPY", "USDCAD")

    def provider_info(self) -> MarketProviderInfo:
        return MarketProviderInfo(
            name=self.name,
            provider_type="static_research",
            supports_realtime=False,
            supports_historical=True,
            research_only=True,
            metadata={"external_ready": True, "no_broker_control": True},
        )

    def assets(self) -> list[MarketAsset]:
        return [
            MarketAsset(
                timestamp=self.timestamp,
                provider=self.name,
                asset=asset,
                timeframe="1m",
                metadata={"source_mode": "static_research"},
                display_name=asset,
                asset_class="forex",
                is_active=index < 5,
                quality_score=round(94 - index * 5.5, 2),
            )
            for index, asset in enumerate(self._assets)
        ]

    def candles(self, asset: str | None = None, timeframe: str = "1m") -> list[MarketCandle]:
        selected_assets = [asset] if asset else list(self._assets[:5])
        candles = []
        for asset_index, symbol in enumerate(selected_assets):
            for step in range(12):
                timestamp = self.timestamp - timedelta(minutes=11 - step)
                open_price = round(1.08 + asset_index * 0.013 + step * 0.00009, 5)
                close_price = round(open_price + ((step % 4) - 1.5) * 0.00008, 5)
                candles.append(
                    MarketCandle(
                        timestamp=timestamp,
                        provider=self.name,
                        asset=symbol,
                        timeframe=timeframe,
                        metadata={"source_mode": "static_research", "sequence": step},
                        open=open_price,
                        high=round(max(open_price, close_price) + 0.00018, 5),
                        low=round(min(open_price, close_price) - 0.00018, 5),
                        close=close_price,
                        volume=900 + asset_index * 120 + step * 12,
                    )
                )
        return candles

    def timestamps(self) -> list[datetime]:
        return [self.timestamp - timedelta(minutes=offset) for offset in range(12)]

    def sessions(self) -> list[MarketSession]:
        payload = (
            ("الجلسة الآسيوية", 58.0, False),
            ("جلسة لندن", 86.0, True),
            ("جلسة نيويورك", 72.0, True),
            ("جلسة التداخل", 79.0, True),
        )
        return [
            MarketSession(
                timestamp=self.timestamp,
                provider=self.name,
                asset="ALL",
                timeframe="session",
                metadata={"source_mode": "static_research"},
                name=name,
                activity_score=score,
                is_active=active,
            )
            for name, score, active in payload
        ]

    def market_status(self) -> list[MarketStatus]:
        return [
            MarketStatus(
                timestamp=self.timestamp,
                provider=self.name,
                asset=asset.asset,
                timeframe=asset.timeframe,
                metadata={"source_mode": "static_research"},
                status="مفتوح" if asset.is_active else "مراقبة فقط",
                coverage_score=round(asset.quality_score - 2.0, 2),
                update_frequency=round(1.8 - index * 0.12, 4),
            )
            for index, asset in enumerate(self.assets())
        ]

    def provider_health(self) -> MarketDataHealth:
        return MarketDataHealth(
            timestamp=self.timestamp,
            provider=self.name,
            asset="ALL",
            timeframe="provider",
            metadata={"source_mode": "static_research", "research_only": True},
            score=91.0,
            label="ممتاز",
            readiness_score=88.5,
            readiness_label="جاهز للبحث",
        )

    def provider_latency(self) -> list[MarketLatency]:
        return [
            MarketLatency(
                timestamp=self.timestamp - timedelta(seconds=index * 4),
                provider=self.name,
                asset=asset,
                timeframe="provider",
                metadata={"source_mode": "static_research"},
                latency_ms=round(32 + index * 3.75, 2),
            )
            for index, asset in enumerate(self._assets[:5])
        ]

    def snapshot(self) -> MarketSnapshot:
        return MarketSnapshot(
            timestamp=self.timestamp,
            provider=self.name,
            asset="ALL",
            timeframe="snapshot",
            metadata={
                "research_only": True,
                "no_trading": True,
                "no_execution": True,
                "no_broker_automation": True,
            },
            provider_info=self.provider_info(),
            assets=tuple(self.assets()),
            candles=tuple(self.candles()),
            sessions=tuple(self.sessions()),
            statuses=tuple(self.market_status()),
            latencies=tuple(self.provider_latency()),
            health=self.provider_health(),
        )
