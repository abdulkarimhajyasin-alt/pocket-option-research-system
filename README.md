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

## Phase 9 Scope

Phase 9 adds configuration, orchestration, and environment management:

- centralized layered configuration loading and resolution
- environment profiles for local, research, paper, and debug modes
- environment variable overrides using nested `TRADING_...` keys
- lightweight service container and dependency graph diagnostics
- startup checks for configs, directories, database access, broker safety, strategies, and operational mode
- runtime composition and orchestrator-driven startup
- diagnostics exports under `reports/diagnostics/`
- dedicated rotating `logs/orchestrator.log`
- environment diagnostics runner at `scripts/check_environment.py`

The orchestration layer manages composition only. Strategies still generate signals, risk keeps final approval authority, storage remains infrastructure, and brokers remain isolated adapters.

## Phase 10 Scope

Phase 10 adds a controlled demo connectivity research layer:

- read-only connector contracts under `app/connectivity/`
- connector capabilities, health snapshots, registry, and error hierarchy
- local CSV market-data connector that wraps the existing CSV loader
- simulated external market connector with local-only latency and heartbeat behavior
- ingestion validation for ordering, gaps, OHLC structure, freshness, and timeframe consistency
- connectivity runtime for safe connector lifecycle, heartbeat, fetch, validation, and shutdown
- read-only connector configs under `configs/connectivity/`
- orchestration integration through service registration, startup checks, and diagnostics
- dedicated rotating `logs/connectivity.log`
- diagnostics runner at `scripts/check_connectivity.py`

All connectors are read-only. They expose no trade execution capability, no credential handling, no browser automation, and no external broker communication.

## Phase 11 Scope

Phase 11 adds market stream processing and real-time data pipeline foundations:

- read-only stream models for ticks, candle updates, batches, state, and metrics
- broker-agnostic `BaseMarketStream` lifecycle and subscription interface
- deterministic local `SimulatedMarketStream` for EURUSD M1/M5 research
- CSV replay stream that emits historical candles as sequential stream events
- tick-to-candle aggregation for M1/M5 with late tick and gap tracking
- rolling stream buffers, validation, health monitoring, and stream diagnostics
- optional streaming runtime adapter that feeds closed candles into the existing Strategy → Risk → paper/demo-safe execution path
- streaming configs under `configs/streaming/`
- diagnostics runner at `scripts/check_streaming.py`
- dedicated rotating `logs/streaming.log`

Streaming does not add live trading, Pocket Option execution, broker automation, websocket reverse engineering, credential handling, AI models, or dashboard UI. Tick persistence is disabled by default; persistence hooks record stream lifecycle, health, validation failures, and replay metadata unless explicitly configured otherwise.

This phase prepares future demo market-data integration while keeping external data flow read-only and local-first.

## Phase 13 Scope

Phase 13 adds the first serious strategy-development research layer:

- reusable strategy research models for market context, evidence, decisions, and rejections
- explainable evidence scoring with separate bullish and bearish confidence paths
- research filters for ATR thresholds, sessions, candle body strength, low range, and wick risk
- price-action utilities for swing structure, fair value gaps, liquidity sweeps, and CISD-like displacement
- `research_cisd_fvg_strategy`, a configurable research candidate that only generates `TradeSignal` objects
- strategy research analytics under `reports/strategy_research/`
- persistence hooks for compact decision, evidence, and metadata events
- dedicated rotating `logs/strategy_research.log`

The research CISD/FVG strategy is a candidate for experimentation, not a profitable system guarantee. It does not execute trades, place Pocket Option orders, automate browsers, handle credentials, or bypass the Risk Engine. Risk approval remains the final authority in backtests and runtime flows.

Run the strategy research backtest:

```bash
python scripts/run_strategy_research.py
```

Inspect generated strategy research reports:

```text
reports/strategy_research/
```

## Phase 14 Scope

Phase 14 adds strategy validation and research-quality tooling:

- walk-forward validation with rolling and expanding train/validation/test windows
- out-of-sample evaluation with separate in-sample and out-of-sample metrics
- parameter sensitivity sweeps for configurable research parameters
- explainable robustness scoring from consistency, stability, sensitivity, and signal reliability
- overfitting diagnostics for train/test divergence, window instability, and parameter sensitivity
- research comparison helpers that do not rank solely by profitability
- dataset descriptors so reports identify data source, time range, symbol, timeframe, and sample count
- reproducible JSON, CSV, and text reports under `reports/validation/`
- persistence hooks for validation runs, walk-forward results, sweeps, robustness, overfitting diagnostics, and dataset metadata
- dedicated rotating `logs/strategy_validation.log`

This layer evaluates whether a strategy looks robust enough for further research. It does not execute trades, connect to live brokers, automate Pocket Option, add real-money functionality, or bypass risk controls.

Run the full validation workflow:

```bash
python scripts/run_validation.py
```

Run focused research-quality tools:

```bash
python scripts/run_walk_forward.py
python scripts/run_parameter_sweep.py
python scripts/run_research_report.py
python scripts/check_research_quality.py
```

## Phase 15 Scope

Phase 15 adds a research-grade dataset management and data-quality layer:

