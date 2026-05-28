"""Runtime analytics derived from runtime state and latency samples."""

from app.analytics.models import RuntimePerformance
from app.runtime.runtime_state import RuntimeState


class RuntimeAnalytics:
    """Builds runtime performance summaries without controlling execution."""

    def analyze(
        self,
        state: RuntimeState,
        settlement_latencies: list[float] | None = None,
        processing_latencies: list[float] | None = None,
    ) -> RuntimePerformance:
        """Return a runtime performance snapshot."""
        uptime_hours = state.uptime_seconds / 3600 if state.uptime_seconds else 0.0
        settlement_latencies = settlement_latencies or []
        processing_latencies = processing_latencies or []
        return RuntimePerformance(
            uptime_seconds=round(state.uptime_seconds, 4),
            execution_throughput=round(
                state.metrics.executed_trades / uptime_hours,
                4,
            )
            if uptime_hours
            else 0.0,
            signals_per_hour=round(state.metrics.generated_signals / uptime_hours, 4)
            if uptime_hours
            else 0.0,
            runtime_errors=state.metrics.runtime_errors,
            blocked_signals=state.metrics.blocked_trades,
            settlement_latency=round(
                sum(settlement_latencies) / len(settlement_latencies),
                4,
            )
            if settlement_latencies
            else 0.0,
            processing_latency=round(
                sum(processing_latencies) / len(processing_latencies),
                4,
            )
            if processing_latencies
            else 0.0,
        )
