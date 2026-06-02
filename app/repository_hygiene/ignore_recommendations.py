"""Ignore recommendation generation for repository hygiene."""

from __future__ import annotations

from pathlib import Path
from typing import Any

from app.repository_hygiene.models import IgnoreRecommendation
from app.repository_hygiene.schemas import HYGIENE_ONLY_FLAGS


class IgnoreRecommendationEngine:
    """Generate recommendation-only ignore patterns."""

    CANDIDATES = (
        (".pytest_cache/", "Local pytest cache should stay out of source control.", "مرتفع"),
        ("**/__pycache__/", "Python cache folders are local runtime artifacts.", "مرتفع"),
        (".codex_tmp/", "Local assistant scratch output is not release evidence.", "متوسط"),
        (
            "storage/research_archive/snapshots/research-v*/",
            "Archive snapshots need explicit retention review before tracking.",
            "منخفض",
        ),
    )

    def __init__(self, project_root: Path | str = ".") -> None:
        self.project_root = Path(project_root)

    def build(self) -> dict[str, Any]:
        existing = self._existing_patterns()
        items = [
            IgnoreRecommendation(pattern=pattern, reason=reason, confidence=confidence).to_dict()
            for pattern, reason, confidence in self.CANDIDATES
            if pattern not in existing
        ]
        return {"items": items, "existing_patterns": sorted(existing), **HYGIENE_ONLY_FLAGS}

    def _existing_patterns(self) -> set[str]:
        path = self.project_root / ".gitignore"
        if not path.exists():
            return set()
        return {
            line.strip()
            for line in path.read_text(encoding="utf-8").splitlines()
            if line.strip() and not line.strip().startswith("#")
        }
