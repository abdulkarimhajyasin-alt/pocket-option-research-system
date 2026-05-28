"""Runtime metrics helpers."""

from dataclasses import dataclass

from app.runtime.runtime_state import RuntimeState


@dataclass(frozen=True)
class RuntimeMetricsReport:
    """Derived runtime metrics report."""

    uptime_seconds: float
    candles_per_second: float
    trades_per_hour: float
    signal_rejection_rate: float
    runtime_errors: int
    average_settlement_latency_seconds: float


class RuntimeMetricsCalculator:
    """Calculates runtime metrics from state and settlement latencies."""

    def calculate(
        self,
        state: RuntimeState,
        settlement_latencies: list[float] | None = None,
    ) -> RuntimeMetricsReport:
        """Calculate a structured runtime metrics report."""
        settlement_latencies = settlement_latencies or []
        uptime = state.uptime_seconds
        metrics = state.metrics
        total_signals = metrics.generated_signals
        return RuntimeMetricsReport(
            uptime_seconds=round(uptime, 4),
            candles_per_second=round(metrics.processed_candles / uptime, 4) if uptime else 0.0,
            trades_per_hour=round(metrics.executed_trades / (uptime / 3600), 4) if uptime else 0.0,
            signal_rejection_rate=round(metrics.blocked_trades / total_signals, 4)
            if total_signals
            else 0.0,
            runtime_errors=metrics.runtime_errors,
            average_settlement_latency_seconds=round(
                sum(settlement_latencies) / len(settlement_latencies),
                4,
            )
            if settlement_latencies
            else 0.0,
        )
