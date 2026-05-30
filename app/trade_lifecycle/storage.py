"""Storage for research lifecycle simulation outputs."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from app.trade_lifecycle.models import TradeLifecycleRecord


class TradeLifecycleStorage:
    """Persist lifecycle records and analysis files."""

    def __init__(self, output_dir: Path | str = "storage/trade_lifecycle") -> None:
        self.output_dir = Path(output_dir)

    def save(
        self,
        records: list[TradeLifecycleRecord],
        analytics: dict[str, Any],
    ) -> dict[str, str]:
        self.output_dir.mkdir(parents=True, exist_ok=True)
        paths = {
            "records": self.output_dir / "lifecycle_records.json",
            "metrics": self.output_dir / "lifecycle_metrics.json",
            "success": self.output_dir / "success_analysis.json",
            "failure": self.output_dir / "failure_analysis.json",
            "quality": self.output_dir / "quality_scores.json",
        }
        rows = [item.to_dict() for item in records]
        self._write(paths["records"], rows)
        self._write(paths["metrics"], analytics.get("summary", {}))
        self._write(paths["success"], analytics.get("success_factors", {}))
        self._write(paths["failure"], analytics.get("failure_factors", {}))
        self._write(
            paths["quality"],
            [{"lifecycle_id": item.lifecycle_id, **item.quality.to_dict()} for item in records],
        )
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
