# Pocket Option Research System

## Project Vision

This project is a professional experimental trading research platform. It is designed for backtesting, strategy experimentation, risk management, analytics, and demo-only execution.

This is not a gambling bot, not a production live-trading system, and does not contain real broker integration.

## Architecture Overview

The platform is organized around clean, modular boundaries:

- `app/` contains the runnable application code.
- `app/strategies/` defines strategy abstractions.
- `app/signals/` contains signal domain models.
- `app/risk/` validates signals before execution.
- `app/execution/` coordinates validated execution workflows.
- `app/brokers/` defines broker interfaces and demo adapters.
- `app/logging/` configures professional application logging.
- `tests/`, `configs/`, `logs/`, and `reports/` support validation and research operations.

Top-level domain folders are reserved for future expansion across data, indicators, strategies, signals, risk, execution, brokers, backtesting, analytics, logging, and storage.

## Phase 1 Scope

Phase 1 builds only the core foundation architecture:

- typed domain models
- abstract strategy and broker interfaces
- a risk engine skeleton
- a mock broker for simulated execution
- an execution manager
- loguru console and rotating file logging
- a minimal runnable demo flow

Out of scope for this phase:

- real broker code
- Pocket Option integration
- browser automation
- websocket logic
- AI logic
- dashboard
- database integration

## Phase 2 Scope

Phase 2 adds the market data and backtesting foundation:

- validated `Candle` and `CandleSeries` market data models
- CSV historical data loading with safe invalid-row handling
- market data normalization for timestamps, timeframe aliases, duplicates, and ordering
- a sequential candle replay backtesting engine
- binary-option style simulation with configurable payout, stake, and expiry candles
- structured backtest trades, equity points, results, and metrics
- JSON and CSV report exports into `reports/`
- a sample candle-direction strategy used only for pipeline validation

The backtesting engine reuses the same `BaseStrategy` interface used by demo execution. Strategy logic is not duplicated for backtesting.

## Setup

Use Python 3.11.

```bash
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
```

Run the demo flow:

```bash
python -m app.main
```

Run the sample backtest:

```bash
python scripts/run_backtest.py
```

## Validation

```bash
python -m compileall app
pytest
flake8 app
```

## Initial Git Commands

```bash
git init
git add .
git commit -m "Initial core architecture foundation"
```
