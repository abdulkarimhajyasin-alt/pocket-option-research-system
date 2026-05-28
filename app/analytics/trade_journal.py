"""Structured append-only trade journal."""

import csv
import json
from pathlib import Path
from typing import Iterable

from loguru import logger

from app.analytics.models import TradeJournalEntry


class TradeJournal:
    """Stores searchable trade lifecycle records for research workflows."""

    def __init__(self) -> None:
        self._entries: list[TradeJournalEntry] = []

    def append(self, entry: TradeJournalEntry) -> None:
        """Append one immutable journal entry."""
        self._entries.append(entry)
        logger.bind(component="analytics").info(
            "Trade journal entry written trade_id={} state={}",
            entry.trade_id,
            entry.lifecycle_state,
        )

    def entries(self) -> list[TradeJournalEntry]:
        """Return journal entries in append order."""
        return list(self._entries)

    def search(
        self,
        *,
        strategy_name: str | None = None,
        symbol: str | None = None,
        lifecycle_state: str | None = None,
    ) -> list[TradeJournalEntry]:
        """Search journal entries by common research tags."""
        entries: Iterable[TradeJournalEntry] = self._entries
        if strategy_name is not None:
            entries = [entry for entry in entries if entry.strategy_name == strategy_name]
        if symbol is not None:
            entries = [entry for entry in entries if entry.symbol == symbol]
        if lifecycle_state is not None:
            entries = [entry for entry in entries if entry.lifecycle_state == lifecycle_state]
        return list(entries)

    def export_json(self, path: Path | str) -> Path:
        """Export journal entries to JSON."""
        output_path = Path(path)
        output_path.parent.mkdir(parents=True, exist_ok=True)
        payload = [entry.to_dict() for entry in self._entries]
        output_path.write_text(json.dumps(payload, indent=2), encoding="utf-8")
        logger.bind(component="analytics").info("Trade journal JSON exported: {}", output_path)
        return output_path

    def export_csv(self, path: Path | str) -> Path:
        """Export journal entries to CSV."""
        output_path = Path(path)
        output_path.parent.mkdir(parents=True, exist_ok=True)
        fieldnames = list(TradeJournalEntry.__dataclass_fields__.keys())
        with output_path.open("w", encoding="utf-8", newline="") as file:
            writer = csv.DictWriter(file, fieldnames=fieldnames)
            writer.writeheader()
            for entry in self._entries:
                writer.writerow(entry.to_dict())
        logger.bind(component="analytics").info("Trade journal CSV exported: {}", output_path)
        return output_path
