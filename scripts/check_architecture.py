"""Phase 18 architecture diagnostics."""

from __future__ import annotations

from pathlib import Path
import sys

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from app.i18n.validators import ArabicDashboardValidator  # noqa: E402


def _contains(path: str, *needles: str) -> bool:
    text = (PROJECT_ROOT / path).read_text(encoding="utf-8")
    return all(needle in text for needle in needles)


def main() -> None:
    """Verify Phase 18 architectural boundaries are present and wired."""
    checks = {
        "report_repository": _contains(
            "app/dashboard/routes.py",
            "ReportRepository",
            "DashboardContext",
        ),
        "runtime_factory": _contains(
            "app/runtime/runtime_manager.py",
            "RuntimeDependencyFactory",
        )
        and _contains("app/runtime/composition.py", "create_stream", "create_connector_registry"),
        "pipeline_usage": _contains(
            "app/runtime/event_loop.py",
            "CandleProcessingPipeline",
            "pipeline.process",
        )
        and _contains("app/runtime/streaming_runtime.py", "CandleProcessingPipeline"),
        "typed_events": _contains(
            "app/storage/persistence.py",
            "BaseEvent",
            "persist_event",
        ),
        "dashboard_jobs": _contains(
            "app/dashboard/routes.py",
            "JobManager",
            "/jobs",
        ),
        "dataset_refactor": _contains(
            "app/datasets/service.py",
            "DatasetInspector",
            "DatasetExporter",
            "DatasetPersistenceAdapter",
        ),
        "validation_refactor": _contains(
            "app/validation/service.py",
            "ValidationExecutionService",
            "ValidationReportExporter",
            "ValidationPersistenceAdapter",
        ),
        "arabic_dashboard": ArabicDashboardValidator(PROJECT_ROOT).validate().passed,
    }
    print(checks)
    if not all(checks.values()):
        raise SystemExit(1)


if __name__ == "__main__":
    main()
