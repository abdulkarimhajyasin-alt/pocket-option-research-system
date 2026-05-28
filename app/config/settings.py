"""Application settings for the research platform foundation."""

from dataclasses import dataclass
from pathlib import Path


@dataclass(frozen=True)
class Settings:
    """Static application settings for the Phase 1 demo runtime."""

    environment: str = "development"
    log_level: str = "INFO"
    log_file_path: Path = Path("logs/app.log")
    mock_initial_balance: float = 10_000.0
    min_signal_confidence: float = 0.60
