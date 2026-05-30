"""Storage for confluence research outputs."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from app.confluence.models import ResearchDecision


class ConfluenceStorage:
    """Persist confluence decisions and metrics safely."""

    def __init__(self, output_dir: Path | str = "storage/confluence") -> None:
        self.output_dir = Path(output_dir)

    def save(
        self,
        decisions: list[ResearchDecision],
        analytics: dict[str, Any],
    ) -> dict[str, str]:
        self.output_dir.mkdir(parents=True, exist_ok=True)
        paths = {
            "results": self.output_dir / "confluence_results.json",
            "factors": self.output_dir / "factor_scores.json",
            "metrics": self.output_dir / "confluence_metrics.json",
            "decisions": self.output_dir / "decision_history.json",
        }
        result_rows = [item.to_dict() for item in decisions]
        factor_rows = [
            {
                "opportunity_id": item.opportunity_id,
                "asset": item.asset,
                "factors": item.confluence.to_dict().get("factors", []),
            }
            for item in decisions
        ]
        self._write(paths["results"], result_rows)
        self._write(paths["factors"], factor_rows)
        self._write(paths["metrics"], analytics.get("summary", {}))
        self._write(paths["decisions"], result_rows)
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
