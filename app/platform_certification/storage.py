"""Storage writer for platform certification outputs."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from app.platform_certification.models import PlatformCertificationResult


class PlatformCertificationStorage:
    """Persist certification outputs under storage/platform_certification."""

    def __init__(self, output_dir: Path | str = "storage/platform_certification") -> None:
        self.output_dir = Path(output_dir)

    def save(self, result: PlatformCertificationResult) -> dict[str, str]:
        self.output_dir.mkdir(parents=True, exist_ok=True)
        payload = result.to_dict()
        paths = {
            "results": self.output_dir / "certification_results.json",
            "domains": self.output_dir / "domain_scores.json",
            "diagnostics": self.output_dir / "diagnostics.json",
            "recommendations": self.output_dir / "recommendations.json",
        }
        self._write(paths["results"], payload)
        self._write(paths["domains"], payload["domain_scores"])
        self._write(paths["diagnostics"], payload["diagnostics"])
        self._write(paths["recommendations"], payload["recommendations"])
        return {key: str(path) for key, path in paths.items()}

    def _write(self, path: Path, payload: Any) -> None:
        path.write_text(json.dumps(payload, indent=2, ensure_ascii=False), encoding="utf-8")
