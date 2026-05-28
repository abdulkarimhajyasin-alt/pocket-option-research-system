"""Research dataset generation for future ML and optimization workflows."""

import csv
from pathlib import Path
from typing import Any

from loguru import logger

from app.analytics.models import TradeJournalEntry


class ResearchDatasetBuilder:
    """Builds normalized CSV datasets without implementing ML models."""

    def build_trade_dataset(
        self,
        entries: list[TradeJournalEntry],
        path: Path | str,
    ) -> Path:
        """Export normalized lifecycle entries for downstream research."""
        output_path = Path(path)
        output_path.parent.mkdir(parents=True, exist_ok=True)
        rows = [self._normalize_entry(entry) for entry in entries]
        fieldnames = [
            "trade_id",
            "timestamp",
            "strategy_name",
            "symbol",
            "timeframe",
            "direction",
            "confidence",
            "lifecycle_state",
            "outcome",
            "pnl",
            "rejection_reason",
            "risk_rule",
            "hour_utc",
            "is_win",
            "is_loss",
            "is_blocked",
        ]
        with output_path.open("w", encoding="utf-8", newline="") as file:
            writer = csv.DictWriter(file, fieldnames=fieldnames)
            writer.writeheader()
            for row in rows:
                writer.writerow(row)
        logger.bind(component="analytics").info("Research dataset generated: {}", output_path)
        return output_path

    def _normalize_entry(self, entry: TradeJournalEntry) -> dict[str, Any]:
        return {
            "trade_id": entry.trade_id,
            "timestamp": entry.timestamp.isoformat(),
            "strategy_name": entry.strategy_name,
            "symbol": entry.symbol,
            "timeframe": entry.timeframe,
            "direction": entry.direction,
            "confidence": round(entry.confidence, 6),
            "lifecycle_state": entry.lifecycle_state,
            "outcome": entry.outcome,
            "pnl": round(entry.pnl, 6),
            "rejection_reason": entry.rejection_reason,
            "risk_rule": entry.risk_rule,
            "hour_utc": entry.timestamp.hour,
            "is_win": int(entry.outcome == "win"),
            "is_loss": int(entry.outcome == "loss"),
            "is_blocked": int(entry.lifecycle_state == "blocked"),
        }
