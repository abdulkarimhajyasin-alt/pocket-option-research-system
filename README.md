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
- `app/analytics/` builds research journals, equity curves, exports, and snapshots.
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

## Phase 3 Scope

Phase 3 adds professional strategy infrastructure:

- reusable indicator architecture for SMA, EMA, RSI, and ATR
- indicator and strategy registries for dynamic loading
- strategy metadata, lifecycle hooks, parameters, session restrictions, and confidence thresholds
- YAML-backed strategy configuration
- UTC-aware London, New York, and Asian session filtering
- weighted confidence scoring helpers
- reusable candle pattern detection
- timeframe conversion and comparison helpers
- an architecture-first CISD/FVG strategy skeleton

Strategies remain isolated signal generators. They do not execute trades or call brokers.

## Phase 4 Scope

Phase 4 hardens the Risk Engine into the platform safety core:

- structured risk validation responses and rejection reasons
- isolated daily state tracking and UTC-safe resets
- reusable risk rules for trade limits, loss limits, confidence, sessions, symbols, and timeframes
- cooldown controls after losses and loss streaks
- exposure tracking by active trade, symbol, strategy, and direction
- YAML risk profiles under `configs/risk/`
- risk-aware backtesting with blocked trade tracking and rejection summaries
- dedicated rotating `logs/risk_events.log`

The Risk Engine has final approval authority. Strategies only generate signals.

## Phase 5 Scope

Phase 5 adds a local execution runtime and paper trading system:

- runtime lifecycle manager, event loop, health monitor, shutdown manager, and kill switch
- runtime state and metrics tracking
- local `PaperBroker` with simulated balance, positions, and binary-option settlements
- queue-based execution manager with trade lifecycle states
- position tracking for open and closed paper trades
- runtime YAML configs under `configs/runtime/`
- local runner at `scripts/run_runtime.py`
- rotating `logs/runtime.log`

The runtime remains broker-agnostic and risk-first. It performs no real broker communication.

## Phase 6 Scope

Phase 6 adds analytics and research infrastructure:

- append-only trade journaling shared by backtesting and paper runtime
- equity curve tracking with drawdown, peaks, troughs, and cumulative PnL
- strategy, symbol, session, hourly, streak, rejection, and exposure analytics
- runtime analytics snapshots for throughput, blocked signals, errors, and latency placeholders
- JSON and CSV analytics exports under `reports/analytics/`
- normalized research dataset generation for future ML and optimization work
- dedicated rotating `logs/analytics.log`

Analytics remains decoupled from execution decisions. It observes lifecycle events and exports structured research artifacts.

## Phase 7 Scope

Phase 7 adds broker adapter architecture and demo integration planning:

- typed broker capabilities, health snapshots, runtime status, and error hierarchy
- upgraded `BaseBroker` contract for lifecycle, health, environment validation, and support lookup
- dynamic broker registry for future plugin-style adapter loading
- `DemoBrokerAdapter` that wraps local paper trading while simulating adapter lifecycle and latency
- broker runtime coordinator for initialization, heartbeat, diagnostics, and safe shutdown
- broker YAML configs under `configs/brokers/`
- explicit demo-only enforcement that rejects live mode and live-capable adapters
- dedicated rotating `logs/broker.log`
- diagnostics runner at `scripts/check_broker_runtime.py`

Broker adapters remain isolated from strategies, risk, analytics, and runtime internals. No external broker communication is implemented.

## Phase 8 Scope

Phase 8 adds persistence, storage, and replay infrastructure:

- local SQLite storage under `storage/trading_system.db`
- schema initialization and migration helpers
- repository-based persistence for trades, signals, runtime events, risk events, analytics snapshots, broker health, and execution lifecycle events
- append-only event storage with replay support
- runtime snapshot creation and recovery helpers
- optional persistence integration for paper runtime and backtesting flows
- storage diagnostics runner at `scripts/check_storage.py`
- dedicated rotating `logs/storage.log`

Storage remains infrastructure only. It is decoupled from strategy logic, broker adapters, and analytics calculations, while preparing the platform for future PostgreSQL-compatible persistence.

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

Run the local paper runtime:

```bash
python scripts/run_runtime.py
```

Run broker diagnostics:

```bash
python scripts/check_broker_runtime.py
```

Run storage diagnostics:

```bash
python scripts/check_storage.py
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
