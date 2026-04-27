from __future__ import annotations

import json
from pathlib import Path

from agente_imoveis.models import SourceRecord
from agente_imoveis.utils.normalization import normalize_text


BASE_DIR = Path(__file__).resolve().parents[3]
CONFIG_DIR = BASE_DIR / "config"


CITY_ALIASES = {
    "guaiba": "Guaiba",
    "eldorado": "Eldorado do Sul",
    "eldorado do sul": "Eldorado do Sul",
    "sao jeronimo": "Sao Jeronimo",
    "arroio dos ratos": "Arroio dos Ratos",
    "charqueadas": "Charqueadas",
    "tapes": "Tapes",
    "barra do ribeiro": "Barra do Ribeiro",
    "capao da canoa": "Capao da Canoa",
    "capao": "Capao da Canoa",
    "xangrila": "Xangrila",
    "xangri la": "Xangrila",
    "xangri-la": "Xangrila",
}


def load_radar_cities() -> dict[str, dict[str, str]]:
    payload = json.loads((CONFIG_DIR / "cidades.json").read_text(encoding="utf-8"))
    radar: dict[str, dict[str, str]] = {}
    for item in payload:
        radar[normalize_text(item["cidade"])] = {
            "cidade": item["cidade"],
            "estado": item["estado"],
            "prioridade": item.get("prioridade", "media"),
        }
    return radar


def _text_blocks(record: SourceRecord) -> list[str]:
    blocks = [
        record.city,
        record.state,
        record.title,
        record.address,
        record.asset_type,
        record.link,
    ]
    for value in record.raw_payload.values():
        if isinstance(value, str):
            blocks.append(value)
    return [normalize_text(text).lower() for text in blocks if normalize_text(text)]


def infer_geography(record: SourceRecord, radar_cities: dict[str, dict[str, str]]) -> dict:
    texts = _text_blocks(record)
    joined = " | ".join(texts)
    normalized_city = normalize_text(record.city)
    normalized_state = normalize_text(record.state)
    radar_names = {value["cidade"] for value in radar_cities.values()}

    if normalized_city in radar_cities and normalized_state == "RS":
        radar = radar_cities[normalized_city]
        return {
            "city": radar["cidade"],
            "state": "RS",
            "geo_status": "cidade_radar",
            "geo_confidence": 10.0,
            "radar_match": True,
            "radar_priority": radar["prioridade"],
            "notes": [f"Cidade do radar identificada diretamente: {radar['cidade']}/RS"],
        }

    for alias, canonical in CITY_ALIASES.items():
        if alias in joined and canonical in radar_names:
            radar = radar_cities[normalize_text(canonical)]
            return {
                "city": radar["cidade"],
                "state": "RS",
                "geo_status": "cidade_radar_inferida",
                "geo_confidence": 9.0,
                "radar_match": True,
                "radar_priority": radar["prioridade"],
                "notes": [f"Cidade do radar inferida por texto: {radar['cidade']}/RS"],
            }

    if normalized_state == "RS" or any(token in joined for token in [" rio grande do sul", "/rs", "- rs", " rs "]):
        return {
            "city": normalized_city,
            "state": "RS",
            "geo_status": "rio_grande_do_sul",
            "geo_confidence": 7.0,
            "radar_match": False,
            "radar_priority": "",
            "notes": ["Ativo identificado no RS, mas fora das cidades-alvo ou sem cidade precisa."],
        }

    if normalized_city or normalized_state:
        return {
            "city": normalized_city,
            "state": normalized_state,
            "geo_status": "fora_do_radar",
            "geo_confidence": 4.0,
            "radar_match": False,
            "radar_priority": "",
            "notes": ["Ativo fora do radar geografico prioritario."],
        }

    return {
        "city": "",
        "state": "",
        "geo_status": "indefinido",
        "geo_confidence": 2.5,
        "radar_match": False,
        "radar_priority": "",
        "notes": ["Geografia ainda nao identificada com seguranca."],
    }


def filter_records_for_rs(
    records: list[SourceRecord], radar_cities: dict[str, dict[str, str]]
) -> tuple[list[SourceRecord], list[SourceRecord]]:
    inside: list[SourceRecord] = []
    outside: list[SourceRecord] = []
    for record in records:
        geo = infer_geography(record, radar_cities)
        if geo["state"] == "RS" or geo["radar_match"]:
            inside.append(record)
        else:
            outside.append(record)
    return inside, outside
