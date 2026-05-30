"""Diagnostics for the signal intelligence engine."""

from __future__ import annotations

from pathlib import Path
import sys

from fastapi.testclient import TestClient

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from app.dashboard.routes import create_dashboard_app  # noqa: E402
from app.signal_intelligence.service import SignalIntelligenceService  # noqa: E402


def main() -> None:
    result = SignalIntelligenceService(PROJECT_ROOT).run()
    app = create_dashboard_app(PROJECT_ROOT)
    client = TestClient(app)
    response = client.get("/signals-intelligence")
    api_response = client.get("/api/signals-intelligence")
    template_text = (
        PROJECT_ROOT / "app/templates/dashboard/signals_intelligence.html"
    ).read_text(encoding="utf-8")
    checks = {
        "signals_generated": result.analytics["summary"]["signal_count"] > 0,
        "confidence": result.analytics["summary"]["highest_confidence"] <= 100,
        "reports": all(Path(path).exists() for path in result.report_paths.values()),
        "storage": all(Path(path).exists() for path in result.storage_paths.values()),
        "dashboard": response.status_code == 200 and api_response.status_code == 200,
        "arabic": all(
            label in (template_text + response.text)
            for label in (
                "ذكاء الإشارات",
                "أفضل فرصة حالية",
                "عدد الإشارات",
                "متوسط الثقة",
                "توزيع الإشارات",
            )
        )
        and "Signal Intelligence" not in template_text,
        "research_only": all(
            signal.get("research_only") is True
            for signal in result.analytics.get("latest_signals", [])
        ),
    }
    print(checks)
    if not all(checks.values()):
        raise SystemExit(1)


if __name__ == "__main__":
    main()
