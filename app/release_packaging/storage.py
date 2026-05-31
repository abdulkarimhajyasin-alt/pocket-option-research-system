"""Storage writer for release packaging outputs."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any


class ReleasePackagingStorage:
    """Persist release package outputs."""

    def __init__(self, output_dir: Path | str = "storage/release_packaging") -> None:
        self.output_dir = Path(output_dir)

    def save(
        self,
        manifest: dict[str, Any],
        status: dict[str, Any],
        audit: dict[str, Any],
        diagnostics: list[dict[str, Any]],
        recommendations: list[str],
    ) -> dict[str, str]:
        self.output_dir.mkdir(parents=True, exist_ok=True)
        release_state = {
            "release_id": manifest.get("release_id"),
            "release_status": manifest.get("release_status"),
            "recommended_next_decision": status.get("recommended_next_decision"),
            "research_only": True,
            "local_only": True,
        }
        paths = {
            "manifest": self.output_dir / "release_manifest.json",
            "status": self.output_dir / "project_status.json",
            "audit": self.output_dir / "repository_audit.json",
            "diagnostics": self.output_dir / "diagnostics.json",
            "recommendations": self.output_dir / "recommendations.json",
            "state": self.output_dir / "release_state.json",
        }
        self._write(paths["manifest"], manifest)
        self._write(paths["status"], status)
        self._write(paths["audit"], audit)
        self._write(paths["diagnostics"], diagnostics)
        self._write(paths["recommendations"], recommendations)
        self._write(paths["state"], release_state)
        return {key: str(path) for key, path in paths.items()}

    def _write(self, path: Path, payload: Any) -> None:
        path.write_text(json.dumps(payload, indent=2, ensure_ascii=False), encoding="utf-8")
