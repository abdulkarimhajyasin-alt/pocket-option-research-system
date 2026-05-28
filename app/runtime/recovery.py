"""Runtime recovery helpers built on persisted snapshots."""

from dataclasses import dataclass

from loguru import logger

from app.storage.snapshots import RuntimeSnapshot, SnapshotManager


@dataclass(frozen=True)
class RecoveryResult:
    """Result of a recovery attempt."""

    recovered: bool
    session_id: str
    snapshot: RuntimeSnapshot | None
    message: str


class RecoveryManager:
    """Restores runtime-adjacent state from persisted snapshots."""

    def __init__(self, snapshot_manager: SnapshotManager) -> None:
        self.snapshot_manager = snapshot_manager

    def recover(self, session_id: str) -> RecoveryResult:
        """Recover the latest snapshot for a session."""
        snapshot = self.snapshot_manager.restore_latest(session_id)
        if snapshot is None:
            logger.bind(component="storage").warning(
                "No recovery snapshot found session={}",
                session_id,
            )
            return RecoveryResult(False, session_id, None, "no_snapshot")
        logger.bind(component="storage").info("Runtime recovery completed session={}", session_id)
        return RecoveryResult(True, session_id, snapshot, "recovered")
