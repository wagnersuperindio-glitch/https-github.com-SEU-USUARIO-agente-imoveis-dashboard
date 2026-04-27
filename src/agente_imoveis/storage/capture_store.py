from __future__ import annotations

import json
from dataclasses import asdict
from datetime import datetime
from pathlib import Path

from agente_imoveis.models import SourceRecord
from agente_imoveis.utils.normalization import slugify


BASE_DIR = Path(__file__).resolve().parents[3]
RAW_DIR = BASE_DIR / "saida" / "capturas_brutas"
NORMALIZED_DIR = BASE_DIR / "saida" / "capturas_normalizadas"
EXECUTION_DIR = BASE_DIR / "saida" / "execucoes"


def timestamp_token() -> str:
    return datetime.now().strftime("%Y-%m-%d_%H-%M-%S")


def ensure_dirs() -> None:
    RAW_DIR.mkdir(parents=True, exist_ok=True)
    NORMALIZED_DIR.mkdir(parents=True, exist_ok=True)
    EXECUTION_DIR.mkdir(parents=True, exist_ok=True)


def save_raw_capture(source_name: str, content: str, suffix: str = "html") -> Path:
    ensure_dirs()
    filename = f"{timestamp_token()}_{slugify(source_name)}.{suffix}"
    target = RAW_DIR / filename
    target.write_text(content, encoding="utf-8")
    return target


def save_records(source_name: str, records: list[SourceRecord]) -> Path:
    ensure_dirs()
    filename = f"{timestamp_token()}_{slugify(source_name)}.json"
    target = NORMALIZED_DIR / filename
    payload = [asdict(record) for record in records]
    target.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")
    return target


def save_execution_summary(summary: dict) -> Path:
    ensure_dirs()
    filename = f"{timestamp_token()}_resumo_execucao_mvp.json"
    target = EXECUTION_DIR / filename
    target.write_text(json.dumps(summary, ensure_ascii=False, indent=2), encoding="utf-8")
    return target
