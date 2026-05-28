"""Backtest report export utilities."""

import csv
import json
from dataclasses import asdict
from datetime import datetime
from pathlib import Path
from typing import Any

from loguru import logger

from app.backtesting.models import BacktestResult, BacktestTrade, EquityPoint


class BacktestReportBuilder:
    """Exports backtest results to JSON and CSV files."""

    def __init__(self, reports_dir: Path | str = "reports") -> None:
        self.reports_dir = Path(reports_dir)
        self.reports_dir.mkdir(parents=True, exist_ok=True)

    def export(self, result: BacktestResult, run_name: str | None = None) -> dict[str, Path]:
        """Export a JSON summary report and CSV trade list."""
        safe_name = run_name or f"{result.strategy_name}_{result.symbol}_{result.timeframe}"
        json_path = self.reports_dir / f"{safe_name}_report.json"
        csv_path = self.reports_dir / f"{safe_name}_trades.csv"

        self.export_json(result, json_path)
        self.export_trades_csv(result.trades, csv_path)
        logger.info("Backtest reports exported to {}", self.reports_dir)
        return {"json": json_path, "csv": csv_path}

    def export_json(self, result: BacktestResult, path: Path) -> None:
        """Export a structured JSON backtest report."""
        payload = {
            "summary": result.summary(),
            "metrics": result.metrics,
            "trades": [self._serialize_trade(trade) for trade in result.trades],
            "equity_curve": [self._serialize_equity(point) for point in result.equity_curve],
        }
        path.write_text(json.dumps(payload, indent=2), encoding="utf-8")
        logger.info("JSON backtest report exported: {}", path)

    def export_trades_csv(self, trades: list[BacktestTrade], path: Path) -> None:
        """Export simulated trades to CSV."""
        fieldnames = list(asdict(trades[0]).keys()) if trades else self._empty_trade_fields()
        with path.open("w", encoding="utf-8", newline="") as file:
            writer = csv.DictWriter(file, fieldnames=fieldnames)
            writer.writeheader()
            for trade in trades:
                writer.writerow(self._serialize_trade(trade))
        logger.info("CSV trade export written: {}", path)

    def _serialize_trade(self, trade: BacktestTrade) -> dict[str, Any]:
        row = asdict(trade)
        row["outcome"] = trade.outcome.value
        row["entry_timestamp"] = self._serialize_datetime(trade.entry_timestamp)
        row["exit_timestamp"] = self._serialize_datetime(trade.exit_timestamp)
        return row

    def _serialize_equity(self, point: EquityPoint) -> dict[str, Any]:
        row = asdict(point)
        row["timestamp"] = self._serialize_datetime(point.timestamp)
        return row

    def _serialize_datetime(self, value: datetime | None) -> str | None:
        return value.isoformat() if value is not None else None

    def _empty_trade_fields(self) -> list[str]:
        return [
            "symbol",
            "timeframe",
            "direction",
            "strategy_name",
            "confidence",
            "entry_timestamp",
            "entry_price",
            "exit_timestamp",
            "exit_price",
            "outcome",
            "pnl",
            "reason",
        ]
