"""Small localization foundation for dashboard UI copy."""

from __future__ import annotations

from typing import Any

from app.i18n.ar import AR_TRANSLATIONS


DEFAULT_LANGUAGE = "ar"
SUPPORTED_LANGUAGES = ("ar", "en")

_TRANSLATIONS: dict[str, dict[str, Any]] = {
    "ar": AR_TRANSLATIONS,
}


def get_translations(language: str = DEFAULT_LANGUAGE) -> dict[str, Any]:
    """Return UI translations for a supported language."""
    if language not in SUPPORTED_LANGUAGES:
        language = DEFAULT_LANGUAGE
    return _TRANSLATIONS.get(language, AR_TRANSLATIONS)


def translate(key: str, language: str = DEFAULT_LANGUAGE, default: str | None = None) -> str:
    """Resolve a dotted translation key."""
    current: Any = get_translations(language)
    for part in key.split("."):
        if not isinstance(current, dict) or part not in current:
            return default or key
        current = current[part]
    return str(current)
