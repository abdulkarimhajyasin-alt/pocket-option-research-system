"""Storage for opportunity qualification artifacts."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from app.opportunity_engine.models import OpportunityRanking, QualifiedOpportunity


class OpportunityStorage:
    """Persist opportunity qualification files under storage/opportunities."""

    def __init__(self, output_dir: Path | str = "storage/opportunities") -> None:
        self.output_dir = Path(output_dir)

    def save(
        self,
        opportunities: list[QualifiedOpportunity],
        rankings: list[OpportunityRanking],
        analytics: dict[str, Any],
    ) -> dict[str, str]:
        self.output_dir.mkdir(parents=True, exist_ok=True)
        paths = {
            "opportunities": self.output_dir / "qualified_opportunities.json",
            "rankings": self.output_dir / "opportunity_rankings.json",
            "metrics": self.output_dir / "qualification_metrics.json",
            "rejections": self.output_dir / "rejection_analysis.json",
        }
        self._write(paths["opportunities"], [item.to_dict() for item in opportunities])
        self._write(paths["rankings"], [item.to_dict() for item in rankings])
        self._write(paths["metrics"], analytics.get("summary", {}))
        self._write(paths["rejections"], analytics.get("rejection_distribution", {}))
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
