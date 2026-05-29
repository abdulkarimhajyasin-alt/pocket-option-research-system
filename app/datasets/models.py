"""Dataset management domain models."""

from __future__ import annotations

from dataclasses import asdict, dataclass, field
from datetime import datetime
from enum import StrEnum
from typing import Any


class GapSeverity(StrEnum):
    """Gap classification levels."""

    EXPECTED = "expected"
    SUSPICIOUS = "suspicious"
    SEVERE = "severe"


class DatasetProfile(StrEnum):
    """Deterministic synthetic market profiles."""

    TRENDING = "trending"
    RANGING = "ranging"
    VOLATILE = "volatile"
    LOW_VOLATILITY = "low_volatility"
    NOISY = "noisy"


@dataclass(frozen=True)
class DatasetMetadata:
    """Immutable metadata for a registered research dataset."""

    dataset_id: str
    dataset_name: str
    source: str
    symbol: str
    timeframe: str
    start_time: datetime | None
    end_time: datetime | None
    row_count: int
    checksum: str
    version: str
    tags: tuple[str, ...] = ()

    def to_dict(self) -> dict[str, Any]:
        """Return serializable metadata."""
        payload = asdict(self)
        payload["start_time"] = self.start_time.isoformat() if self.start_time else None
        payload["end_time"] = self.end_time.isoformat() if self.end_time else None
        payload["tags"] = list(self.tags)
        return payload


@dataclass(frozen=True)
class DatasetVersion:
    """One immutable version record for a dataset."""

    dataset_id: str
    version: str
    generated_at: datetime
    checksum: str
    row_count: int
    source_changes: str = "initial"
    quality_score: float = 0.0
    quality_changes: str = "not recorded"
    parent_version: str | None = None

    def to_dict(self) -> dict[str, Any]:
        """Return serializable version metadata."""
        payload = asdict(self)
        payload["generated_at"] = self.generated_at.isoformat()
        return payload


@dataclass(frozen=True)
class QualityIssue:
    """One explainable data-quality issue."""

    code: str
    severity: str
    message: str
    count: int = 1
    sample: str | None = None

    def to_dict(self) -> dict[str, Any]:
        """Return serializable issue."""
        return asdict(self)


@dataclass(frozen=True)
class GapRecord:
    """One detected timestamp gap."""

    start: datetime
    end: datetime
    expected_seconds: int
    actual_seconds: int
    missing_intervals: int
    severity: GapSeverity
    reason: str

    def to_dict(self) -> dict[str, Any]:
        """Return serializable gap record."""
        return {
            "start": self.start.isoformat(),
            "end": self.end.isoformat(),
            "expected_seconds": self.expected_seconds,
            "actual_seconds": self.actual_seconds,
            "missing_intervals": self.missing_intervals,
            "severity": self.severity.value,
            "reason": self.reason,
        }


@dataclass(frozen=True)
class QualityReport:
    """Complete data-quality output for one dataset."""

    dataset_id: str
    dataset_name: str
    quality_score: float
    row_count: int
    warnings: list[QualityIssue]
    errors: list[QualityIssue]
    gaps: list[GapRecord]
    components: dict[str, float]

    @property
    def passed(self) -> bool:
        """Return whether the dataset is safe for research usage."""
        return not self.errors

    def to_dict(self) -> dict[str, Any]:
        """Return serializable quality report."""
        return {
            "dataset_id": self.dataset_id,
            "dataset_name": self.dataset_name,
            "quality_score": self.quality_score,
            "row_count": self.row_count,
            "passed": self.passed,
            "warnings": [warning.to_dict() for warning in self.warnings],
            "errors": [error.to_dict() for error in self.errors],
            "gaps": [gap.to_dict() for gap in self.gaps],
            "components": self.components,
        }


@dataclass(frozen=True)
class IntegrityReport:
    """Integrity verification report."""

    dataset_id: str
    checksum: str
    fingerprint: str
    row_count: int
    schema_valid: bool
    row_count_valid: bool
    checksum_valid: bool
    issues: list[str] = field(default_factory=list)

    @property
    def passed(self) -> bool:
        """Return whether integrity verification passed."""
        return self.schema_valid and self.row_count_valid and self.checksum_valid

    def to_dict(self) -> dict[str, Any]:
        """Return serializable integrity report."""
        return {**asdict(self), "passed": self.passed}


@dataclass(frozen=True)
class DatasetStatistics:
    """Research statistics for one normalized dataset."""

    dataset_id: str
    dataset_name: str
    row_count: int
    start_time: datetime | None
    end_time: datetime | None
    average_candle_size: float
    volatility_estimate: float
    gap_count: int
    duplicate_count: int
    quality_score: float

    def to_dict(self) -> dict[str, Any]:
        """Return serializable statistics."""
        payload = asdict(self)
        payload["start_time"] = self.start_time.isoformat() if self.start_time else None
        payload["end_time"] = self.end_time.isoformat() if self.end_time else None
        return payload


@dataclass(frozen=True)
class DatasetComparisonReport:
    """Comparison output across datasets."""

    report_id: str
    datasets: list[str]
    rankings: list[dict[str, Any]]
    comparisons: list[dict[str, Any]]

    def to_dict(self) -> dict[str, Any]:
        """Return serializable comparison report."""
        return asdict(self)
