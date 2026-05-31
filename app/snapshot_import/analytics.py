"""Analytics for manual snapshot imports."""

from __future__ import annotations

from collections import Counter
from typing import Any

from app.snapshot_import.models import SnapshotImportResult


class SnapshotImportAnalytics:
    """Generate import, quality, validation, processing, and safety analytics."""

    def summarize(self, result: SnapshotImportResult) -> dict[str, Any]:
        import_types = Counter(item.import_type for item in result.imports)
        diagnostics = Counter(item.severity for item in result.diagnostics)
        recommendations = Counter(item.title for item in result.recommendations)
        quality_trend = {
            item.filename: 100.0 if item.validation_status == "ناجح" else 50.0
            for item in result.imports
        }
        completeness = {
            item.filename: 100.0 if item.size_bytes > 0 else 0.0
            for item in result.imports
        }
        return {
            "summary": {
                "import_count": len(result.imports),
                "workflow_score": result.workflow.score,
                "workflow_state": result.workflow.state,
                "quality_score": result.quality.score,
                "validation_score": result.validation.score,
                "processing_score": result.processing.score,
                "safety_score": result.safety.score,
                "warning_count": len(result.diagnostics),
                "recommendation_count": len(result.recommendations),
                "last_import": result.timestamp.isoformat(),
                "manual_only": True,
                "research_only": True,
                "observation_only": True,
            },
            "import_distribution": dict(import_types),
            "quality_distribution": result.quality.to_dict(),
            "validation_distribution": result.validation.to_dict(),
            "processing_distribution": result.processing.to_dict(),
            "safety_distribution": {
                "لا تسجيل دخول": 100.0 if result.safety.no_login else 0.0,
                "لا مصادقة": 100.0 if result.safety.no_authentication else 0.0,
                "لا أتمتة متصفح": 100.0
                if result.safety.no_browser_automation
                else 0.0,
                "لا وصول وسيط": 100.0 if result.safety.no_broker_access else 0.0,
                "لا تنفيذ": 100.0 if result.safety.no_execution else 0.0,
                "لا تفاعل حساب": 100.0
                if result.safety.no_account_interaction
                else 0.0,
            },
            "file_quality": quality_trend,
            "file_completeness": completeness,
            "quality_timeline": quality_trend,
            "diagnostics_distribution": dict(diagnostics),
            "recommendation_distribution": dict(recommendations),
            "latest": result.to_dict(),
        }
