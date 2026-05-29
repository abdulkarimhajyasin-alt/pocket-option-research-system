"""Safe allowlisted research actions for the dashboard."""

from __future__ import annotations

import subprocess
import sys
from pathlib import Path

from loguru import logger

from app.dashboard.models import ActionDefinition, ActionResult


ACTION_DEFINITIONS: dict[str, ActionDefinition] = {
    "strategy_research": ActionDefinition(
        name="strategy_research",
        label="Strategy research run",
        description="Run the explainable research strategy workflow.",
        command=("scripts/run_strategy_research.py",),
    ),
    "validation": ActionDefinition(
        name="validation",
        label="Validation run",
        description="Run the complete validation workflow.",
        command=("scripts/run_validation.py",),
    ),
    "walk_forward": ActionDefinition(
        name="walk_forward",
        label="Walk-forward run",
        description="Run walk-forward validation only.",
        command=("scripts/run_walk_forward.py",),
    ),
    "parameter_sweep": ActionDefinition(
        name="parameter_sweep",
        label="Parameter sweep",
        description="Run the allowlisted parameter sweep workflow.",
        command=("scripts/run_parameter_sweep.py",),
    ),
    "research_report": ActionDefinition(
        name="research_report",
        label="Research report generation",
        description="Generate strategy research reports.",
        command=("scripts/run_research_report.py",),
    ),
    "dataset_quality": ActionDefinition(
        name="dataset_quality",
        label="Dataset quality check",
        description="Analyze dataset quality and write reports.",
        command=("scripts/check_dataset_quality.py",),
    ),
    "dataset_statistics": ActionDefinition(
        name="dataset_statistics",
        label="Dataset statistics",
        description="Generate dataset statistics.",
        command=("scripts/run_dataset_statistics.py",),
    ),
    "dataset_comparison": ActionDefinition(
        name="dataset_comparison",
        label="Dataset comparison",
        description="Compare registered research datasets.",
        command=("scripts/run_dataset_comparison.py",),
    ),
    "dataset_integrity": ActionDefinition(
        name="dataset_integrity",
        label="Dataset integrity verification",
        description="Verify dataset schema, checksum, and fingerprint.",
        command=("scripts/verify_dataset_integrity.py",),
    ),
}


class DashboardActionRunner:
    """Execute only fixed safe research actions."""

    def __init__(self, project_root: Path | str = ".", timeout_seconds: int = 120) -> None:
        self.project_root = Path(project_root)
        self.timeout_seconds = timeout_seconds

    def list_actions(self) -> list[ActionDefinition]:
        """Return allowlisted dashboard actions."""
        return list(ACTION_DEFINITIONS.values())

    def run(self, action_name: str) -> ActionResult:
        """Execute one allowlisted action with no shell interpolation."""
        if action_name not in ACTION_DEFINITIONS:
            logger.bind(component="dashboard").warning(
                "Invalid dashboard action requested: {}",
                action_name,
            )
            raise KeyError(f"Unknown dashboard action: {action_name}")
        action = ACTION_DEFINITIONS[action_name]
        command = (sys.executable, *action.command)
        logger.bind(component="dashboard").info("Running dashboard action {}", action.name)
        try:
            completed = subprocess.run(
                command,
                cwd=self.project_root,
                check=False,
                capture_output=True,
                text=True,
                timeout=self.timeout_seconds,
            )
            if completed.returncode != 0:
                logger.bind(component="dashboard").warning(
                    "Dashboard action {} failed with exit code {}",
                    action.name,
                    completed.returncode,
                )
            return ActionResult(
                action_name=action.name,
                label=action.label,
                exit_code=completed.returncode,
                stdout=self._trim(completed.stdout),
                stderr=self._trim(completed.stderr),
                command_display="python " + " ".join(action.command),
            )
        except subprocess.TimeoutExpired as exc:
            logger.bind(component="dashboard").warning(
                "Dashboard action {} timed out",
                action.name,
            )
            return ActionResult(
                action_name=action.name,
                label=action.label,
                exit_code=124,
                stdout=self._trim(exc.stdout or ""),
                stderr=self._trim(exc.stderr or ""),
                command_display="python " + " ".join(action.command),
                timed_out=True,
                error="Action timed out",
            )

    def _trim(self, value: str, limit: int = 6000) -> str:
        if len(value) <= limit:
            return value
        return value[-limit:]
