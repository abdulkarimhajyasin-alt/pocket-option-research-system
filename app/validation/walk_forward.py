"""Walk-forward validation engine."""

from __future__ import annotations

from dataclasses import dataclass

from loguru import logger

from app.config.strategy_config import StrategyConfig
from app.data.models import CandleSeries
from app.validation.dataset import DatasetManager
from app.validation.models import (
    WalkForwardResult,
    WalkForwardWindow,
    WalkForwardWindowResult,
    WindowMode,
)
from app.validation.runner import ValidationBacktestRunner
from app.validation.statistics import coefficient_of_variation, mean


@dataclass(frozen=True)
class WalkForwardConfig:
    """Configurable walk-forward split settings."""

    enabled: bool = True
    mode: WindowMode = WindowMode.ROLLING
    train_size: int = 120
    validation_size: int = 40
    test_size: int = 40
    step_size: int = 40
    minimum_samples: int = 120


class WalkForwardValidator:
    """Splits data into rolling or expanding train/validation/test windows."""

    def __init__(
        self,
        runner: ValidationBacktestRunner,
        dataset_manager: DatasetManager | None = None,
    ) -> None:
        self.runner = runner
        self.dataset_manager = dataset_manager or DatasetManager()

    def split(self, sample_count: int, config: WalkForwardConfig) -> list[WalkForwardWindow]:
        """Create deterministic walk-forward windows."""
        if sample_count < config.minimum_samples:
            return []
        windows: list[WalkForwardWindow] = []
        index = 0
        start = 0
        while True:
            train_start = 0 if config.mode == WindowMode.EXPANDING else start
            train_end = start + config.train_size
            validation_end = train_end + config.validation_size
            test_end = validation_end + config.test_size
            if test_end > sample_count:
                break
            windows.append(
                WalkForwardWindow(
                    index=index,
                    train_start=train_start,
                    train_end=train_end,
                    validation_start=train_end,
                    validation_end=validation_end,
                    test_start=validation_end,
                    test_end=test_end,
                )
            )
            index += 1
            start += config.step_size
        return windows

    def run(
        self,
        strategy_config: StrategyConfig,
        candles: CandleSeries,
        dataset_name: str,
        source: str,
        config: WalkForwardConfig,
    ) -> WalkForwardResult:
        """Run walk-forward validation."""
        windows = self.split(len(candles), config)
        results: list[WalkForwardWindowResult] = []
        for window in windows:
            descriptor = self.dataset_manager.describe(
                candles,
                dataset_name,
                source,
                {"walk_forward_window": window.to_dict(), "mode": config.mode.value},
            )
            train = self.runner.run(
                strategy_config,
                self.dataset_manager.slice(candles, window.train_start, window.train_end),
                descriptor,
                f"wf_{window.index}_train",
            )
            validation = self.runner.run(
                strategy_config,
                self.dataset_manager.slice(
                    candles,
                    window.validation_start,
                    window.validation_end,
                ),
                descriptor,
                f"wf_{window.index}_validation",
            )
            test = self.runner.run(
                strategy_config,
                self.dataset_manager.slice(candles, window.test_start, window.test_end),
                descriptor,
                f"wf_{window.index}_test",
            )
            results.append(WalkForwardWindowResult(window, train, validation, test))
        aggregate = self._aggregate(results)
        stability = self._stability(results)
        logger.bind(component="strategy_validation").info(
            "Walk-forward completed windows={} stability={}",
            len(results),
            stability,
        )
        return WalkForwardResult(
            strategy_name=strategy_config.name,
            mode=config.mode,
            windows=results,
            aggregate_metrics=aggregate,
            stability_metrics=stability,
        )

    def _aggregate(
        self,
        results: list[WalkForwardWindowResult],
    ) -> dict[str, float | int]:
        test_metrics = [result.test.metrics for result in results]
        return {
            "windows": len(results),
            "average_test_win_rate": round(mean([item.win_rate for item in test_metrics]), 4),
            "average_test_net_pnl": round(mean([item.net_pnl for item in test_metrics]), 4),
            "average_test_signals": round(mean([item.signal_count for item in test_metrics]), 4),
        }

    def _stability(
        self,
        results: list[WalkForwardWindowResult],
    ) -> dict[str, float | int]:
        test_metrics = [result.test.metrics for result in results]
        pnl_values = [item.net_pnl for item in test_metrics]
        win_rates = [item.win_rate for item in test_metrics]
        signal_counts = [float(item.signal_count) for item in test_metrics]
        return {
            "pnl_variation": round(coefficient_of_variation(pnl_values), 4),
            "win_rate_variation": round(coefficient_of_variation(win_rates), 4),
            "signal_count_variation": round(coefficient_of_variation(signal_counts), 4),
            "positive_window_rate": (
                round(sum(1 for value in pnl_values if value >= 0) / len(pnl_values), 4)
                if pnl_values
                else 0.0
            ),
        }
