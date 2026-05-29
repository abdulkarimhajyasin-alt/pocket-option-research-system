"""Professional loguru logging configuration."""

import sys
from pathlib import Path

from loguru import logger


def configure_logging(log_level: str = "INFO", log_file_path: Path | str = "logs/app.log") -> None:
    """Configure console and rotating file logging."""
    log_path = Path(log_file_path)
    log_path.parent.mkdir(parents=True, exist_ok=True)

    logger.remove()
    log_format = (
        "<green>{time:YYYY-MM-DD HH:mm:ss.SSS}</green> | "
        "<level>{level: <8}</level> | "
        "<cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> | "
        "<level>{message}</level>"
    )

    logger.add(sys.stdout, level=log_level, format=log_format, colorize=True)
    logger.add(
        log_path,
        level=log_level,
        format=(
            "{time:YYYY-MM-DD HH:mm:ss.SSS} | {level: <8} | "
            "{name}:{function}:{line} | {message}"
        ),
        rotation="10 MB",
        retention="14 days",
        compression="zip",
        enqueue=True,
    )
    logger.add(
        log_path.parent / "risk_events.log",
        level=log_level,
        format=(
            "{time:YYYY-MM-DD HH:mm:ss.SSS} | {level: <8} | "
            "{extra[component]} | {message}"
        ),
        filter=lambda record: record["extra"].get("component") == "risk",
        rotation="10 MB",
        retention="30 days",
        compression="zip",
        enqueue=True,
    )
    logger.add(
        log_path.parent / "runtime.log",
        level=log_level,
        format=(
            "{time:YYYY-MM-DD HH:mm:ss.SSS} | {level: <8} | "
            "{name}:{function}:{line} | {message}"
        ),
        rotation="10 MB",
        retention="14 days",
        compression="zip",
        enqueue=True,
    )
    logger.add(
        log_path.parent / "analytics.log",
        level=log_level,
        format=(
            "{time:YYYY-MM-DD HH:mm:ss.SSS} | {level: <8} | "
            "{extra[component]} | {message}"
        ),
        filter=lambda record: record["extra"].get("component") == "analytics",
        rotation="10 MB",
        retention="30 days",
        compression="zip",
        enqueue=True,
    )
    logger.add(
        log_path.parent / "broker.log",
        level=log_level,
        format=(
            "{time:YYYY-MM-DD HH:mm:ss.SSS} | {level: <8} | "
            "{extra[component]} | {message}"
        ),
        filter=lambda record: record["extra"].get("component") == "broker",
        rotation="10 MB",
        retention="30 days",
        compression="zip",
        enqueue=True,
    )
    logger.add(
        log_path.parent / "storage.log",
        level=log_level,
        format=(
            "{time:YYYY-MM-DD HH:mm:ss.SSS} | {level: <8} | "
            "{extra[component]} | {message}"
        ),
        filter=lambda record: record["extra"].get("component") == "storage",
        rotation="10 MB",
        retention="30 days",
        compression="zip",
        enqueue=True,
    )
    logger.add(
        log_path.parent / "orchestrator.log",
        level=log_level,
        format=(
            "{time:YYYY-MM-DD HH:mm:ss.SSS} | {level: <8} | "
            "{extra[component]} | {message}"
        ),
        filter=lambda record: record["extra"].get("component") == "orchestrator",
        rotation="10 MB",
        retention="30 days",
        compression="zip",
        enqueue=True,
    )
    logger.add(
        log_path.parent / "connectivity.log",
        level=log_level,
        format=(
            "{time:YYYY-MM-DD HH:mm:ss.SSS} | {level: <8} | "
            "{extra[component]} | {message}"
        ),
        filter=lambda record: record["extra"].get("component") == "connectivity",
        rotation="10 MB",
        retention="30 days",
        compression="zip",
        enqueue=True,
    )
    logger.add(
        log_path.parent / "streaming.log",
        level=log_level,
        format=(
            "{time:YYYY-MM-DD HH:mm:ss.SSS} | {level: <8} | "
            "{extra[component]} | {message}"
        ),
        filter=lambda record: record["extra"].get("component") == "streaming",
        rotation="10 MB",
        retention="30 days",
        compression="zip",
        enqueue=True,
    )
