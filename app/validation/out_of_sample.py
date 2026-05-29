"""Out-of-sample validation framework."""

from __future__ import annotations

from dataclasses import dataclass

from app.config.strategy_config import StrategyConfig
from app.data.models import CandleSeries
from app.validation.dataset import DatasetManager
from app.validation.models import OutOfSampleResult
from app.validation.runner import ValidationBacktestRunner
from app.validation.statistics import clamp


@dataclass(frozen=True)
class OutOfSampleConfig:
    """Out-of-sample split settings."""

    enabled: bool = True
    in_sample_ratio: float = 0.70
    minimum_samples: int = 80


class OutOfSampleValidator:
    """Runs isolated in-sample and out-of-sample tests."""

    def __init__(
        self,
        runner: ValidationBacktestRunner,
        dataset_manager: DatasetManager | None = None,
    ) -> None:
        self.runner = runner
        self.dataset_manager = dataset_manager or DatasetManager()

    def run(
        self,
        strategy_config: StrategyConfig,
        candles: CandleSeries,
        dataset_name: str,
        source: str,
        config: OutOfSampleConfig,
    ) -> OutOfSampleResult:
        """Run in-sample and out-of-sample validation without metric contamination."""
        if len(candles) < config.minimum_samples:
            raise ValueError("Not enough candles for out-of-sample validation")
        split_index = max(1, min(len(candles) - 1, int(len(candles) * config.in_sample_ratio)))
        descriptor = self.dataset_manager.describe(
            candles,
            dataset_name,
            source,
            {
                "in_sample": [0, split_index],
                "out_of_sample": [split_index, len(candles)],
            },
        )
        in_sample = self.runner.run(
            strategy_config,
            self.dataset_manager.slice(candles, 0, split_index),
            descriptor,
            "in_sample",
        )
        out_sample = self.runner.run(
            strategy_config,
            self.dataset_manager.slice(candles, split_index, len(candles)),
            descriptor,
            "out_of_sample",
        )
        degradation = self._degradation(in_sample.metrics.to_dict(), out_sample.metrics.to_dict())
        stability_score = round(
            clamp(
                100.0
                - abs(degradation["win_rate_degradation"]) * 100.0
                - abs(degradation["pnl_degradation"]) * 25.0
                - abs(degradation["signal_degradation"]) * 10.0
            ),
            2,
        )
        return OutOfSampleResult(
            strategy_name=strategy_config.name,
            in_sample=in_sample,
            out_of_sample=out_sample,
            degradation_metrics=degradation,
            stability_score=stability_score,
        )

    def _degradation(
        self,
        in_sample: dict[str, float | int],
        out_sample: dict[str, float | int],
    ) -> dict[str, float]:
        return {
            "win_rate_degradation": round(
                float(in_sample["win_rate"]) - float(out_sample["win_rate"]),
                4,
            ),
            "pnl_degradation": round(
                float(in_sample["net_pnl"]) - float(out_sample["net_pnl"]),
                4,
            ),
            "signal_degradation": round(
                float(in_sample["signal_count"]) - float(out_sample["signal_count"]),
                4,
            ),
            "confidence_degradation": round(
                float(in_sample["average_confidence"]) - float(out_sample["average_confidence"]),
                4,
            ),
        }
