"""Diagnostics for release baseline reconciliation."""

from __future__ import annotations

from pathlib import Path
from typing import Any

from app.release_baseline.schemas import FORBIDDEN_BASELINE_STATES, FORBIDDEN_SOURCE_TERMS


class ReleaseBaselineDiagnostics:
    """Evaluate baseline package completeness and safety."""

    REQUIRED = {
        "source_inventory",
        "baseline_inventory",
        "commit_classification",
        "artifact_reconciliation",
        "evidence_selection",
        "cleanup_checklist",
        "ignore_review",
        "prompt_file_policy",
        "validation_churn",
        "archive_reconciliation",
        "decision_matrix",
        "scorecard",
    }

    def evaluate(self, project_root: Path, payloads: dict[str, Any]) -> list[dict[str, str]]:
        diagnostics: list[dict[str, str]] = []
        for source in payloads.get("source_inventory", {}).get("missing_sources", []):
            diagnostics.append(
                {
                    "code": "missing-source-output",
                    "severity": "متوسط",
                    "message": str(source),
                }
            )
        for key in sorted(self.REQUIRED.difference(payloads)):
            diagnostics.append(
                {"code": f"missing-{key}", "severity": "مرتفع", "message": key}
            )
        manual = sum(
            1
            for item in payloads.get("cleanup_checklist", {}).get("items", [])
            if item.get("requires_human_confirmation")
        )
        if manual > 100:
            diagnostics.append(
                {
                    "code": "excessive-manual-review-count",
                    "severity": "متوسط",
                    "message": str(manual),
                }
            )
        score = float(
            payloads.get("scorecard", {}).get("overall_baseline_readiness_score", 0.0)
        )
        if score < 75:
            diagnostics.append(
                {
                    "code": "low-baseline-readiness-score",
                    "severity": "متوسط",
                    "message": str(score),
                }
            )
        git_items = payloads.get("source_inventory", {}).get("git_status", {}).get("items", [])
        for item in git_items:
            category = str(item.get("category", ""))
            label = str(item.get("status_label", ""))
            path = str(item.get("path", ""))
            if label == "untracked" and "archive" in category:
                diagnostics.append(
                    {
                        "code": "untracked-archive-artifact",
                        "severity": "متوسط",
                        "message": path,
                    }
                )
            if label == "deleted" and path.startswith("phase"):
                diagnostics.append(
                    {
                        "code": "deleted-phase-prompt-file",
                        "severity": "مرتفع",
                        "message": path,
                    }
                )
            if label == "modified" and category in {
                "generated report change",
                "generated storage change",
            }:
                diagnostics.append(
                    {
                        "code": category.replace(" ", "-"),
                        "severity": "منخفض",
                        "message": path,
                    }
                )
        text = str(payloads)
        for state in FORBIDDEN_BASELINE_STATES:
            if state in text:
                diagnostics.append(
                    {
                        "code": "forbidden-baseline-state",
                        "severity": "مرتفع",
                        "message": state,
                    }
                )
        lowered = text.lower()
        for term in ("automatic deletion enabled", "destructive cleanup enabled"):
            if term in lowered:
                diagnostics.append(
                    {"code": "unsafe-wording", "severity": "مرتفع", "message": term}
                )
        diagnostics.extend(self._source_diagnostics(project_root))
        template = (
            project_root / "app" / "templates" / "dashboard" / "release_baseline.html"
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
            and "release_baseline" not in ar_file.read_text(encoding="utf-8")
        ):
            diagnostics.append(
                {"code": "missing-arabic-labels", "severity": "متوسط", "message": "i18n"}
            )
        return diagnostics

    def _source_diagnostics(self, project_root: Path) -> list[dict[str, str]]:
        module_dir = project_root / "app" / "release_baseline"
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
