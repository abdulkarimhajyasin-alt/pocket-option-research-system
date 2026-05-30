"""Safe allowlisted research actions for the dashboard."""

from __future__ import annotations

import subprocess
import sys
from pathlib import Path

from loguru import logger

from app.dashboard.models import ActionDefinition, ActionResult
from app.jobs.models import JobResult
from app.jobs.registry import JobRegistry


ACTION_DEFINITIONS: dict[str, ActionDefinition] = {
    "strategy_research": ActionDefinition(
        name="strategy_research",
        label="تشغيل بحث الاستراتيجية",
        description="تشغيل مسار بحث الاستراتيجية القابل للتفسير.",
        command=("scripts/run_strategy_research.py",),
    ),
    "validation": ActionDefinition(
        name="validation",
        label="تشغيل التحقق",
        description="تشغيل مسار التحقق الكامل.",
        command=("scripts/run_validation.py",),
    ),
    "walk_forward": ActionDefinition(
        name="walk_forward",
        label="تحقق النافذة المتحركة",
        description="تشغيل تحقق النافذة المتحركة فقط.",
        command=("scripts/run_walk_forward.py",),
    ),
    "parameter_sweep": ActionDefinition(
        name="parameter_sweep",
        label="فحص المعاملات",
        description="تشغيل فحص المعاملات المسموح به.",
        command=("scripts/run_parameter_sweep.py",),
    ),
    "research_report": ActionDefinition(
        name="research_report",
        label="توليد تقرير البحث",
        description="توليد تقارير بحث الاستراتيجية.",
        command=("scripts/run_research_report.py",),
    ),
    "dataset_quality": ActionDefinition(
        name="dataset_quality",
        label="فحص جودة البيانات",
        description="تحليل جودة البيانات وتوليد التقارير.",
        command=("scripts/check_dataset_quality.py",),
    ),
    "dataset_statistics": ActionDefinition(
        name="dataset_statistics",
        label="إحصاءات البيانات",
        description="توليد إحصاءات مجموعة البيانات.",
        command=("scripts/run_dataset_statistics.py",),
    ),
    "dataset_comparison": ActionDefinition(
        name="dataset_comparison",
        label="مقارنة البيانات",
        description="مقارنة مجموعات البيانات البحثية المسجلة.",
        command=("scripts/run_dataset_comparison.py",),
    ),
    "dataset_integrity": ActionDefinition(
        name="dataset_integrity",
        label="تحقق سلامة البيانات",
        description="التحقق من مخطط البيانات والبصمة والمجموع الاختباري.",
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
        job_result = self.run_job(action_name)
        action = ACTION_DEFINITIONS[action_name]
        return ActionResult(
            action_name=action.name,
            label=action.label,
            exit_code=job_result.exit_code,
            stdout=job_result.stdout,
            stderr=job_result.stderr,
            command_display="python " + " ".join(action.command),
            timed_out=job_result.exit_code == 124,
            error=job_result.error,
        )

    def run_job(self, action_name: str) -> JobResult:
        """Execute one allowlisted action and return a background-job result."""
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
            return JobResult(
                exit_code=completed.returncode,
                stdout=self._trim(completed.stdout),
                stderr=self._trim(completed.stderr),
            )
        except subprocess.TimeoutExpired as exc:
            logger.bind(component="dashboard").warning(
                "Dashboard action {} timed out",
                action.name,
            )
            return JobResult(
                exit_code=124,
                stdout=self._trim(exc.stdout or ""),
                stderr=self._trim(exc.stderr or ""),
                error="Action timed out",
            )

    def _trim(self, value: str, limit: int = 6000) -> str:
        if len(value) <= limit:
            return value
        return value[-limit:]

    def job_registry(self) -> JobRegistry:
        """Return a job registry backed by this runner."""
        registry = JobRegistry()
        for action in ACTION_DEFINITIONS.values():
            registry.register(action, lambda name=action.name: self.run_job(name))
        return registry
