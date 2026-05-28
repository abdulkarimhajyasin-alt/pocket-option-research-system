"""SQLite database connection and lifecycle management."""

import sqlite3
from pathlib import Path
from types import TracebackType

from loguru import logger


class Database:
    """Manages local SQLite connections with transaction-safe helpers."""

    def __init__(self, path: Path | str = "storage/trading_system.db") -> None:
        self.path = Path(path)
        self.connection: sqlite3.Connection | None = None

    def connect(self) -> sqlite3.Connection:
        """Open a SQLite connection."""
        self.path.parent.mkdir(parents=True, exist_ok=True)
        self.connection = sqlite3.connect(self.path)
        self.connection.row_factory = sqlite3.Row
        self.connection.execute("PRAGMA foreign_keys = ON")
        logger.bind(component="storage").info("Database connected path={}", self.path)
        return self.connection

    def get_connection(self) -> sqlite3.Connection:
        """Return an open connection, opening it when needed."""
        if self.connection is None:
            return self.connect()
        return self.connection

    def close(self) -> None:
        """Close the SQLite connection safely."""
        if self.connection is None:
            return
        self.connection.close()
        self.connection = None
        logger.bind(component="storage").info("Database connection closed")

    def __enter__(self) -> "Database":
        self.connect()
        return self

    def __exit__(
        self,
        exc_type: type[BaseException] | None,
        exc: BaseException | None,
        traceback: TracebackType | None,
    ) -> None:
        self.close()