- centralized dataset registry with deterministic IDs, metadata, checksums, versions, and tags
- immutable dataset version records and version comparison helpers
- quality scoring for empty data, missing intervals, duplicates, timestamp ordering, OHLC validity, zero-volume anomalies, and timeframe consistency
- gap detection with expected, suspicious, and severe classifications
- checksum and fingerprint-based integrity verification
- dataset normalization for timestamps, symbols, timeframes, and common OHLCV column aliases
- dataset statistics for row count, date range, candle size, volatility, gaps, duplicates, and quality score
- deterministic synthetic datasets for trending, ranging, volatile, low-volatility, and noisy market profiles
- dataset comparison reports that rank by quality, coverage, gaps, duplicates, and volatility
- validation quality gates so Phase 14 validation reports include dataset ID, version, checksum, quality, integrity, and statistics
- dataset reports under `reports/datasets/` and dedicated `logs/dataset_quality.log`

This layer validates data before research usage. It does not execute trades, connect to live brokers, automate Pocket Option, alter risk controls, or add real-money functionality.

Run dataset diagnostics:

```bash
python scripts/check_dataset_quality.py
python scripts/generate_synthetic_dataset.py
python scripts/run_dataset_statistics.py
python scripts/run_dataset_comparison.py
python scripts/verify_dataset_integrity.py
python scripts/check_data_layer.py
```

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

Run environment diagnostics:

```bash
python scripts/check_environment.py
```

Run connectivity diagnostics:

```bash
python scripts/check_connectivity.py
```

Run streaming diagnostics:

```bash
python scripts/check_streaming.py
```

Run strategy research diagnostics:

```bash
python scripts/run_strategy_research.py
```

Run strategy validation diagnostics:

```bash
python scripts/check_research_quality.py
```

Run dataset quality diagnostics:

```bash
python scripts/check_data_layer.py
```

## Local Research Dashboard

Phase 16 adds a local FastAPI dashboard for browsing research state from a browser.
Phase 17 upgrades it into an Arabic-first research visualization and analytics workbench.
It is local-only and does not execute live trades, connect to real-money accounts, or automate
broker actions.

Start the dashboard:

```bash
python scripts/run_dashboard.py
```

Open:

```text
http://localhost:8000
```

Run non-blocking dashboard diagnostics:

```bash
python scripts/check_visualization_layer.py
python scripts/check_dashboard.py
python scripts/run_dashboard.py --check
```

## Phase 41 Market Observation Pipeline

Phase 41 adds the canonical research-only Market Observation pipeline. It normalizes
passive local outputs from observation, market-data, browser-observation artifacts,
external-observation artifacts, manual snapshot imports, broker-readiness reports, and
observation-intelligence reports into one unified market observation source.

Outputs are written under:

- `storage/market_observation/`
- `reports/market_observation/`

Run the pipeline and diagnostics:

```bash
python scripts/run_market_observation.py
python scripts/check_market_observation.py
```

The pipeline does not add broker access, browser automation, login, execution, order
placement, credential handling, or trading automation. It only reads existing local
research artifacts and produces dashboard/report data.

## Phase 42 Live Observation Replay Engine

Phase 42 adds a deterministic Live Observation Replay Engine for research-only
observation flow simulation. It replays historical, imported, unified, browser,
external, and observation-intelligence outputs as if they were arriving in sequence.

Outputs are written under:

- `storage/live_observation/`
- `reports/live_observation/`

Run the replay engine and diagnostics:

```bash
python scripts/run_live_observation.py
python scripts/check_live_observation.py
```

The replay engine simulates observation timing only. It does not add broker access,
browser automation, login, authentication, credential handling, order placement,
execution, money management, position management, or trading automation.

## Phase 43 Signal Stream Engine

Phase 43 adds a research-only Signal Stream Engine that consumes live observation
replay outputs, market observation reports, observation intelligence reports, and
signal intelligence reports to generate continuous signal events.

Outputs are written under:

- `storage/signal_stream/`
- `reports/signal_stream/`

Run the signal stream engine and diagnostics:

```bash
python scripts/run_signal_stream.py
python scripts/check_signal_stream.py
```

Signal directions are research classifications only: `CALL`, `PUT`, and `NO_TRADE`.
The engine does not add broker access, browser automation, login, authentication,
credential handling, order placement, execution, money management, position
management, or trading automation.

Dashboard pages:

- Overview
- Strategies
- Datasets
- Validation
- Signals
- Reports
- Run Center

The Run Center executes only fixed allowlisted research scripts. It does not accept arbitrary
shell input.

Phase 17 visualization features:

- Arabic-first RTL dashboard shell with translation dictionaries under `app/i18n/`
- executive research health cards and workflow state tracking
- equity, balance, cumulative performance, and drawdown charts from analytics reports
- signal analytics at `/signals`
- validation and dataset charts on their explorer pages
- recent activity timeline and deterministic research insights
- local-only dashboard APIs at `/api/dashboard`, `/api/metrics`, `/api/validation`,
  `/api/datasets`, and `/api/signals`

## Validation

```bash
python -m compileall app
pytest
flake8 app
python scripts/check_visualization_layer.py
python scripts/check_dashboard.py
python scripts/run_dashboard.py --check
python scripts/check_dataset_quality.py
python scripts/generate_synthetic_dataset.py
python scripts/run_dataset_statistics.py
python scripts/run_dataset_comparison.py
python scripts/verify_dataset_integrity.py
python scripts/check_data_layer.py
python scripts/run_strategy_research.py
python scripts/run_validation.py
python scripts/run_walk_forward.py
python scripts/run_parameter_sweep.py
python scripts/run_research_report.py
python scripts/check_research_quality.py
python scripts/check_streaming.py
```

## Initial Git Commands

```bash
git init
git add .
git commit -m "Initial core architecture foundation"
```
