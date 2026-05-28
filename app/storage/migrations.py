"""SQLite schema initialization and migrations."""

from sqlite3 import Connection

from loguru import logger


SCHEMA_STATEMENTS = [
    """
    CREATE TABLE IF NOT EXISTS events (
        event_id TEXT PRIMARY KEY,
        session_id TEXT NOT NULL,
        event_type TEXT NOT NULL,
        aggregate_id TEXT NOT NULL,
        timestamp TEXT NOT NULL,
        payload TEXT NOT NULL
    )
    """,
    """
    CREATE TABLE IF NOT EXISTS trades (
        trade_id TEXT NOT NULL,
        session_id TEXT NOT NULL,
        strategy_name TEXT NOT NULL,
        symbol TEXT NOT NULL,
        timeframe TEXT NOT NULL,
        direction TEXT NOT NULL,
        lifecycle_state TEXT NOT NULL,
        timestamp TEXT NOT NULL,
        confidence REAL NOT NULL,
        pnl REAL NOT NULL,
        outcome TEXT,
        rejection_reason TEXT,
        PRIMARY KEY (trade_id, lifecycle_state, timestamp)
    )
    """,
    """
    CREATE TABLE IF NOT EXISTS signals (
        signal_id TEXT PRIMARY KEY,
        session_id TEXT NOT NULL,
        strategy_name TEXT NOT NULL,
        symbol TEXT NOT NULL,
        timeframe TEXT NOT NULL,
        direction TEXT NOT NULL,
        confidence REAL NOT NULL,
        timestamp TEXT NOT NULL
    )
    """,
    """
    CREATE TABLE IF NOT EXISTS runtime_events (
        event_id TEXT PRIMARY KEY,
        session_id TEXT NOT NULL,
        event_type TEXT NOT NULL,
        timestamp TEXT NOT NULL,
        message TEXT NOT NULL,
        payload TEXT NOT NULL
    )
    """,
    """
    CREATE TABLE IF NOT EXISTS risk_events (
        event_id TEXT PRIMARY KEY,
        session_id TEXT NOT NULL,
        timestamp TEXT NOT NULL,
        strategy_name TEXT NOT NULL,
        symbol TEXT NOT NULL,
        timeframe TEXT NOT NULL,
        approved INTEGER NOT NULL,
        reason TEXT,
        message TEXT NOT NULL,
        state_snapshot TEXT NOT NULL
    )
    """,
    """
    CREATE TABLE IF NOT EXISTS analytics_snapshots (
        snapshot_id TEXT PRIMARY KEY,
        session_id TEXT NOT NULL,
        timestamp TEXT NOT NULL,
        snapshot_type TEXT NOT NULL,
        payload TEXT NOT NULL
    )
    """,
    """
    CREATE TABLE IF NOT EXISTS runtime_states (
        state_id TEXT PRIMARY KEY,
        session_id TEXT NOT NULL,
        timestamp TEXT NOT NULL,
        mode TEXT NOT NULL,
        active INTEGER NOT NULL,
        health TEXT NOT NULL,
        payload TEXT NOT NULL
    )
    """,
    """
    CREATE TABLE IF NOT EXISTS broker_health_events (
        event_id TEXT PRIMARY KEY,
        session_id TEXT NOT NULL,
        timestamp TEXT NOT NULL,
        broker_name TEXT NOT NULL,
        status TEXT NOT NULL,
        connected INTEGER NOT NULL,
        payload TEXT NOT NULL
    )
    """,
    """
    CREATE TABLE IF NOT EXISTS execution_events (
        event_id TEXT PRIMARY KEY,
        session_id TEXT NOT NULL,
        timestamp TEXT NOT NULL,
        trade_id TEXT NOT NULL,
        lifecycle_state TEXT NOT NULL,
        payload TEXT NOT NULL
    )
    """,
]


def initialize_schema(connection: Connection) -> None:
    """Create all storage tables if they do not exist."""
    logger.bind(component="storage").info("Initializing database schema")
    with connection:
        for statement in SCHEMA_STATEMENTS:
            connection.execute(statement)
    logger.bind(component="storage").info("Database schema ready")


def list_tables(connection: Connection) -> list[str]:
    """Return user-created SQLite table names."""
    rows = connection.execute(
        "SELECT name FROM sqlite_master WHERE type='table' ORDER BY name"
    ).fetchall()
    return [str(row["name"]) for row in rows]
