"""Run the architecture-audit-only production hardening layer."""

from __future__ import annotations

from pathlib import Path
import sys

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from app.architecture_audit.service import ArchitectureAuditService  # noqa: E402


def main() -> None:
    """Generate architecture audit storage and reports."""
    run = ArchitectureAuditService(PROJECT_ROOT).run()
    certification = run.result.certification
    print("Architecture audit generated")
    print(f"overall_score={certification.overall_score}")
    print(f"certification_state={certification.certification_state}")
    print(f"safety_score={certification.safety_score}")
    print("architecture_audit_only=True")
    print("hardening_only=True")
    print("research_only=True")
    print("not_real_execution=True")
    print("not_broker_access=True")
    print(f"storage={run.storage_paths}")
    print(f"reports={run.report_paths}")


if __name__ == "__main__":
    main()
