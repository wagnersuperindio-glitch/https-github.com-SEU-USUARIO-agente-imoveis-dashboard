from __future__ import annotations

import json
from collections import Counter
from dataclasses import asdict
from datetime import datetime
from statistics import median
from pathlib import Path

from agente_imoveis.models import IntelligenceRecord, SourceRecord
from agente_imoveis.processing.history import build_weekly_window, save_history_snapshot
from agente_imoveis.processing.geography import infer_geography, load_radar_cities
from agente_imoveis.utils.normalization import normalize_text


BASE_DIR = Path(__file__).resolve().parents[3]
CONFIG_DIR = BASE_DIR / "config"
INTELLIGENCE_DIR = BASE_DIR / "saida" / "inteligencia"


def _load_score_rules() -> dict:
    return json.loads((CONFIG_DIR / "regua_score_v1.json").read_text(encoding="utf-8"))


def _asset_priority(asset_type: str, title: str) -> float:
    text = normalize_text(f"{asset_type} {title}").lower()
    if any(term in text for term in ["terreno", "lote", "gleba", "incorporac"]):
        return 9.2
    if any(term in text for term in ["galp", "comercial", "predio", "logistica", "loja"]):
        return 8.6
    if any(term in text for term in ["casa", "apartamento", "imovel"]):
        return 7.2
    return 6.0


def _source_priority(source_name: str, category: str) -> float:
    text = normalize_text(f"{source_name} {category}").lower()
    if any(term in text for term in ["caixa", "bb", "banrisul"]):
        return 8.9
    if any(term in text for term in ["mega", "leil", "banco_leilao", "agregador_leilao"]):
        return 8.1
    if any(term in text for term in ["imobiliaria", "portal"]):
        return 6.6
    return 6.0


def _data_quality(record: SourceRecord) -> float:
    score = 3.8
    if record.title:
        score += 1.6
    if record.link:
        score += 1.0
    if record.price:
        score += 1.2
    if record.city:
        score += 0.8
    if record.state:
        score += 0.6
    if record.area_m2:
        score += 1.0
    if record.event_date:
        score += 0.8
    if record.event_stage:
        score += 0.5
    return min(score, 10.0)


def _geo_priority(geo: dict) -> float:
    if geo["radar_match"]:
        return 9.8
    if geo["state"] == "RS":
        return 7.4
    if geo["geo_status"] == "indefinido":
        return 4.5
    return 2.8


def _decision(score: float, score_rules: dict) -> str:
    faixas = score_rules["faixas_decisao"]
    if score >= faixas["atacar_agora"]["score_minimo"]:
        return "Atacar Agora"
    if score >= faixas["aprofundar_analise"]["score_minimo"]:
        return "Aprofundar Analise"
    if score >= faixas["monitorar"]["score_minimo"]:
        return "Monitorar"
    return "Descartar"


def _asset_family(asset_type: str, title: str) -> str:
    text = normalize_text(f"{asset_type} {title}").lower()
    if any(term in text for term in ["terreno", "lote", "gleba"]):
        return "terreno"
    if any(term in text for term in ["galp", "logistica", "industrial"]):
        return "galpao"
    if any(term in text for term in ["comercial", "loja", "sala", "conjunto", "predio"]):
        return "comercial"
    if any(term in text for term in ["sitio", "chacara", "fazenda"]):
        return "rural"
    if any(term in text for term in ["apartamento", "cobertura", "studio", "kitnet"]):
        return "apartamento"
    if any(term in text for term in ["casa", "sobrado", "condominio"]):
        return "casa"
    return "outros"


def _price_per_m2(record: SourceRecord) -> float | None:
    if not record.price or not record.area_m2 or record.area_m2 <= 0:
        return None
    return round(record.price / record.area_m2, 2)


def _build_comparable_benchmarks(records: list[SourceRecord]) -> dict[tuple[str, str], float]:
    buckets: dict[tuple[str, str], list[float]] = {}
    for record in records:
        city = normalize_text(record.city)
        if not city:
            continue
        ppm2 = _price_per_m2(record)
        if ppm2 is None:
            continue
        family = _asset_family(record.asset_type, record.title)
        buckets.setdefault((city, family), []).append(ppm2)

    benchmarks: dict[tuple[str, str], float] = {}
    for key, values in buckets.items():
        if len(values) >= 3:
            benchmarks[key] = round(median(values), 2)
    return benchmarks


