"""Validation helpers that enforce Arabic-first dashboard copy."""

from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

from app.i18n import DEFAULT_LANGUAGE, get_translations


REQUIRED_SECTIONS = ("app", "nav", "status", "pages", "metrics", "charts", "workflow", "labels")
ARABIC_RANGE = ("\u0600", "\u06ff")


@dataclass(frozen=True)
class ArabicValidationResult:
    """Result from Arabic dashboard compliance validation."""

    passed: bool
    untranslated: list[str] = field(default_factory=list)
    missing_sections: list[str] = field(default_factory=list)
    scanned_templates: int = 0

    def to_dict(self) -> dict[str, object]:
        """Return a diagnostic dictionary."""
        return {
            "passed": self.passed,
            "untranslated": self.untranslated,
            "missing_sections": self.missing_sections,
            "scanned_templates": self.scanned_templates,
        }


class ArabicDashboardValidator:
    """Detect accidental English UI copy in the Arabic-first dashboard contract."""

    def __init__(self, project_root: Path | str = ".") -> None:
        self.project_root = Path(project_root)

    def validate(self, language: str = DEFAULT_LANGUAGE) -> ArabicValidationResult:
        """Validate required translation sections and dashboard templates."""
        translations = get_translations(language)
        missing = [section for section in REQUIRED_SECTIONS if section not in translations]
        untranslated = []
        untranslated.extend(self._scan_translation_values(translations))
        template_issues, scanned = self._scan_templates()
        untranslated.extend(template_issues)
        return ArabicValidationResult(
            passed=not missing and not untranslated,
            untranslated=sorted(set(untranslated)),
            missing_sections=missing,
            scanned_templates=scanned,
        )

    def _scan_translation_values(self, translations: dict[str, Any]) -> list[str]:
        issues: list[str] = []

        def walk(prefix: str, value: Any) -> None:
            if isinstance(value, dict):
                for key, child in value.items():
                    walk(f"{prefix}.{key}" if prefix else str(key), child)
                return
            if isinstance(value, str) and not self._contains_arabic(value):
                issues.append(f"translation:{prefix}")

        for section in REQUIRED_SECTIONS:
            walk(section, translations.get(section, {}))
        return issues

    def _scan_templates(self) -> tuple[list[str], int]:
        template_root = self.project_root / "app" / "templates" / "dashboard"
        if not template_root.exists():
            return ["templates:missing_dashboard_templates"], 0
        issues = []
        scanned = 0
        english_needles = (
            "Allowlisted workflows",
            "Research Pipeline",
            "Distribution",
            "Components",
            "History",
            "Sessions",
            "Evidence",
            "Coverage",
            "Maximum",
            "Current",
            "Worst",
            "Recoveries",
            "Exit ",
        )
        for path in template_root.glob("*.html"):
            scanned += 1
            text = path.read_text(encoding="utf-8")
            for needle in english_needles:
                if needle in text:
                    issues.append(f"template:{path.name}:{needle}")
        return issues, scanned

    def _contains_arabic(self, value: str) -> bool:
        return any(ARABIC_RANGE[0] <= char <= ARABIC_RANGE[1] for char in value)
