from __future__ import annotations

import re
import unicodedata


def normalize_text(value: str) -> str:
    normalized = unicodedata.normalize("NFKD", value or "")
    return "".join(char for char in normalized if not unicodedata.combining(char)).strip()


def slugify(value: str) -> str:
    value = normalize_text(value).lower()
    value = re.sub(r"[^a-z0-9]+", "-", value)
    return value.strip("-")


def parse_brl_number(text: str) -> float | None:
    if not text:
        return None
    cleaned = normalize_text(text)
    match = re.search(r"([\d\.\,]+)", cleaned)
    if not match:
        return None
    number = match.group(1).replace(".", "").replace(",", ".")
    try:
        return float(number)
    except ValueError:
        return None


def detect_city_state(text: str) -> tuple[str, str]:
    cleaned = normalize_text(text)
    if "," in cleaned:
        city, state = [part.strip() for part in cleaned.split(",", 1)]
        return city, state
    return cleaned, ""
