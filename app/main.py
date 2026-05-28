"""Application entry point for the orchestrated research platform."""

import os
from pathlib import Path

from loguru import logger

from app.config.settings import Settings
from app.logging.logger import configure_logging
from app.runtime.orchestrator import RuntimeOrchestrator


def main() -> None:
    """Run environment-aware startup diagnostics and a local paper runtime."""
    settings = Settings()
    configure_logging(settings.log_level, settings.log_file_path)
    environment = os.getenv("TRADING_ENV", "local")
    orchestrator = RuntimeOrchestrator(Path.cwd(), environment=environment)
    diagnostics = orchestrator.bootstrap()
    logger.bind(component="orchestrator").info("Startup diagnostics: {}", diagnostics.to_dict())
    state = orchestrator.start()
    orchestrator.shutdown()
    print({"environment": environment, "runtime": state.snapshot()})


if __name__ == "__main__":
    main()
