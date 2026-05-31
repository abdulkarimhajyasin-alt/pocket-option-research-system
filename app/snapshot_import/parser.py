"""Parser for manually imported snapshots."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from app.snapshot_import.models import ParseResult
from app.snapshot_import.models import SnapshotImport
from app.snapshot_import.validator import average


class SnapshotParserEngine:
    """Extract visible information from read-only imported files."""

    def parse(self, imports: tuple[SnapshotImport, ...]) -> ParseResult:
        text = " ".join(self._import_text(item) for item in imports)
        lower = text.lower()
        assets = self._count_any(lower, ["asset", "assets", "instrument"])
        payouts = self._count_any(lower, ["payout", "return", "yield"])
        sessions = self._count_any(lower, ["session", "london", "new_york", "research"])
        timestamps = self._count_any(lower, ["timestamp", "time", "created_at"])
        market_information = self._count_any(
            lower,
            ["market", "open", "high", "low", "close", "candle"],
        )
        symbols = self._count_any(lower, ["symbol", "eurusd", "pair"])
        score = average(
            [
                min(100.0, assets * 30.0),
                min(100.0, payouts * 30.0),
                min(100.0, sessions * 30.0),
                min(100.0, timestamps * 25.0),
                min(100.0, market_information * 20.0),
                min(100.0, symbols * 30.0),
            ]
        )
        return ParseResult(
            score=score,
            assets=assets,
            payouts=payouts,
            sessions=sessions,
            timestamps=timestamps,
            market_information=market_information,
            symbols=symbols,
        )

    def _import_text(self, item: SnapshotImport) -> str:
        path = Path(item.source_path)
        if not path.exists():
            return ""
        try:
            text = path.read_text(encoding="utf-8")
            if path.suffix.lower() == ".json":
                payload: Any = json.loads(text)
                return json.dumps(payload, ensure_ascii=False)
            return text
        except (OSError, UnicodeDecodeError, json.JSONDecodeError):
            return ""

    def _count_any(self, text: str, needles: list[str]) -> int:
        return sum(1 for needle in needles if needle in text)
