"""YAML configuration loading utilities."""

from pathlib import Path
from typing import Any

import yaml
from loguru import logger


class ConfigLoader:
    """Loads YAML configuration files from the project tree."""

    def __init__(self, project_root: Path | str = ".") -> None:
        self.project_root = Path(project_root)

    def resolve_path(self, path: Path | str) -> Path:
        """Resolve a config path relative to the project root."""
        config_path = Path(path)
        if not config_path.is_absolute():
            config_path = self.project_root / config_path
        return config_path

    def load_yaml(self, path: Path | str, required: bool = True) -> dict[str, Any]:
        """Load a YAML file into a dictionary."""
        config_path = self.resolve_path(path)
        if not config_path.exists():
            if required:
                raise FileNotFoundError(f"Config file not found: {config_path}")
            logger.bind(component="orchestrator").warning(
                "Optional config missing: {}",
                config_path,
            )
            return {}
        logger.bind(component="orchestrator").info("Loading config: {}", config_path)
        raw = yaml.safe_load(config_path.read_text(encoding="utf-8")) or {}
        if not isinstance(raw, dict):
            raise ValueError(f"Config file must contain a mapping: {config_path}")
        return raw
