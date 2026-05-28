"""Equity curve tracking and drawdown calculations."""

from datetime import datetime

from loguru import logger

from app.analytics.models import EquityCurvePoint


class EquityCurveTracker:
    """Tracks balance progression, cumulative PnL, peaks, troughs, and drawdown."""

    def __init__(self, initial_equity: float = 0.0) -> None:
        self.initial_equity = initial_equity
        self._points: list[EquityCurvePoint] = []
        self._peak = initial_equity
        self._trough = initial_equity

    def update(self, timestamp: datetime, equity: float, pnl: float = 0.0) -> EquityCurvePoint:
        """Append one equity point and return it."""
        self._peak = max(self._peak, equity)
        self._trough = min(self._trough, equity)
        drawdown = self._peak - equity
        point = EquityCurvePoint(
            timestamp=timestamp,
            equity=equity,
            cumulative_pnl=equity - self.initial_equity,
            drawdown=drawdown,
            peak=self._peak,
            trough=self._trough,
        )
        self._points.append(point)
        logger.bind(component="analytics").info(
            "Equity updated equity={} drawdown={} pnl={}",
            round(equity, 4),
            round(drawdown, 4),
            round(pnl, 4),
        )
        return point

    def points(self) -> list[EquityCurvePoint]:
        """Return equity points in time order."""
        return list(self._points)

    @property
    def max_drawdown(self) -> float:
        """Return maximum absolute drawdown."""
        return max((point.drawdown for point in self._points), default=0.0)
