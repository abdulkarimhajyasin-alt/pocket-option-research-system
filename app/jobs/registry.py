"""Allowlisted background job registry."""

from __future__ import annotations

from collections.abc import Callable

from app.dashboard.models import ActionDefinition
from app.jobs.models import JobResult


JobCallable = Callable[[], JobResult]


class JobRegistry:
    """Registers allowlisted dashboard job callables."""

    def __init__(self) -> None:
        self._jobs: dict[str, tuple[ActionDefinition, JobCallable]] = {}

    def register(self, definition: ActionDefinition, runner: JobCallable) -> None:
        """Register one allowlisted job."""
        if not definition.name.strip():
            raise ValueError("Job name is required")
        self._jobs[definition.name] = (definition, runner)

    def get(self, name: str) -> tuple[ActionDefinition, JobCallable]:
        """Return a registered job definition and callable."""
        if name not in self._jobs:
            raise KeyError(f"Unknown job: {name}")
        return self._jobs[name]

    def definitions(self) -> list[ActionDefinition]:
        """Return registered action definitions."""
        return [definition for definition, _ in self._jobs.values()]

    def names(self) -> list[str]:
        """Return sorted job names."""
        return sorted(self._jobs)
