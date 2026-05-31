from pathlib import Path

from fastapi.testclient import TestClient

from app.dashboard.routes import create_dashboard_app
from app.snapshot_import.importer import SnapshotImporter
from app.snapshot_import.parser import SnapshotParserEngine
from app.snapshot_import.processor import SnapshotProcessingEngine
from app.snapshot_import.processor import SnapshotQualityEngine
from app.snapshot_import.service import SnapshotImportService
from app.snapshot_import.validator import SnapshotValidationEngine
from app.snapshot_import.workflow import SnapshotImportWorkflow
from app.snapshot_import.workflow import SnapshotSafetyEngine


def test_snapshot_import_engines_are_bounded_and_manual_only():
    imports = SnapshotImporter(Path(".")).register_uploads()
    validation = SnapshotValidationEngine().validate(imports)
    parse = SnapshotParserEngine().parse(imports)
    processing = SnapshotProcessingEngine().process(imports, parse, validation)
    quality = SnapshotQualityEngine().evaluate(imports, validation, processing)
    safety = SnapshotSafetyEngine().evaluate()
    workflow = SnapshotImportWorkflow().score(validation, processing, quality, safety)

    assert len(imports) >= 1
    assert 0 <= validation.score <= 100
    assert 0 <= parse.score <= 100
    assert 0 <= processing.score <= 100
    assert 0 <= quality.score <= 100
    assert 0 <= workflow.score <= 100
    assert safety.status == "PASS"
    assert safety.no_login is True
    assert safety.no_authentication is True
    assert safety.no_browser_automation is True
    assert safety.no_broker_access is True
    assert safety.no_execution is True
    assert safety.no_account_interaction is True


def test_snapshot_import_service_generates_outputs():
    run = SnapshotImportService(Path(".")).run()
    assert run.result.workflow.state
    assert run.result.metadata["manual_only"] is True
    assert run.result.metadata["observation_only"] is True
    assert run.result.metadata["not_execution"] is True
    assert run.result.metadata["not_order_placement"] is True
    assert run.result.metadata["not_account_login"] is True
    assert run.result.metadata["not_broker_authentication"] is True
    assert run.result.metadata["not_credential_handling"] is True
    assert run.result.metadata["not_browser_automation"] is True
    assert run.result.metadata["not_broker_control"] is True
    assert run.result.to_dict()["manual_only"] is True
    assert all(Path(path).exists() for path in run.storage_paths.values())
    assert all(Path(path).exists() for path in run.report_paths.values())


def test_snapshot_import_dashboard_and_api_are_arabic():
    SnapshotImportService(Path(".")).run()
    client = TestClient(create_dashboard_app(Path(".")))
    page = client.get("/snapshot-import")
    api = client.get("/api/snapshot-import")
    assert page.status_code == 200
    assert api.status_code == 200
    assert "مركز استيراد اللقطات" in page.text
    assert "رفع ملف يدوي" in page.text
    assert "توزيع اللقطات" in page.text
    assert "Snapshot Import" not in page.text
    assert api.json()["summary"]["manual_only"] is True
