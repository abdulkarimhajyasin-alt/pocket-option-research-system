"""Diagnostics for repository hygiene outputs."""

from __future__ import annotations

from pathlib import Path
from typing import Any

from app.repository_hygiene.schemas import FORBIDDEN_SOURCE_TERMS


class RepositoryHygieneDiagnostics:
    """Evaluate repository hygiene completeness and safety."""

    REQUIRED = {
        "git_status_inventory",
        "artifact_inventory",
        "artifact_classification",
        "retention_policy",
        "cleanup_plan",
        "ignore_recommendations",
        "duplicate_artifacts",
        "stale_artifacts",
        "archive_policy",
        "scorecard",
    }

    def evaluate(self, project_root: Path, payloads: dict[str, Any]) -> list[dict[str, str]]:
        diagnostics: list[dict[str, str]] = []
        for key in sorted(self.REQUIRED.difference(payloads)):
            diagnostics.append({"code": f"missing-{key}", "severity": "مرتفع", "message": key})
        git_items = payloads.get("git_status_inventory", {}).get("items", [])
        for item in git_items:
            category = str(item.get("category", ""))
            label = str(item.get("status_label", ""))
            if label == "untracked" and "archive" in category:
                diagnostics.append(
                    {
                        "code": "untracked-generated-artifact",
                        "severity": "متوسط",
                        "message": str(item.get("path")),
                    }
                )
            if label == "deleted" and str(item.get("path", "")).startswith("phase"):
                diagnostics.append(
                    {
                        "code": "deleted-phase-prompt-file",
                        "severity": "مرتفع",
                        "message": str(item.get("path")),
                    }
                )
            if label == "modified" and category in {
                "generated report change",
                "generated storage change",
            }:
                diagnostics.append(
                    {
                        "code": category.replace(" ", "-"),
                        "severity": "متوسط",
                        "message": str(item.get("path")),
                    }
                )
        if payloads.get("duplicate_artifacts", {}).get("items"):
            diagnostics.append(
                {
                    "code": "duplicate-generated-artifact-names",
                    "severity": "منخفض",
                    "message": "duplicates",
                }
            )
        if payloads.get("stale_artifacts", {}).get("items"):
            diagnostics.append(
                {
                    "code": "stale-archive-snapshots",
                    "severity": "متوسط",
                    "message": "stale",
                }
            )
        if payloads.get("git_status_inventory", {}).get("git_unavailable"):
            diagnostics.append(
                {"code": "git-unavailable", "severity": "متوسط", "message": "git"}
            )
        text = str(payloads).lower()
        for term in ("automatic deletion enabled", "destructive cleanup enabled"):
            if term in text:
                diagnostics.append(
                    {"code": "unsafe-wording", "severity": "مرتفع", "message": term}
                )
        diagnostics.extend(self._source_diagnostics(project_root))
        template = (
            project_root
            / "app"
            / "templates"
            / "dashboard"
            / "repository_hygiene.html"
        )
        if not template.exists():
            diagnostics.append(
                {
                    "code": "missing-dashboard-integration",
                    "severity": "متوسط",
                    "message": "template",
                }
            )
        ar_file = project_root / "app" / "i18n" / "ar.py"
        if (
            ar_file.exists()
            and "repository_hygiene" not in ar_file.read_text(encoding="utf-8")
        ):
            diagnostics.append(
                {"code": "missing-arabic-labels", "severity": "متوسط", "message": "i18n"}
            )
        return diagnostics

    def _source_diagnostics(self, project_root: Path) -> list[dict[str, str]]:
        module_dir = project_root / "app" / "repository_hygiene"
        if not module_dir.exists():
            return [{"code": "missing-module", "severity": "مرتفع", "message": "module"}]
        text = "\n".join(
            path.read_text(encoding="utf-8").lower() for path in module_dir.glob("*.py")
        )
        return [
            {
                "code": "forbidden-implementation-artifact",
                "severity": "مرتفع",
                "message": term,
            }
            for term in FORBIDDEN_SOURCE_TERMS
            if term in text
        ]
