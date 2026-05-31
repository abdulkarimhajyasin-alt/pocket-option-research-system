"""Storage for passive broker observation readiness."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from app.broker_readiness.models import BrokerReadinessResult


class BrokerReadinessStorage:
    """Persist broker readiness outputs safely."""

    def __init__(self, output_dir: Path | str = "storage/broker_readiness") -> None:
        self.output_dir = Path(output_dir)

    def save(
        self,
        result: BrokerReadinessResult,
        analytics: dict[str, Any],
    ) -> dict[str, str]:
        self.output_dir.mkdir(parents=True, exist_ok=True)
        paths = {
            "readiness": self.output_dir / "readiness_results.json",
            "capability": self.output_dir / "capability_results.json",
            "validation": self.output_dir / "validation_results.json",
            "restriction": self.output_dir / "restriction_results.json",
            "diagnostics": self.output_dir / "diagnostics.json",
        }
        self._write(paths["readiness"], result.to_dict())
        self._write(paths["capability"], result.capability.to_dict())
        self._write(paths["validation"], result.validation.to_dict())
        self._write(paths["restriction"], result.restrictions.to_dict())
        self._write(paths["diagnostics"], analytics)
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
