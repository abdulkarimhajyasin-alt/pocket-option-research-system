"""Run the safety-boundary-only integration safety layer."""

from __future__ import annotations

from pathlib import Path
import sys

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from app.integration_safety.service import IntegrationSafetyService  # noqa: E402


def main() -> None:
    """Generate integration safety storage and reports."""
    run = IntegrationSafetyService(PROJECT_ROOT).run()
    policy = run.result.policy
    print("Integration safety boundary generated")
    print(f"boundary_status={policy.boundary_status}")
    print(f"safety_score={policy.safety_score}")
    print(f"compliance_score={policy.compliance_score}")
    print("safety_boundary_only=True")
    print("readiness_only=True")
    print("research_only=True")
    print("not_broker_access=True")
    print("not_browser_automation=True")
    print("not_external_execution_adapter=True")
    print(f"storage={run.storage_paths}")
    print(f"reports={run.report_paths}")


if __name__ == "__main__":
    main()
