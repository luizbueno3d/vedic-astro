"""Small i18n helper for server-rendered templates."""

from __future__ import annotations

import json
from functools import lru_cache
from pathlib import Path

DEFAULT_LOCALE = "en"
SUPPORTED_LOCALES = ("en", "pt-BR")
LOCALE_LABELS = {
    "en": "English",
    "pt-BR": "Português (BR)",
}

_LOCALES_DIR = Path(__file__).resolve().parent.parent / "locales"


def normalize_locale(value: str | None) -> str | None:
    if not value:
        return None

    normalized = value.strip().replace("_", "-")
    lowered = normalized.lower()

    if lowered in {"en", "en-us", "en-gb"}:
        return "en"
    if lowered in {"pt", "pt-br", "pt_br", "br"}:
        return "pt-BR"
    return normalized if normalized in SUPPORTED_LOCALES else None


def resolve_locale(
    requested: str | None = None,
    session_locale: str | None = None,
    accept_language: str | None = None,
) -> str:
    for candidate in (requested, session_locale):
        locale = normalize_locale(candidate)
        if locale:
            return locale

    for part in (accept_language or "").split(","):
        code = part.split(";", 1)[0].strip()
        locale = normalize_locale(code)
        if locale:
            return locale

    return DEFAULT_LOCALE


def html_lang(locale: str | None) -> str:
    return resolve_locale(locale)


def locale_options() -> list[dict[str, str]]:
    return [
        {"code": code, "label": LOCALE_LABELS[code]}
        for code in SUPPORTED_LOCALES
    ]


@lru_cache(maxsize=1)
def _load_catalogs() -> dict[str, dict]:
    catalogs = {}
    for locale in SUPPORTED_LOCALES:
        path = _LOCALES_DIR / f"{locale}.json"
        with path.open("r", encoding="utf-8") as file:
            catalogs[locale] = json.load(file)
    return catalogs


def _lookup(catalog: dict, key: str):
    current = catalog
    for part in key.split("."):
        if not isinstance(current, dict) or part not in current:
            return None
        current = current[part]
    return current if isinstance(current, str) else None


def translate(key: str, locale: str | None = None, **kwargs) -> str:
    selected = resolve_locale(locale)
    catalogs = _load_catalogs()
    text = _lookup(catalogs.get(selected, {}), key)
    if text is None and selected != DEFAULT_LOCALE:
        text = _lookup(catalogs[DEFAULT_LOCALE], key)
    if text is None:
        text = key
    return text.format(**kwargs) if kwargs else text