def _discount_score(price_per_m2: float | None, comparable_price_per_m2: float | None) -> tuple[float, float | None]:
    if price_per_m2 is None or comparable_price_per_m2 is None or comparable_price_per_m2 <= 0:
        return 5.4, None
    discount_pct = round(((comparable_price_per_m2 - price_per_m2) / comparable_price_per_m2) * 100, 2)
    if discount_pct >= 35:
        return 9.7, discount_pct
    if discount_pct >= 25:
        return 8.8, discount_pct
    if discount_pct >= 15:
        return 7.6, discount_pct
    if discount_pct >= 5:
        return 6.3, discount_pct
    if discount_pct >= 0:
        return 5.2, discount_pct
    if discount_pct >= -10:
        return 3.9, discount_pct
    return 2.4, discount_pct


def _liquidity_score(record: SourceRecord, geo: dict) -> float:
    score = 5.8
    if geo["radar_match"]:
        score += 1.2
    family = _asset_family(record.asset_type, record.title)
    if family in {"apartamento", "casa"}:
        score += 1.1
    elif family in {"terreno", "comercial"}:
        score += 0.8
    elif family == "rural":
        score -= 0.8
    if record.area_m2:
        if record.area_m2 <= 300:
            score += 1.0
        elif record.area_m2 <= 1200:
            score += 0.5
        elif record.area_m2 >= 5000:
            score -= 0.7
    if record.price:
        if record.price <= 300000:
            score += 1.0
        elif record.price <= 800000:
            score += 0.4
        elif record.price >= 2000000:
            score -= 0.6
    return round(max(2.5, min(score, 10.0)), 2)


def _risk_score(record: SourceRecord) -> float:
    text = normalize_text(f"{record.source_name} {record.category} {record.event_stage} {record.title}").lower()
    score = 7.2
    if any(term in text for term in ["leil", "judicial", "ocup", "desocup"]):
        score -= 1.6
    if any(term in text for term in ["caixa", "bb", "banrisul"]):
        score += 0.4
    if any(term in text for term in ["marketplace", "facebook"]):
        score -= 1.8
    if record.price and record.area_m2:
        score += 0.5
    if not record.price or not record.city:
        score -= 0.7
    return round(max(2.0, min(score, 10.0)), 2)


def _strategic_fit_score(record: SourceRecord, geo: dict) -> float:
    family = _asset_family(record.asset_type, record.title)
    score = 6.0
    if family == "terreno":
        score = 9.4
    elif family == "comercial":
        score = 8.9
    elif family == "galpao":
        score = 9.1
    elif family in {"casa", "apartamento"}:
        score = 7.3
    elif family == "rural":
        score = 6.4
    if geo["radar_match"]:
        score += 0.5
    return round(min(score, 10.0), 2)


def _execution_score(record: SourceRecord, data_quality: float) -> float:
    score = 4.8 + (data_quality * 0.42)
    if record.price:
        score += 0.5
    if record.area_m2:
        score += 0.4
    if record.link:
        score += 0.3
    if record.event_date:
        score -= 0.2
    return round(max(2.5, min(score, 10.0)), 2)


