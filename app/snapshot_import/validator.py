"""Validation for manual snapshot imports."""

from __future__ import annotations

from app.snapshot_import.models import SUPPORTED_IMPORT_TYPES
from app.snapshot_import.models import SnapshotImport
from app.snapshot_import.models import ValidationResult


def clamp(value: float) -> float:
    """Clamp score values to 0-100."""
    return round(max(0.0, min(100.0, value)), 2)


def average(values: list[float]) -> float:
    """Average bounded score values."""
    if not values:
        return 0.0
    return round(sum(clamp(value) for value in values) / len(values), 2)


class SnapshotValidationEngine:
    """Validate file structure, integrity, type, completeness, and size."""

    def __init__(self, max_size_bytes: int = 2_000_000) -> None:
        self.max_size_bytes = max_size_bytes

    def validate(self, imports: tuple[SnapshotImport, ...]) -> ValidationResult:
        count = len(imports)
        readable = sum(1 for item in imports if item.metadata.get("readable"))
        complete = sum(1 for item in imports if item.size_bytes > 0)
        supported = sum(1 for item in imports if item.import_type in SUPPORTED_IMPORT_TYPES)
        valid = sum(1 for item in imports if item.validation_status == "ناجح")
        sized = sum(1 for item in imports if item.size_bytes <= self.max_size_bytes)
        file_structure = (readable / count * 100.0) if count else 0.0
        file_integrity = (valid / count * 100.0) if count else 0.0
        supported_type = (supported / count * 100.0) if count else 0.0
        file_completeness = (complete / count * 100.0) if count else 0.0
        size_constraints = (sized / count * 100.0) if count else 0.0
        return ValidationResult(
            score=average(
                [
                    file_structure,
                    file_integrity,
                    supported_type,
                    file_completeness,
                    size_constraints,
                ]
            ),
            file_structure=clamp(file_structure),
            file_integrity=clamp(file_integrity),
            supported_type=clamp(supported_type),
            file_completeness=clamp(file_completeness),
            size_constraints=clamp(size_constraints),
        )
