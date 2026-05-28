"""Market session performance analytics."""

from datetime import UTC

from app.analytics.models import SessionPerformance, TradeJournalEntry
from app.signals.session_filter import SessionFilter


class SessionAnalytics:
    """Aggregates journal entries by London, New York, and Asian sessions."""

    def __init__(self, session_filter: SessionFilter | None = None) -> None:
        self.session_filter = session_filter or SessionFilter()

    def analyze(self, entries: list[TradeJournalEntry]) -> list[SessionPerformance]:
        """Return per-session performance metrics."""
        results: list[SessionPerformance] = []
        for session_name in ("asian", "london", "new_york"):
            session_entries = [
                entry
                for entry in entries
                if self.session_filter.get_session(session_name).contains(
                    entry.timestamp.astimezone(UTC)
                )
            ]
            results.append(self._build(session_name, session_entries))
        return results

    def _build(
        self,
        session_name: str,
        entries: list[TradeJournalEntry],
    ) -> SessionPerformance:
        settled = [entry for entry in entries if entry.lifecycle_state == "settled"]
        blocked = [entry for entry in entries if entry.lifecycle_state == "blocked"]
        decisions = settled + blocked
        wins = sum(1 for entry in settled if entry.outcome == "win")
        losses = sum(1 for entry in settled if entry.outcome == "loss")
        confidence_count = len(decisions)
        average_confidence = (
            sum(entry.confidence for entry in decisions) / confidence_count
            if confidence_count
            else 0.0
        )
        return SessionPerformance(
            session_name=session_name,
            trades=len(settled),
            wins=wins,
            losses=losses,
            pnl=round(sum(entry.pnl for entry in settled), 4),
            rejection_rate=round(len(blocked) / len(decisions), 4) if decisions else 0.0,
            average_confidence=round(average_confidence, 4),
        )
