"""Duplicate artifact detection for repository hygiene."""

from __future__ import annotations

from typing import Any

from app.repository_hygiene.models import DuplicateArtifactFinding
from app.repository_hygiene.schemas import HYGIENE_ONLY_FLAGS


class DuplicateArtifactDetectionEngine:
    """Detect duplicate generated artifact names without cleanup."""

    def detect(self, inventory: dict[str, Any]) -> dict[str, Any]:
        by_name: dict[str, list[str]] = {}
        for item in inventory.get("items", []):
            name = str(item.get("file_name", ""))
            by_name.setdefault(name, []).append(str(item.get("path", "")))
        findings = [
            DuplicateArtifactFinding(
                file_name=name,
                paths=paths,
                count=len(paths),
                action="review manually",
            ).to_dict()
            for name, paths in sorted(by_name.items())
            if len(paths) > 1
        ]
        return {"items": findings, **HYGIENE_ONLY_FLAGS}
