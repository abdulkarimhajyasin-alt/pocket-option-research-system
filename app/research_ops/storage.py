"""Storage for research operations outputs."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from app.research_ops.models import ResearchOperationsResult


class ResearchOperationsStorage:
    """Persist control center payloads safely."""

    def __init__(self, output_dir: Path | str = "storage/research_ops") -> None:
        self.output_dir = Path(output_dir)

    def save(
        self,
        result: ResearchOperationsResult,
        analytics: dict[str, Any],
    ) -> dict[str, str]:
        self.output_dir.mkdir(parents=True, exist_ok=True)
        paths = {
            "summary": self.output_dir / "executive_summary.json",
            "health": self.output_dir / "research_health.json",
            "alerts": self.output_dir / "alerts.json",
            "recommendations": self.output_dir / "recommendations.json",
            "risk": self.output_dir / "risk_assessment.json",
            "actions": self.output_dir / "next_actions.json",
        }
        self._write(paths["summary"], result.executive_summary.to_dict())
        self._write(paths["health"], result.executive_summary.research_health.to_dict())
        self._write(paths["alerts"], [item.to_dict() for item in result.alerts])
        self._write(
            paths["recommendations"],
            [item.to_dict() for item in result.recommendations],
        )
        self._write(paths["risk"], result.risk_assessment.to_dict())
        self._write(paths["actions"], result.executive_summary.next_action.to_dict())
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
