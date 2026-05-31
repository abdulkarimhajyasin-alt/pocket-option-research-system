"""Read-only adapter for already supplied browser observation artifacts."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from app.browser_observation.models import AdapterScore
from app.browser_observation.models import ObservationArtifact
from app.browser_observation.models import SUPPORTED_ARTIFACT_TYPES
from app.browser_observation.validator import average


def readiness_state(score: float) -> tuple[str, str]:
    """Return Arabic readiness state for the read-only adapter."""
    if score >= 95:
        return "جاهزة للمراقبة المتقدمة", "اللقطات كافية للمراقبة المتقدمة."
    if score >= 85:
        return "جاهزة بشروط", "اللقطات صالحة مع متابعة بعض التحسينات."
    if score >= 70:
        return "تحتاج تحسين محدود", "اللقطات صالحة بحثيا مع فجوات محدودة."
    if score >= 50:
        return "تحتاج تحسين كبير", "اللقطات تحتاج تحسينات قبل التوسع."
    return "غير مؤهلة", "اللقطات غير كافية للمراقبة التحليلية."


class ReadOnlyObservationAdapter:
    """Load, inspect, parse, and summarize local read-only artifacts."""

    def __init__(self, project_root: Path | str = ".") -> None:
        self.project_root = Path(project_root)

    def load_artifacts(self) -> tuple[ObservationArtifact, ...]:
        artifact_specs = [
            (
                "html-summary",
                "html_snapshot",
                self.project_root / "reports" / "observation" / "observation_summary.json",
            ),
            (
                "dom-export-summary",
                "dom_export",
                self.project_root / "reports" / "external_observation" / "source_report.json",
            ),
            (
                "page-capture-summary",
                "page_capture",
                self.project_root / "reports" / "broker_readiness" / "readiness_summary.json",
            ),
            (
                "observation-dump",
                "observation_dump",
                self.project_root / "storage" / "external_observation" / "diagnostics.json",
            ),
            (
                "static-snapshot",
                "static_snapshot",
                self.project_root / "data" / "sample_eurusd_m1.csv",
            ),
        ]
        return tuple(self._build_artifact(*item) for item in artifact_specs)

    def score(
        self,
        parse_score: float,
        validation_score: float,
        visibility_score: float,
        monitoring_score: float,
        safety_score: float,
    ) -> AdapterScore:
        score = average(
            [
                parse_score,
                validation_score,
                visibility_score,
                monitoring_score,
                safety_score,
            ]
        )
        state, explanation = readiness_state(score)
        return AdapterScore(score=score, state=state, explanation=explanation)

    def _build_artifact(
        self,
        artifact_id: str,
        artifact_type: str,
        path: Path,
    ) -> ObservationArtifact:
        exists = path.exists()
        readable = self._is_readable(path) if exists else False
        created_at = (
            path.stat().st_mtime_ns if exists else 0
        )
        return ObservationArtifact(
            artifact_id=artifact_id,
            artifact_type=artifact_type,
            artifact_source=str(path),
            created_at=str(created_at),
            validation_status="ناجح"
            if exists and readable and artifact_type in SUPPORTED_ARTIFACT_TYPES
            else "تحذير",
            visibility_status="مرئي" if exists and readable else "ناقص",
            monitoring_status="مستقر" if exists and readable else "غير مكتمل",
            metadata={
                "exists": exists,
                "readable": readable,
                "read_only": True,
                "artifact_size": path.stat().st_size if exists else 0,
            },
        )

    def _is_readable(self, path: Path) -> bool:
        try:
            if path.suffix.lower() == ".json":
                payload: Any = json.loads(path.read_text(encoding="utf-8"))
                return isinstance(payload, (dict, list))
            text = path.read_text(encoding="utf-8")
            return bool(text.strip())
        except (OSError, UnicodeDecodeError, json.JSONDecodeError):
            return False
