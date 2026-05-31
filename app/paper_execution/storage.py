"""Storage for paper-only execution outputs."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from app.paper_execution.models import PaperExecutionRun


class PaperExecutionStorage:
    """Persist paper execution research outputs."""

    def __init__(self, output_dir: Path | str = "storage/paper_execution") -> None:
        self.output_dir = Path(output_dir)

    def save(self, result: PaperExecutionRun) -> dict[str, str]:
        self.output_dir.mkdir(parents=True, exist_ok=True)
        paths = {
            "paper_orders": self.output_dir / "paper_orders.json",
            "paper_lifecycle": self.output_dir / "paper_lifecycle.json",
            "paper_results": self.output_dir / "paper_results.json",
            "risk_results": self.output_dir / "risk_results.json",
            "analytics": self.output_dir / "analytics.json",
            "diagnostics": self.output_dir / "diagnostics.json",
        }
        self._write(paths["paper_orders"], [item.to_dict() for item in result.orders])
        self._write(paths["paper_lifecycle"], [item.to_dict() for item in result.lifecycle])
        self._write(paths["paper_results"], [item.to_dict() for item in result.results])
        self._write(paths["risk_results"], [item.to_dict() for item in result.risk_gates])
        self._write(paths["analytics"], result.analytics)
        self._write(paths["diagnostics"], result.to_dict())
        return {key: str(path) for key, path in paths.items()}

    def _write(self, path: Path, payload: Any) -> None:
        path.write_text(json.dumps(payload, indent=2, ensure_ascii=False), encoding="utf-8")
