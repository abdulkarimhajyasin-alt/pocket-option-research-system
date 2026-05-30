"""Report generation for offline execution simulations."""

from __future__ import annotations

import csv
import json
from pathlib import Path
from typing import Any

from app.execution_simulator.models import SimulatedTrade


class ExecutionSimulationReporter:
    """Write execution simulation reports under reports/execution."""

    def __init__(self, output_dir: Path | str = "reports/execution") -> None:
        self.output_dir = Path(output_dir)

    def export(
        self,
        trades: list[SimulatedTrade],
        analytics: dict[str, Any],
        run_name: str = "execution_simulation",
    ) -> dict[str, str]:
        """Export summary JSON, trades CSV, and analytics JSON."""
        self.output_dir.mkdir(parents=True, exist_ok=True)
        summary_path = self.output_dir / f"{run_name}_summary.json"
        trades_path = self.output_dir / f"{run_name}_trades.csv"
        analytics_path = self.output_dir / f"{run_name}_analytics.json"
        summary = {
            "run_name": run_name,
            "research_only": True,
            "simulation_only": True,
            "total_trades": analytics.get("total_trades", 0),
            "executed_trades": analytics.get("executed_trades", 0),
            "blocked_trades": analytics.get("blocked_trades", 0),
            "win_rate": analytics.get("win_rate", 0.0),
            "profit_loss": analytics.get("profit_loss", 0.0),
        }
        summary_path.write_text(
            json.dumps(summary, indent=2, ensure_ascii=False),
            encoding="utf-8",
        )
        analytics_path.write_text(
            json.dumps(analytics, indent=2, ensure_ascii=False),
            encoding="utf-8",
        )
        self._write_trades(trades_path, trades)
        return {
            "summary": str(summary_path),
            "trades": str(trades_path),
            "analytics": str(analytics_path),
        }

    def _write_trades(self, path: Path, trades: list[SimulatedTrade]) -> None:
        fields = [
            "trade_id",
            "order_id",
            "symbol",
            "timeframe",
            "direction",
            "strategy_name",
            "confidence",
            "entry_time",
            "expiry_time",
            "entry_price",
            "expiry_price",
            "outcome",
            "payout",
            "profit_loss",
            "expected_return",
            "actual_return",
            "blocked_reason",
        ]
        with path.open("w", encoding="utf-8", newline="") as handle:
            writer = csv.DictWriter(handle, fieldnames=fields)
            writer.writeheader()
            for trade in trades:
                writer.writerow(trade.to_dict())
