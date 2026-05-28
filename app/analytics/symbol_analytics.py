"""Per-symbol research analytics."""

from app.analytics.models import SymbolPerformance, TradeJournalEntry


class SymbolAnalytics:
    """Aggregates journal entries by symbol."""

    def analyze(self, entries: list[TradeJournalEntry]) -> list[SymbolPerformance]:
        """Return per-symbol performance metrics."""
        symbols = sorted({entry.symbol for entry in entries})
        return [self._build(symbol, entries) for symbol in symbols]

    def _build(self, symbol: str, entries: list[TradeJournalEntry]) -> SymbolPerformance:
        symbol_entries = [entry for entry in entries if entry.symbol == symbol]
        settled = [entry for entry in symbol_entries if entry.lifecycle_state == "settled"]
        blocked = [entry for entry in symbol_entries if entry.lifecycle_state == "blocked"]
        decisions = settled + blocked
        wins = sum(1 for entry in settled if entry.outcome == "win")
        losses = sum(1 for entry in settled if entry.outcome == "loss")
        average_confidence = (
            sum(entry.confidence for entry in decisions) / len(decisions) if decisions else 0.0
        )
        return SymbolPerformance(
            symbol=symbol,
            trades=len(settled),
            wins=wins,
            losses=losses,
            pnl=round(sum(entry.pnl for entry in settled), 4),
            rejection_count=len(blocked),
            average_confidence=round(average_confidence, 4),
            exposure_frequency=sum(
                1 for entry in symbol_entries if entry.lifecycle_state == "executed"
            ),
        )
