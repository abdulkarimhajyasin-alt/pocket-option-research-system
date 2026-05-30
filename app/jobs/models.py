"""Dashboard background job models."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import UTC, datetime
from enum import StrEnum
from typing import Any


class JobStatus(StrEnum):
    """Observable job lifecycle states."""

    QUEUED = "queued"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"


@dataclass(frozen=True)
class JobResult:
    """Captured result for one completed job."""

    exit_code: int
    stdout: str = ""
    stderr: str = ""
    error: str | None = None

    def to_dict(self) -> dict[str, Any]:
        """Return a JSON-safe result."""
        return {
            "exit_code": self.exit_code,
            "stdout": self.stdout,
            "stderr": self.stderr,
            "error": self.error,
        }


@dataclass
class JobRecord:
    """Stateful dashboard background job record."""

    run_id: str
    name: str
    label: str
    status: JobStatus
    queued_at: datetime
    started_at: datetime | None = None
    completed_at: datetime | None = None
    result: JobResult | None = None

    def to_dict(self) -> dict[str, Any]:
        """Return a JSON-safe job record."""
        return {
            "run_id": self.run_id,
            "name": self.name,
            "label": self.label,
            "status": self.status.value,
            "status_label": self.status_label,
            "queued_at": self.queued_at.isoformat(),
            "started_at": self.started_at.isoformat() if self.started_at else None,
            "completed_at": self.completed_at.isoformat() if self.completed_at else None,
            "result": self.result.to_dict() if self.result else None,
        }

    @property
    def status_label(self) -> str:
        """Return Arabic status label."""
        labels = {
            JobStatus.QUEUED: "قيد الانتظار",
            JobStatus.RUNNING: "قيد التنفيذ",
            JobStatus.COMPLETED: "مكتمل",
            JobStatus.FAILED: "فشل",
        }
        return labels[self.status]


def utc_now() -> datetime:
    """Return a timezone-aware UTC timestamp."""
    return datetime.now(UTC)
