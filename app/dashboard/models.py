"""Dashboard view models for the local research UI."""

from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
from typing import Any


@dataclass(frozen=True)
class DashboardConfig:
    """Safe local dashboard configuration."""

    enabled: bool = True
    host: str = "127.0.0.1"
    port: int = 8000
    reports_dir: str = "reports"
    allow_actions: bool = True


@dataclass(frozen=True)
class ReportFile:
    """One report discovered under the configured reports directory."""

    report_id: str
    name: str
    path: Path
    relative_path: str
    report_type: str
    size_bytes: int
    modified_at: str


@dataclass(frozen=True)
class ReportContent:
    """Parsed report content for rendering."""

    file: ReportFile
    title: str
    raw_text: str
    json_data: Any | None = None
    csv_headers: list[str] = field(default_factory=list)
    csv_rows: list[list[str]] = field(default_factory=list)
    error: str | None = None


@dataclass(frozen=True)
class StrategySummary:
    """Strategy metadata normalized for templates."""

    strategy_id: str
    name: str
    description: str
    version: str
    metadata: dict[str, Any]
    parameters: dict[str, Any]
    default_configuration: dict[str, Any]
    latest_signal_summary: dict[str, Any] | None = None
    latest_report: ReportFile | None = None


@dataclass(frozen=True)
class DatasetSummary:
    """Dataset metadata and quality summary."""

    dataset_id: str
    name: str
    symbol: str
    timeframe: str
    version: str
    row_count: int
    start_time: str | None
    end_time: str | None
    checksum: str | None
    fingerprint: str | None
    quality_score: float | None
    gap_count: int
    duplicate_count: int
    integrity_status: str
    latest_report: ReportFile | None = None


@dataclass(frozen=True)
class ValidationSummary:
    """Validation report summary."""

    report_id: str
    strategy_name: str
    dataset_name: str
    robustness_score: float | None
    robustness_category: str
    out_of_sample_summary: dict[str, Any]
    walk_forward_summary: dict[str, Any]
    parameter_sweep_summary: dict[str, Any]
    overfitting_warnings: list[dict[str, Any]]
    latest_report: ReportFile | None = None


@dataclass(frozen=True)
class ActionDefinition:
    """Allowlisted dashboard action."""

    name: str
    label: str
    description: str
    command: tuple[str, ...]


@dataclass(frozen=True)
class ActionResult:
    """Result from a safe research action execution."""

    action_name: str
    label: str
    exit_code: int
    stdout: str
    stderr: str
    command_display: str
    timed_out: bool = False
    error: str | None = None


@dataclass(frozen=True)
class DashboardOverview:
    """Home page aggregate data."""

    strategies: list[StrategySummary]
    datasets: list[DatasetSummary]
    validations: list[ValidationSummary]
    reports: list[ReportFile]
    latest_validation_report: ReportFile | None
    latest_dataset_report: ReportFile | None
    latest_backtest_report: ReportFile | None
    latest_robustness_score: float | None
    latest_dataset_quality_score: float | None
    warning_counts: dict[str, int]
