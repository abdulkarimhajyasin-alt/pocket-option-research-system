"""Storage session lifecycle helpers."""

from dataclasses import dataclass
from pathlib import Path
from uuid import uuid4

from app.storage.database import Database
from app.storage.migrations import initialize_schema


@dataclass
class StorageSession:
    """Owns a database connection and logical persistence session id."""

    database: Database
    session_id: str

    @classmethod
    def create(
        cls,
        database_path: Path | str = "storage/trading_system.db",
        session_id: str | None = None,
    ) -> "StorageSession":
        """Create a connected and initialized storage session."""
        database = Database(database_path)
        connection = database.connect()
        initialize_schema(connection)
        return cls(database=database, session_id=session_id or str(uuid4()))

    def close(self) -> None:
        """Close the backing database connection."""
        self.database.close()
