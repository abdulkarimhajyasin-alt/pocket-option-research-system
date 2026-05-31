"""Parser for read-only browser observation artifacts."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from app.browser_observation.models import ObservationArtifact
from app.browser_observation.models import ParseResult
from app.browser_observation.validator import average


class ArtifactParserEngine:
    """Extract observable information without browser interaction."""

    def parse(self, artifacts: tuple[ObservationArtifact, ...]) -> ParseResult:
        text = " ".join(self._artifact_text(item) for item in artifacts)
        lower = text.lower()
        visible_assets = self._count_any(lower, ["asset", "assets", "eurusd", "symbol"])
        visible_payouts = self._count_any(lower, ["payout", "return", "yield"])
        visible_sessions = self._count_any(lower, ["session", "london", "new_york"])
        visible_symbols = self._count_any(lower, ["symbol", "eurusd", "pair"])
        visible_timestamps = self._count_any(lower, ["timestamp", "time", "created_at"])
        visible_market_data = self._count_any(
            lower,
            ["open", "high", "low", "close", "candle", "market"],
        )
        score = average(
            [
                min(100.0, visible_assets * 25.0),
                min(100.0, visible_payouts * 25.0),
                min(100.0, visible_sessions * 25.0),
                min(100.0, visible_symbols * 25.0),
                min(100.0, visible_timestamps * 20.0),
                min(100.0, visible_market_data * 15.0),
            ]
        )
        return ParseResult(
            score=score,
            visible_assets=visible_assets,
            visible_payouts=visible_payouts,
            visible_sessions=visible_sessions,
            visible_symbols=visible_symbols,
            visible_timestamps=visible_timestamps,
            visible_market_data=visible_market_data,
        )

    def _artifact_text(self, artifact: ObservationArtifact) -> str:
        path = Path(artifact.artifact_source)
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
