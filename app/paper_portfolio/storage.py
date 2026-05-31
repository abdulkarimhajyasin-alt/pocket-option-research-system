"""Storage for paper portfolio governance outputs."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from app.paper_portfolio.models import PaperPortfolioRun


class PaperPortfolioStorage:
    """Persist paper portfolio outputs."""

    def __init__(self, output_dir: Path | str = "storage/paper_portfolio") -> None:
        self.output_dir = Path(output_dir)

    def save(self, result: PaperPortfolioRun) -> dict[str, str]:
        self.output_dir.mkdir(parents=True, exist_ok=True)
        paths = {
            "portfolio": self.output_dir / "portfolio_results.json",
            "exposure": self.output_dir / "exposure_results.json",
            "drawdown": self.output_dir / "drawdown_results.json",
            "governance": self.output_dir / "governance_results.json",
            "limits": self.output_dir / "limits_results.json",
            "diagnostics": self.output_dir / "diagnostics.json",
        }
        self._write(paths["portfolio"], result.portfolio.to_dict())
        self._write(paths["exposure"], result.exposure)
        self._write(paths["drawdown"], result.drawdown)
        self._write(paths["governance"], [item.to_dict() for item in result.governance])
        self._write(paths["limits"], [item.to_dict() for item in result.limits])
        self._write(paths["diagnostics"], result.to_dict())
        return {key: str(path) for key, path in paths.items()}

    def _write(self, path: Path, payload: Any) -> None:
        path.write_text(json.dumps(payload, indent=2, ensure_ascii=False), encoding="utf-8")
