"""Overfitting detection diagnostics."""

from __future__ import annotations

from app.validation.models import (
    OutOfSampleResult,
    OverfittingWarning,
    ParameterSweepSummary,
    WalkForwardResult,
    WarningSeverity,
)
from app.validation.statistics import coefficient_of_variation


class OverfittingDetector:
    """Detects common research overfitting indicators."""

    def detect(
        self,
        walk_forward: WalkForwardResult | None = None,
        out_of_sample: OutOfSampleResult | None = None,
        sweep: ParameterSweepSummary | None = None,
    ) -> list[OverfittingWarning]:
        """Return explainable overfitting warnings."""
        warnings: list[OverfittingWarning] = []
        if out_of_sample is not None:
            warnings.extend(self._out_of_sample_warnings(out_of_sample))
        if walk_forward is not None:
            warnings.extend(self._walk_forward_warnings(walk_forward))
        if sweep is not None:
            warnings.extend(self._sweep_warnings(sweep))
        return warnings

    def _out_of_sample_warnings(
        self,
        result: OutOfSampleResult,
    ) -> list[OverfittingWarning]:
        warnings: list[OverfittingWarning] = []
        win_drop = result.degradation_metrics.get("win_rate_degradation", 0.0)
        pnl_drop = result.degradation_metrics.get("pnl_degradation", 0.0)
        if win_drop > 0.25:
            warnings.append(
                OverfittingWarning(
                    "train_test_win_rate_divergence",
                    WarningSeverity.HIGH,
                    "Out-of-sample win rate is materially below in-sample win rate.",
                    {"win_rate_degradation": win_drop},
                )
            )
        if pnl_drop > 5.0:
            warnings.append(
                OverfittingWarning(
                    "train_test_pnl_divergence",
                    WarningSeverity.MEDIUM,
                    "Out-of-sample net PnL degraded sharply versus in-sample results.",
                    {"pnl_degradation": pnl_drop},
                )
            )
        return warnings

    def _walk_forward_warnings(
        self,
        result: WalkForwardResult,
    ) -> list[OverfittingWarning]:
        warnings: list[OverfittingWarning] = []
        pnl_variation = float(result.stability_metrics.get("pnl_variation", 0.0))
        signal_variation = float(result.stability_metrics.get("signal_count_variation", 0.0))
        if pnl_variation > 1.25:
            warnings.append(
                OverfittingWarning(
                    "unstable_window_pnl",
                    WarningSeverity.HIGH,
                    "Walk-forward windows show high PnL variation.",
                    {"pnl_variation": pnl_variation},
                )
            )
        if signal_variation > 0.75:
            warnings.append(
                OverfittingWarning(
                    "unstable_signal_generation",
                    WarningSeverity.MEDIUM,
                    "Signal counts vary heavily across validation windows.",
                    {"signal_count_variation": signal_variation},
                )
            )
        return warnings

    def _sweep_warnings(
        self,
        summary: ParameterSweepSummary,
    ) -> list[OverfittingWarning]:
        if not summary.results:
            return []
        pnl_variation = coefficient_of_variation(
            [item.result.metrics.net_pnl for item in summary.results]
        )
        signal_variation = coefficient_of_variation(
            [float(item.result.metrics.signal_count) for item in summary.results]
        )
        warnings: list[OverfittingWarning] = []
        if pnl_variation > 1.5:
            warnings.append(
                OverfittingWarning(
                    "excessive_parameter_sensitivity",
                    WarningSeverity.HIGH,
                    "Small parameter changes produce highly divergent PnL.",
                    {"pnl_variation": round(pnl_variation, 4)},
                )
            )
        if signal_variation > 1.0:
            warnings.append(
                OverfittingWarning(
                    "parameter_sensitive_signal_count",
                    WarningSeverity.MEDIUM,
                    "Signal frequency is highly parameter-sensitive.",
                    {"signal_count_variation": round(signal_variation, 4)},
                )
            )
        return warnings
