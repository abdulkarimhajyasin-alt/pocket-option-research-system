"""Parameter sensitivity and sweep analysis."""

from __future__ import annotations

from dataclasses import dataclass, field
from itertools import product
from typing import Any

from app.config.strategy_config import StrategyConfig
from app.data.models import CandleSeries
from app.validation.dataset import DatasetManager
from app.validation.models import ParameterSweepResult, ParameterSweepSummary
from app.validation.runner import ValidationBacktestRunner
from app.validation.statistics import coefficient_of_variation


@dataclass(frozen=True)
class ParameterSweepConfig:
    """Parameter sweep settings."""

    enabled: bool = True
    grid: dict[str, list[Any]] = field(default_factory=dict)
    max_combinations: int = 50


class ParameterSweepEngine:
    """Runs deterministic grid-search style parameter sensitivity tests."""

    def __init__(
        self,
        runner: ValidationBacktestRunner,
        dataset_manager: DatasetManager | None = None,
    ) -> None:
        self.runner = runner
        self.dataset_manager = dataset_manager or DatasetManager()

    def combinations(self, config: ParameterSweepConfig) -> list[dict[str, Any]]:
        """Return bounded parameter combinations."""
        names = sorted(config.grid)
        values = [config.grid[name] for name in names]
        combos = [dict(zip(names, item, strict=True)) for item in product(*values)]
        return combos[: config.max_combinations]

    def run(
        self,
        strategy_config: StrategyConfig,
        candles: CandleSeries,
        dataset_name: str,
        source: str,
        config: ParameterSweepConfig,
    ) -> ParameterSweepSummary:
        """Run a parameter sweep and summarize stable regions."""
        descriptor = self.dataset_manager.describe(
            candles,
            dataset_name,
            source,
            {"parameter_sweep": config.grid},
        )
        results: list[ParameterSweepResult] = []
        for index, parameters in enumerate(self.combinations(config)):
            run = self.runner.run(
                strategy_config,
                candles,
                descriptor,
                f"sweep_{index}",
                parameter_overrides=parameters,
            )
            stability = {
                "score_basis": round(
                    run.metrics.win_rate * 50.0
                    + max(0.0, run.metrics.net_pnl) * 2.0
                    + min(run.metrics.signal_count, 20) * 1.0,
                    4,
                )
            }
            results.append(ParameterSweepResult(parameters, run, stability))
        ranked = sorted(
            results,
            key=lambda item: (
                item.result.metrics.win_rate,
                item.result.metrics.net_pnl,
                item.result.metrics.signal_count,
            ),
            reverse=True,
        )
        stable = self._stable_regions(results)
        return ParameterSweepSummary(
            strategy_name=strategy_config.name,
            results=results,
            best_parameter_sets=[item.parameters for item in ranked[:3]],
            worst_parameter_sets=[item.parameters for item in ranked[-3:]],
            stable_parameter_regions=stable,
        )

    def _stable_regions(
        self,
        results: list[ParameterSweepResult],
    ) -> list[dict[str, Any]]:
        if not results:
            return []
        pnl_values = [item.result.metrics.net_pnl for item in results]
        win_values = [item.result.metrics.win_rate for item in results]
        pnl_variation = coefficient_of_variation(pnl_values)
        win_variation = coefficient_of_variation(win_values)
        stable_threshold = pnl_variation <= 1.0 and win_variation <= 0.5
        if not stable_threshold:
            return []
        return [
            {
                "parameter_sets": [item.parameters for item in results],
                "pnl_variation": round(pnl_variation, 4),
                "win_rate_variation": round(win_variation, 4),
            }
        ]
