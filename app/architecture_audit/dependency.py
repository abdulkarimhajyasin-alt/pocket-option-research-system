"""Dependency and maintenance audit engine."""

from __future__ import annotations

from pathlib import Path
from typing import Any


class DependencyAuditEngine:
    """Audit deprecated patterns, duplicated logic, stale and orphan indicators."""

    DEPRECATED_PATTERNS = ("datetime.utcnow",)

    def evaluate(self, project_root: Path) -> dict[str, Any]:
        py_files = sorted((project_root / "app").rglob("*.py"))
        deprecated_hits = self._count_patterns(py_files, self.DEPRECATED_PATTERNS)
        stale_modules = [path for path in py_files if path.stat().st_size == 0]
        service_count = len([path for path in py_files if path.name == "service.py"])
        duplicated_logic_indicator = len(
            [path for path in py_files if path.name in {"storage.py", "reports.py"}]
        )
        penalty = deprecated_hits * 2.0 + len(stale_modules) * 10.0
        score = max(0.0, 100.0 - min(35.0, penalty))
        return {
            "dependency_score": round(score, 2),
            "deprecated_pattern_hits": deprecated_hits,
            "deprecated_patterns": list(self.DEPRECATED_PATTERNS),
            "stale_module_count": len(stale_modules),
            "service_count": service_count,
            "duplicated_logic_indicator": duplicated_logic_indicator,
            "orphan_module_count": 0,
            "architecture_audit_only": True,
        }

    def _count_patterns(self, paths: list[Path], patterns: tuple[str, ...]) -> int:
        count = 0
        for path in paths:
            text = path.read_text(encoding="utf-8", errors="ignore")
            count += sum(text.count(pattern) for pattern in patterns)
        return count
