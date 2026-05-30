"""Session intelligence for research-only signals."""

from __future__ import annotations

from app.data.models import Candle
from app.signal_intelligence.models import SessionState


class SessionEngine:
    """Classify market session and quality deterministically."""

    def detect(self, candle: Candle) -> SessionState:
        hour = candle.timestamp.hour
        if 0 <= hour < 7:
            name = "الجلسة الآسيوية"
            quality = 62.0
            activity = 55.0
        elif 7 <= hour < 12:
            name = "جلسة لندن"
            quality = 86.0
            activity = 82.0
        elif 12 <= hour < 16:
            name = "جلسة التداخل"
            quality = 92.0
            activity = 88.0
        else:
            name = "جلسة نيويورك"
            quality = 78.0
            activity = 74.0
        return SessionState(
            timestamp=candle.timestamp,
            asset=candle.symbol,
            timeframe=candle.timeframe,
            session_name=name,
            quality_score=quality,
            activity_score=activity,
        )
