"""YAML configuration for strategy validation research."""

from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

import yaml

from app.validation.models import WindowMode
from app.validation.out_of_sample import OutOfSampleConfig
from app.validation.parameter_sweep import ParameterSweepConfig
from app.validation.walk_forward import WalkForwardConfig


@dataclass(frozen=True)
class RobustnessScoringConfig:
    """Robustness scoring feature switch."""

    enabled: bool = True


@dataclass(frozen=True)
class ValidationResearchConfig:
    """Top-level validation configuration."""

    enabled: bool = True
    dataset_name: str = "sample_eurusd_m1"
    dataset_path: str = "data/sample_eurusd_m1.csv"
    strategy_config_path: str = "configs/strategies/research_cisd_fvg_strategy.yaml"
    risk_profile_path: str = "configs/risk/base_risk.yaml"
    reports_dir: str = "reports/validation"
    walk_forward: WalkForwardConfig = field(default_factory=WalkForwardConfig)
    out_of_sample: OutOfSampleConfig = field(default_factory=OutOfSampleConfig)
    parameter_sweeps: ParameterSweepConfig = field(default_factory=ParameterSweepConfig)
    robustness_scoring: RobustnessScoringConfig = field(default_factory=RobustnessScoringConfig)


class ValidationConfigLoader:
    """Load validation research settings from YAML."""

    def load(self, path: Path | str) -> ValidationResearchConfig:
        """Load and validate validation config."""
        raw = yaml.safe_load(Path(path).read_text(encoding="utf-8")) or {}
        walk_forward = raw.get("walk_forward", {})
        out_of_sample = raw.get("out_of_sample", {})
        parameter_sweeps = raw.get("parameter_sweeps", {})
        robustness = raw.get("robustness_scoring", {})
        validation = raw.get("validation", {})
        return ValidationResearchConfig(
            enabled=bool(validation.get("enabled", raw.get("enabled", True))),
            dataset_name=str(raw.get("dataset_name", "sample_eurusd_m1")),
            dataset_path=str(raw.get("dataset_path", "data/sample_eurusd_m1.csv")),
            strategy_config_path=str(
                raw.get(
                    "strategy_config_path",
                    "configs/strategies/research_cisd_fvg_strategy.yaml",
                )
            ),
            risk_profile_path=str(raw.get("risk_profile_path", "configs/risk/base_risk.yaml")),
            reports_dir=str(raw.get("reports_dir", "reports/validation")),
            walk_forward=WalkForwardConfig(
                enabled=bool(walk_forward.get("enabled", True)),
                mode=WindowMode(str(walk_forward.get("mode", WindowMode.ROLLING.value))),
                train_size=int(walk_forward.get("train_size", 120)),
                validation_size=int(walk_forward.get("validation_size", 40)),
                test_size=int(walk_forward.get("test_size", 40)),
                step_size=int(walk_forward.get("step_size", 40)),
                minimum_samples=int(walk_forward.get("minimum_samples", 120)),
            ),
            out_of_sample=OutOfSampleConfig(
                enabled=bool(out_of_sample.get("enabled", True)),
                in_sample_ratio=float(out_of_sample.get("in_sample_ratio", 0.70)),
                minimum_samples=int(out_of_sample.get("minimum_samples", 80)),
            ),
            parameter_sweeps=ParameterSweepConfig(
                enabled=bool(parameter_sweeps.get("enabled", True)),
                grid=dict(parameter_sweeps.get("grid", {})),
                max_combinations=int(parameter_sweeps.get("max_combinations", 50)),
            ),
            robustness_scoring=RobustnessScoringConfig(
                enabled=bool(robustness.get("enabled", True))
            ),
        )


def config_to_dict(config: ValidationResearchConfig) -> dict[str, Any]:
    """Return a serializable validation config summary."""
    return {
        "enabled": config.enabled,
        "dataset_name": config.dataset_name,
        "dataset_path": config.dataset_path,
        "strategy_config_path": config.strategy_config_path,
        "risk_profile_path": config.risk_profile_path,
        "reports_dir": config.reports_dir,
        "walk_forward": {
            "enabled": config.walk_forward.enabled,
            "mode": config.walk_forward.mode.value,
            "train_size": config.walk_forward.train_size,
            "validation_size": config.walk_forward.validation_size,
            "test_size": config.walk_forward.test_size,
            "step_size": config.walk_forward.step_size,
            "minimum_samples": config.walk_forward.minimum_samples,
        },
        "out_of_sample": {
            "enabled": config.out_of_sample.enabled,
            "in_sample_ratio": config.out_of_sample.in_sample_ratio,
            "minimum_samples": config.out_of_sample.minimum_samples,
        },
        "parameter_sweeps": {
            "enabled": config.parameter_sweeps.enabled,
            "grid": config.parameter_sweeps.grid,
            "max_combinations": config.parameter_sweeps.max_combinations,
        },
        "robustness_scoring": {"enabled": config.robustness_scoring.enabled},
    }