def enrich_records(records: list[SourceRecord]) -> list[IntelligenceRecord]:
    radar_cities = load_radar_cities()
    score_rules = _load_score_rules()
    benchmarks = _build_comparable_benchmarks(records)
    enriched: list[IntelligenceRecord] = []

    for record in records:
        geo = infer_geography(record, radar_cities)
        source_priority = _source_priority(record.source_name, record.category)
        asset_priority = _asset_priority(record.asset_type, record.title)
        data_quality = _data_quality(record)
        geo_priority = _geo_priority(geo)
        operational_score = round(
            (geo_priority * 0.42)
            + (source_priority * 0.22)
            + (asset_priority * 0.20)
            + (data_quality * 0.16),
            2,
        )
        family = _asset_family(record.asset_type, record.title)
        price_per_m2 = _price_per_m2(record)
        comparable_price_per_m2 = benchmarks.get((normalize_text(geo["city"] or record.city), family))
        discount_score, discount_pct = _discount_score(price_per_m2, comparable_price_per_m2)
        liquidity_score = _liquidity_score(record, geo)
        risk_score = _risk_score(record)
        strategic_fit_score = _strategic_fit_score(record, geo)
        execution_score = _execution_score(record, data_quality)
        investment_score = round(
            (discount_score * score_rules["pesos"]["desconto"])
            + (liquidity_score * score_rules["pesos"]["liquidez"])
            + (risk_score * score_rules["pesos"]["risco"])
            + (strategic_fit_score * score_rules["pesos"]["potencial_estrategico"])
            + (execution_score * score_rules["pesos"]["facilidade_execucao"]),
            2,
        )
        operational_decision = _decision(operational_score, score_rules)
        investment_decision = _decision(investment_score, score_rules)

        notes = list(geo["notes"])
        if discount_pct is not None:
            notes.append(f"Desconto vs comparavel interno: {discount_pct:.2f}%")
        elif comparable_price_per_m2 is None:
            notes.append("Sem base comparavel interna suficiente para desconto por m2.")
        if price_per_m2 is not None:
            notes.append(f"Preco por m2 estimado: {price_per_m2:.2f}")

        enriched.append(
            IntelligenceRecord(
                source_name=record.source_name,
                category=record.category,
                city=geo["city"] or record.city,
                state=geo["state"] or record.state,
                asset_type=record.asset_type,
                title=record.title,
                address=record.address,
                price=record.price,
                market_value=record.market_value,
                area_m2=record.area_m2,
                event_date=record.event_date,
                event_stage=record.event_stage,
                link=record.link,
                geo_status=geo["geo_status"],
                geo_confidence=geo["geo_confidence"],
                radar_match=geo["radar_match"],
                radar_priority=geo["radar_priority"],
                operational_score=operational_score,
                decision=operational_decision,
                price_per_m2=price_per_m2,
                comparable_price_per_m2=comparable_price_per_m2,
                discount_vs_comparable_pct=discount_pct,
                liquidity_score=liquidity_score,
                risk_score=risk_score,
                strategic_fit_score=strategic_fit_score,
                execution_score=execution_score,
                investment_score=investment_score,
                investment_decision=investment_decision,
                source_priority=round(source_priority, 2),
                asset_priority=round(asset_priority, 2),
                data_quality=round(data_quality, 2),
                geo_priority=round(geo_priority, 2),
                notes=notes,
            )
        )

    enriched.sort(key=lambda item: (-item.investment_score, -item.operational_score, item.source_name, item.title))
    return enriched


def build_intelligence_summary(records: list[IntelligenceRecord]) -> dict:
    decision_counter = Counter(record.decision for record in records)
    investment_counter = Counter(record.investment_decision for record in records)
    source_counter = Counter(record.source_name for record in records)
    geo_counter = Counter(record.geo_status for record in records)
    return {
        "generated_at": datetime.now().isoformat(timespec="seconds"),
        "records_total": len(records),
        "radar_matches": sum(1 for record in records if record.radar_match),
        "rio_grande_do_sul_total": sum(1 for record in records if record.state == "RS"),
        "decision_breakdown": dict(decision_counter),
        "investment_breakdown": dict(investment_counter),
        "investment_attack_now": sum(1 for record in records if record.investment_decision == "Atacar Agora"),
        "source_breakdown": dict(source_counter.most_common(10)),
        "geo_breakdown": dict(geo_counter),
    }


def save_intelligence_payload(records: list[IntelligenceRecord], executed_at: str | None = None) -> Path:
    INTELLIGENCE_DIR.mkdir(parents=True, exist_ok=True)
    snapshot_meta = save_history_snapshot(records, executed_at=executed_at)
    weekly_window = build_weekly_window(Path(snapshot_meta["path"]))
    target = INTELLIGENCE_DIR / "oportunidades_inteligencia.json"
    payload = {
        "summary": build_intelligence_summary(records),
        "history": {
            "snapshot": snapshot_meta,
            "weekly_window": {
                "path": weekly_window.get("path", ""),
                "summary": weekly_window.get("summary", {}),
                "week_start": weekly_window.get("week_start", ""),
                "baseline_executed_at": weekly_window.get("baseline_snapshot", {}).get("executed_at", ""),
            },
        },
        "records": [asdict(record) for record in records],
    }
    target.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")
    return target
