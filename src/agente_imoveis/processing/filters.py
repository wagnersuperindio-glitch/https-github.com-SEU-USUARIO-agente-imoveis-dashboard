from __future__ import annotations

from agente_imoveis.models import SourceRecord
from agente_imoveis.utils.normalization import normalize_text


def record_has_minimum_data(record: SourceRecord) -> bool:
    return bool(normalize_text(record.asset_type) and normalize_text(record.link))


def deduplicate_records(records: list[SourceRecord]) -> list[SourceRecord]:
    seen: set[tuple[str, str, str, str]] = set()
    unique: list[SourceRecord] = []
    for record in records:
        key = (
            normalize_text(record.source_name).lower(),
            normalize_text(record.city).lower(),
            normalize_text(record.title).lower(),
            normalize_text(record.link).lower(),
        )
        if key in seen:
            continue
        seen.add(key)
        unique.append(record)
    return unique
