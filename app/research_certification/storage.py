"""Storage for research certification outputs."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from app.research_certification.models import ResearchCertificationResult


class ResearchCertificationStorage:
    """Persist certification outputs safely."""

    def __init__(
        self,
        output_dir: Path | str = "storage/research_certification",
    ) -> None:
        self.output_dir = Path(output_dir)

    def save(
        self,
        result: ResearchCertificationResult,
        analytics: dict[str, Any],
    ) -> dict[str, str]:
        self.output_dir.mkdir(parents=True, exist_ok=True)
        paths = {
            "certification": self.output_dir / "certification_results.json",
            "requirements": self.output_dir / "requirements_results.json",
            "diagnostics": self.output_dir / "diagnostics.json",
            "recommendations": self.output_dir / "recommendations.json",
            "maturity": self.output_dir / "maturity_metrics.json",
        }
        self._write(paths["certification"], result.to_dict())
        self._write(paths["requirements"], result.requirements.to_dict())
        self._write(paths["diagnostics"], [item.to_dict() for item in result.diagnostics])
        self._write(
            paths["recommendations"],
            [item.to_dict() for item in result.recommendations],
        )
        self._write(paths["maturity"], analytics)
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
