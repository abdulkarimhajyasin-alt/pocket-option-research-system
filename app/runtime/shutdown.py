"""Graceful runtime shutdown helpers."""

from loguru import logger

from app.runtime.runtime_state import RuntimeState


class ShutdownManager:
    """Coordinates graceful local runtime shutdown."""

    def shutdown(self, state: RuntimeState, reason: str = "completed") -> None:
        """Stop runtime state cleanly."""
        logger.info("Runtime shutdown requested: {}", reason)
        state.stop()
        logger.info("Runtime stopped: {}", state.snapshot())
