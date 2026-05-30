"""Observation provider contracts and deterministic mock data."""

from __future__ import annotations

from abc import ABC, abstractmethod
from datetime import UTC, datetime, timedelta

from app.observation.models import (
    AssetObservation,
    BrokerSnapshot,
    CandleObservation,
    MarketObservation,
    PayoutObservation,
    SessionObservation,
)


class ObservationProvider(ABC):
    """Read-only market observation provider contract."""

    @abstractmethod
    def get_assets(self) -> list[AssetObservation]:
        """Return observed asset availability."""

    @abstractmethod
    def get_market_snapshot(self) -> BrokerSnapshot:
        """Return a complete observation snapshot."""

    @abstractmethod
    def get_candles(self) -> list[CandleObservation]:
        """Return observed candle data."""

    @abstractmethod
    def get_payouts(self) -> list[PayoutObservation]:
        """Return observed payout levels."""

    @abstractmethod
    def get_sessions(self) -> list[SessionObservation]:
        """Return observed session activity."""


class MockObservationProvider(ObservationProvider):
    """Generate deterministic research-only observation data."""

    def __init__(
        self,
        timestamp: datetime | None = None,
        source: str = "mock_observation_provider",
    ) -> None:
        self.timestamp = timestamp or datetime(2026, 1, 1, 12, 0, tzinfo=UTC)
        self.source = source
        self.assets = ("EURUSD", "GBPUSD", "USDJPY", "AUDUSD", "EURJPY")

    def get_assets(self) -> list[AssetObservation]:
        """Return deterministic asset activity observations."""
        return [
            AssetObservation(
                timestamp=self.timestamp,
                asset=asset,
                timeframe="1m",
                source=self.source,
                metadata={"provider_mode": "mock", "research_only": True},
                is_active=index != 4,
                activity_score=round(86 - index * 9.5, 2),
                display_name=asset,
            )
            for index, asset in enumerate(self.assets)
        ]

    def get_market_snapshot(self) -> BrokerSnapshot:
        """Return a full deterministic snapshot."""
        return BrokerSnapshot(
            timestamp=self.timestamp,
            asset="ALL",
            timeframe="snapshot",
            source=self.source,
            metadata={
                "provider_mode": "mock",
                "research_only": True,
                "no_broker_interaction": True,
            },
            assets=tuple(self.get_assets()),
            markets=tuple(self._markets()),
            payouts=tuple(self.get_payouts()),
            sessions=tuple(self.get_sessions()),
            candles=tuple(self.get_candles()),
        )

    def get_candles(self) -> list[CandleObservation]:
        """Return deterministic candle observations for dashboard research."""
        candles: list[CandleObservation] = []
        for asset_index, asset in enumerate(self.assets[:4]):
            base_price = 1.08 + asset_index * 0.015
            for step in range(6):
                timestamp = self.timestamp - timedelta(minutes=5 - step)
                movement = ((asset_index + step) % 5 - 2) * 0.00012
                open_price = round(base_price + step * 0.00018, 5)
                close_price = round(open_price + movement, 5)
                high = round(max(open_price, close_price) + 0.0002, 5)
                low = round(min(open_price, close_price) - 0.0002, 5)
                candles.append(
                    CandleObservation(
                        timestamp=timestamp,
                        asset=asset,
                        timeframe="1m",
                        source=self.source,
                        metadata={"provider_mode": "mock"},
                        open=open_price,
                        high=high,
                        low=low,
                        close=close_price,
                        volume=1000 + asset_index * 150 + step * 25,
                    )
                )
        return candles

    def get_payouts(self) -> list[PayoutObservation]:
        """Return deterministic payout observations."""
        payout_values = (82.0, 78.0, 74.0, 71.0, 66.0)
        return [
            PayoutObservation(
                timestamp=self.timestamp,
                asset=asset,
                timeframe="1m",
                source=self.source,
                metadata={"provider_mode": "mock", "rank": index + 1},
                payout_percent=payout_values[index],
            )
            for index, asset in enumerate(self.assets)
        ]

    def get_sessions(self) -> list[SessionObservation]:
        """Return deterministic session activity observations."""
        sessions = (
            ("الجلسة الآسيوية", 56.0, False),
            ("جلسة لندن", 83.0, True),
            ("جلسة نيويورك", 68.0, True),
            ("جلسة التداخل", 74.0, True),
        )
        return [
            SessionObservation(
                timestamp=self.timestamp,
                asset="ALL",
                timeframe="session",
                source=self.source,
                metadata={"provider_mode": "mock"},
                session_name=name,
                activity_score=score,
                is_active=active,
            )
            for name, score, active in sessions
        ]

    def _markets(self) -> list[MarketObservation]:
        return [
            MarketObservation(
                timestamp=self.timestamp,
                asset=asset.asset,
                timeframe=asset.timeframe,
                source=self.source,
                metadata={"provider_mode": "mock"},
                status="active" if asset.is_active else "watch_only",
                spread_proxy=round(0.8 + index * 0.12, 2),
                volatility_score=round(45 + asset.activity_score * 0.45, 2),
            )
            for index, asset in enumerate(self.get_assets())
        ]
