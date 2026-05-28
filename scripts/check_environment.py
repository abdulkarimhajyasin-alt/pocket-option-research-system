"""Run environment, configuration, and orchestration diagnostics."""

from pathlib import Path
import os
import sys

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from app.config.settings import Settings  # noqa: E402
from app.logging.logger import configure_logging  # noqa: E402
from app.runtime.modes import ModePolicy  # noqa: E402
from app.runtime.orchestrator import RuntimeOrchestrator  # noqa: E402


def main() -> None:
    """Load environment config, validate startup, and print diagnostics."""
    settings = Settings()
    configure_logging(settings.log_level, settings.log_file_path)

    environment = os.getenv("TRADING_ENV", "local")
    orchestrator = RuntimeOrchestrator(PROJECT_ROOT, environment=environment)
    diagnostics = orchestrator.bootstrap()
    mode_result = ModePolicy().validate(diagnostics.mode)
    graph = diagnostics.dependency_graph

    print(
        {
            "environment": diagnostics.environment,
            "mode": diagnostics.mode,
            "mode_allowed": mode_result.allowed,
            "startup_passed": diagnostics.startup["passed"],
            "dependency_graph": graph,
            "broker": diagnostics.broker,
            "persistence": diagnostics.persistence,
            "connectivity": diagnostics.connectivity,
        }
    )
    orchestrator.shutdown()


if __name__ == "__main__":
    main()
