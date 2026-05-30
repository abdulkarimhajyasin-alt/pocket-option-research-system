"""Run the Phase 20 offline execution simulation lab."""

from __future__ import annotations

from pathlib import Path
import sys

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from app.execution_simulator.lab import ExecutionSimulationLab  # noqa: E402


def main() -> None:
    """Run local-only execution simulation and print a compact summary."""
    result = ExecutionSimulationLab(PROJECT_ROOT).run()
    print(result.summary())


if __name__ == "__main__":
    main()
