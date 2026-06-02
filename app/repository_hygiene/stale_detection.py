"""Stale artifact detection for repository hygiene."""

from __future__ import annotations

from typing import Any

from app.repository_hygiene.models import StaleArtifactFinding
from app.repository_hygiene.schemas import HYGIENE_ONLY_FLAGS


class StaleArtifactDetectionEngine:
    """Detect stale versioned archive artifacts without cleanup."""

    def detect(self, inventory: dict[str, Any], retain_latest: int = 5) -> dict[str, Any]:
        versions = [
            int(item["version_number"])
            for item in inventory.get("items", [])
            if item.get("version_number") is not None
        ]
        latest = max(versions) if versions else 0
        threshold = max(0, latest - retain_latest + 1)
        findings = []
        seen_paths: set[str] = set()
        for item in inventory.get("items", []):
            version = item.get("version_number")
            path = str(item.get("path", ""))
            if version is None or path in seen_paths or int(version) >= threshold:
                continue
            seen_paths.add(path)
            findings.append(
                StaleArtifactFinding(
                    path=path,
                    reason="Versioned archive artifact is older than local retention window.",
                    version_number=int(version),
                    action="review manually",
                ).to_dict()
            )
        return {"items": findings, "latest_version": latest, **HYGIENE_ONLY_FLAGS}
