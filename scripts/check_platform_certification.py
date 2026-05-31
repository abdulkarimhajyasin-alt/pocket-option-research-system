"""Validate final research platform certification."""

from __future__ import annotations

import json
from pathlib import Path
import sys

from fastapi.testclient import TestClient

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from app.dashboard.routes import create_dashboard_app  # noqa: E402
from app.platform_certification.schemas import FORBIDDEN_STATES  # noqa: E402
from app.platform_certification.service import PlatformCertificationService  # noqa: E402


def main() -> None:
    """Run certification compliance checks."""
    service = PlatformCertificationService(PROJECT_ROOT)
    run = service.run()
    payload = run.certification.to_dict()
    storage_dir = PROJECT_ROOT / "storage" / "platform_certification"
    report_dir = PROJECT_ROOT / "reports" / "platform_certification"
    required_storage = {
        storage_dir / "certification_results.json",
        storage_dir / "domain_scores.json",
        storage_dir / "diagnostics.json",
        storage_dir / "recommendations.json",
    }
    required_reports = {
        report_dir / "certification_report.json",
        report_dir / "executive_summary.json",
        report_dir / "domain_report.json",
        report_dir / "diagnostics_report.json",
        report_dir / "recommendations_report.json",
    }
    app = create_dashboard_app(PROJECT_ROOT)
    client = TestClient(app)
    responses = {
        "page": client.get("/platform-certification"),
        "root": client.get("/api/platform-certification"),
        "summary": client.get("/api/platform-certification/summary"),
        "domains": client.get("/api/platform-certification/domains"),
        "diagnostics": client.get("/api/platform-certification/diagnostics"),
        "recommendations": client.get("/api/platform-certification/recommendations"),
    }
    text = json.dumps(payload, ensure_ascii=False)
    checks = {
        "storage_files": all(path.exists() for path in required_storage),
        "report_files": all(path.exists() for path in required_reports),
        "json_valid": all(_valid_json(path) for path in required_storage | required_reports),
        "research_only": payload["research_only"] is True,
        "local_only": payload["local_only"] is True,
        "safe_boundary": all(payload["safety_boundary"].values()),
        "no_forbidden_states": not any(state in text for state in FORBIDDEN_STATES),
        "domains": len(payload["domain_scores"]) == 10,
        "routes": all(response.status_code == 200 for response in responses.values()),
        "api_root": responses["root"].json()["research_only"] is True,
        "api_summary": responses["summary"].json()["research_only"] is True,
        "arabic": "الشهادة النهائية للمنصة البحثية" in responses["page"].text,
    }
    print(checks)
    if not all(checks.values()):
        raise SystemExit(1)


def _valid_json(path: Path) -> bool:
    try:
        json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return False
    return True


if __name__ == "__main__":
    main()
