from __future__ import annotations

import json
from pathlib import Path

from agente_imoveis.models import SourceDefinition


BASE_DIR = Path(__file__).resolve().parents[3]
FONTES_PATH = BASE_DIR / "config" / "fontes.json"
IMPLANTACAO_PATH = BASE_DIR / "config" / "fontes_implantacao_v1.json"


def load_source_definitions() -> list[SourceDefinition]:
    raw = json.loads(FONTES_PATH.read_text(encoding="utf-8"))
    return [SourceDefinition(**item) for item in raw]


def load_implementation_plan() -> dict:
    return json.loads(IMPLANTACAO_PATH.read_text(encoding="utf-8"))


def filter_sources_by_names(names: list[str]) -> list[SourceDefinition]:
    wanted = set(names)
    return [source for source in load_source_definitions() if source.nome in wanted]
