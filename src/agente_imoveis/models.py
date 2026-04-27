from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any


@dataclass(slots=True)
class SourceRecord:
    source_name: str
    category: str
    city: str
    state: str
    asset_type: str
    title: str = ""
    address: str = ""
    price: float | None = None
    market_value: float | None = None
    area_m2: float | None = None
    event_date: str = ""
    event_stage: str = ""
    link: str = ""
    raw_payload: dict[str, Any] = field(default_factory=dict)


@dataclass(slots=True)
class IntelligenceRecord:
    source_name: str
    category: str
    city: str
    state: str
    asset_type: str
    title: str
    address: str
    price: float | None
    market_value: float | None
    area_m2: float | None
    event_date: str
    event_stage: str
    link: str
    geo_status: str
    geo_confidence: float
    radar_match: bool
    radar_priority: str
    operational_score: float
    decision: str
    price_per_m2: float | None
    comparable_price_per_m2: float | None
    discount_vs_comparable_pct: float | None
    liquidity_score: float
    risk_score: float
    strategic_fit_score: float
    execution_score: float
    investment_score: float
    investment_decision: str
    source_priority: float
    asset_priority: float
    data_quality: float
    geo_priority: float
    notes: list[str] = field(default_factory=list)


@dataclass(slots=True)
class SourceDefinition:
    nome: str
    categoria: str
    url: str
    prioridade: str
    tipo_monitoramento: str
    horarios_recomendados: list[str]
    tipos_ativos: list[str]
    observacoes: str
