"""Storage for pattern memory outputs."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from app.pattern_memory.models import PatternMemoryResult


class PatternMemoryStorage:
    """Persist pattern memory outputs and safely load missing files."""

    def __init__(self, output_dir: Path | str = "storage/pattern_memory") -> None:
        self.output_dir = Path(output_dir)

    def save(self, result: PatternMemoryResult, analytics: dict[str, Any]) -> dict[str, str]:
        self.output_dir.mkdir(parents=True, exist_ok=True)
        paths = {
            "memory": self.output_dir / "pattern_memory.json",
            "successful": self.output_dir / "successful_patterns.json",
            "failed": self.output_dir / "failed_patterns.json",
            "rankings": self.output_dir / "pattern_rankings.json",
            "similarity": self.output_dir / "similarity_history.json",
            "learning": self.output_dir / "learning_metrics.json",
        }
        records = [item.to_dict() for item in result.records]
        self._write(paths["memory"], result.to_dict())
        self._write(
            paths["successful"],
            [row for row in records if row["outcome_bucket"] == "successful"],
        )
        self._write(paths["failed"], [row for row in records if row["outcome_bucket"] == "failed"])
        self._write(paths["rankings"], [item.to_dict() for item in result.rankings])
        self._write(paths["similarity"], [item.to_dict() for item in result.similarities])
        self._write(paths["learning"], analytics)
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
