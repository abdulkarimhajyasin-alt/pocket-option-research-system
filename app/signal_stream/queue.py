"""Signal queue engine."""

from __future__ import annotations

from app.signal_stream.models import SignalDirection
from app.signal_stream.models import SignalEvent
from app.signal_stream.models import SignalQueueResult
from app.signal_stream.scoring import average
from app.signal_stream.scoring import clamp


class SignalQueueEngine:
    """Manage pending, active, expired, and rejected signal states."""

    def manage(self, events: tuple[SignalEvent, ...]) -> SignalQueueResult:
        rejected = tuple(item for item in events if item.direction == SignalDirection.NO_TRADE)
        tradable = tuple(item for item in events if item.direction != SignalDirection.NO_TRADE)
        active = tradable[: max(1, min(5, len(tradable)))] if tradable else ()
        pending = tradable[len(active) :]
        expired = tuple(item for item in events if item.quality < 50)
        rejection_penalty = len(rejected) / max(len(events), 1) * 30.0
        score = clamp(average([100.0 if events else 0.0, 100.0 - rejection_penalty]))
        return SignalQueueResult(
            score=score,
            pending=tuple(pending),
            active=tuple(active),
            expired=tuple(expired),
            rejected=rejected,
        )
