"""Centralized configuration manager."""

from dataclasses import dataclass
from pathlib import Path
from typing import Any

from loguru import logger

from app.config.environment import EnvironmentName, EnvironmentProfile
from app.config.loader import ConfigLoader
from app.config.resolver import ConfigResolver, deep_merge
from app.config.validators import ConfigValidationResult, ConfigValidator


@dataclass(frozen=True)
class AppConfig:
    """Typed access wrapper around resolved application configuration."""

    environment: EnvironmentProfile
    data: dict[str, Any]
    validation: ConfigValidationResult

    def get(self, path: str, default: Any = None) -> Any:
        """Return a nested config value using dot notation."""
        cursor: Any = self.data
        for part in path.split("."):
            if not isinstance(cursor, dict) or part not in cursor:
                return default
            cursor = cursor[part]
        return cursor

    def section(self, name: str) -> dict[str, Any]:
        """Return a named top-level configuration section."""
        value = self.data.get(name, {})
        return dict(value) if isinstance(value, dict) else {}


class ConfigManager:
    """Loads, resolves, and validates environment-aware configuration."""

    def __init__(self, project_root: Path | str = ".", env_prefix: str = "TRADING") -> None:
        self.project_root = Path(project_root)
        self.loader = ConfigLoader(self.project_root)
        self.resolver = ConfigResolver(env_prefix=env_prefix)
        self.validator = ConfigValidator(self.project_root)

    def load(self, environment: str | EnvironmentName = EnvironmentName.LOCAL) -> AppConfig:
        """Load a resolved application configuration for an environment."""
        profile = self._load_profile(str(environment))
        logger.bind(component="orchestrator").info(
            "Resolving environment profile {}",
            profile.name.value,
        )
        layers = [
            {"environment": profile.__dict__},
            {"runtime": self.loader.load_yaml(profile.runtime_config)},
            {"strategy": self.loader.load_yaml(profile.strategy_config)},
            {"risk": self.loader.load_yaml(profile.risk_config)},
            {"broker": self.loader.load_yaml(profile.broker_config)},
            {"storage": self.loader.load_yaml(profile.storage_config)},
            {"connectivity": self.loader.load_yaml(profile.connectivity_config)},
            {"settings": profile.settings},
        ]
        resolved = self.resolver.resolve(layers)
        validation = self.validator.validate(resolved)
        return AppConfig(environment=profile, data=resolved, validation=validation)

    def _load_profile(self, name: str) -> EnvironmentProfile:
        profile_path = Path("configs") / "environments" / f"{name}.yaml"
        raw = self.loader.load_yaml(profile_path)
        parent_name = raw.get("inherits")
        if parent_name:
            parent = self._load_profile(str(parent_name))
            parent_raw = parent.__dict__.copy()
            parent_raw["name"] = parent.name.value
            merged = deep_merge(parent_raw, raw)
            return EnvironmentProfile.from_dict(merged)
        return EnvironmentProfile.from_dict(raw)
