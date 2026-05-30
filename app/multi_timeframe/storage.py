"""Storage for multi-timeframe confirmation artifacts."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from app.multi_timeframe.models import ConfirmationResult


class MultiTimeframeStorage:
    """Persist confirmation artifacts under storage/multi_timeframe."""

    def __init__(self, output_dir: Path | str = "storage/multi_timeframe") -> None:
        self.output_dir = Path(output_dir)

    def save(
        self,
        results: list[ConfirmationResult],
        analytics: dict[str, Any],
    ) -> dict[str, str]:
        self.output_dir.mkdir(parents=True, exist_ok=True)
        paths = {
            "alignment": self.output_dir / "alignment_results.json",
            "confirmation": self.output_dir / "confirmation_results.json",
            "conflicts": self.output_dir / "conflict_reports.json",
            "statistics": self.output_dir / "timeframe_statistics.json",
        }
        self._write(paths["alignment"], [item.alignment.to_dict() for item in results])
        self._write(paths["confirmation"], [item.to_dict() for item in results])
        self._write(paths["conflicts"], [item.conflict.to_dict() for item in results])
        self._write(paths["statistics"], analytics.get("summary", {}))
        return {key: str(path) for key, path in paths.items()}

    def load_json(self, name: str, default: Any) -> Any:
        path = self.output_dir / name
        if not path.exists():
            return default
        return json.loads(path.read_text(encoding="utf-8"))

    def _write(self, path: Path, payload: Any) -> None:
        path.write_text(
            json.dumps(payload, indent=2, ensure_ascii=False),
            encoding="utf-8",
        )
