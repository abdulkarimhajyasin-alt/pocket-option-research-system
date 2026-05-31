"""Storage for integration safety boundary."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from app.integration_safety.models import IntegrationSafetyRun


class IntegrationSafetyStorage:
    """Persist integration safety outputs."""

    def __init__(self, output_dir: Path | str = "storage/integration_safety") -> None:
        self.output_dir = Path(output_dir)

    def save(self, result: IntegrationSafetyRun) -> dict[str, str]:
        self.output_dir.mkdir(parents=True, exist_ok=True)
        paths = {
            "policy": self.output_dir / "safety_policy.json",
            "boundary": self.output_dir / "boundary_results.json",
            "permissions": self.output_dir / "permission_results.json",
            "restrictions": self.output_dir / "restriction_results.json",
            "compliance": self.output_dir / "compliance_results.json",
            "audit": self.output_dir / "audit_records.json",
            "diagnostics": self.output_dir / "diagnostics.json",
        }
        self._write(paths["policy"], result.policy.to_dict())
        self._write(paths["boundary"], result.boundary)
        self._write(paths["permissions"], result.permissions)
        self._write(paths["restrictions"], result.restrictions)
        self._write(paths["compliance"], result.compliance)
        self._write(paths["audit"], result.audit)
        self._write(paths["diagnostics"], result.to_dict())
        return {key: str(path) for key, path in paths.items()}

    def _write(self, path: Path, payload: Any) -> None:
        path.write_text(
            json.dumps(payload, indent=2, ensure_ascii=False),
            encoding="utf-8",
        )
