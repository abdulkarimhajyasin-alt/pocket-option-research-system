"""Threaded background job manager for local dashboard actions."""

from __future__ import annotations

from concurrent.futures import ThreadPoolExecutor
from threading import Lock
from uuid import uuid4

from app.jobs.models import JobRecord, JobResult, JobStatus, utc_now
from app.jobs.registry import JobRegistry


class JobManager:
    """Queue, track, and observe local research jobs."""

    def __init__(self, registry: JobRegistry, max_workers: int = 2) -> None:
        self.registry = registry
        self._executor = ThreadPoolExecutor(
            max_workers=max_workers,
            thread_name_prefix="dashboard-job",
        )
        self._jobs: dict[str, JobRecord] = {}
        self._lock = Lock()

    def enqueue(self, name: str) -> JobRecord:
        """Queue a registered job and return its record."""
        definition, runner = self.registry.get(name)
        record = JobRecord(
            run_id=str(uuid4()),
            name=definition.name,
            label=definition.label,
            status=JobStatus.QUEUED,
            queued_at=utc_now(),
        )
        with self._lock:
            self._jobs[record.run_id] = record
        self._executor.submit(self._run, record.run_id, runner)
        return record

    def list_jobs(self) -> list[JobRecord]:
        """Return jobs sorted newest first."""
        with self._lock:
            return sorted(self._jobs.values(), key=lambda item: item.queued_at, reverse=True)

    def get(self, run_id: str) -> JobRecord | None:
        """Return one job by run id."""
        with self._lock:
            return self._jobs.get(run_id)

    def active_count(self) -> int:
        """Return count of queued or running jobs."""
        with self._lock:
            return sum(
                1
                for job in self._jobs.values()
                if job.status in {JobStatus.QUEUED, JobStatus.RUNNING}
            )

    def diagnostics(self) -> dict[str, int]:
        """Return job status counts."""
        jobs = self.list_jobs()
        return {
            "active_jobs": self.active_count(),
            "queued_jobs": sum(1 for job in jobs if job.status == JobStatus.QUEUED),
            "running_jobs": sum(1 for job in jobs if job.status == JobStatus.RUNNING),
            "completed_jobs": sum(1 for job in jobs if job.status == JobStatus.COMPLETED),
            "failed_jobs": sum(1 for job in jobs if job.status == JobStatus.FAILED),
        }

    def shutdown(self) -> None:
        """Stop accepting new job work."""
        self._executor.shutdown(wait=False, cancel_futures=False)

    def _run(self, run_id: str, runner: object) -> None:
        with self._lock:
            record = self._jobs[run_id]
            record.status = JobStatus.RUNNING
            record.started_at = utc_now()
        try:
            result = runner()
            status = JobStatus.COMPLETED if result.exit_code == 0 else JobStatus.FAILED
        except Exception as exc:
            result = JobResult(exit_code=1, error=str(exc), stderr=str(exc))
            status = JobStatus.FAILED
        with self._lock:
            record = self._jobs[run_id]
            record.status = status
            record.completed_at = utc_now()
            record.result = result
