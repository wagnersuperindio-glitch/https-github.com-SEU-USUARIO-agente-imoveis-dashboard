from __future__ import annotations

import json
from collections import Counter
from dataclasses import asdict
from datetime import datetime
from pathlib import Path

from agente_imoveis.models import SourceRecord
from agente_imoveis.processing.history import load_latest_weekly_window
from agente_imoveis.processing.intelligence import enrich_records
from agente_imoveis.storage.capture_store import EXECUTION_DIR


BASE_DIR = Path(__file__).resolve().parents[3]
CONFIG_DIR = BASE_DIR / "config"
REPORT_DIR = BASE_DIR / "saida" / "relatorios"


def _load_json(path: Path) -> dict | list:
    return json.loads(path.read_text(encoding="utf-8"))


def _latest_file(directory: Path, pattern: str) -> Path | None:
    files = sorted(directory.glob(pattern))
    return files[-1] if files else None


def _load_latest_execution_summary() -> dict:
    latest = _latest_file(EXECUTION_DIR, "*_resumo_execucao_mvp.json")
    if not latest:
        return {}
    summary = _load_json(latest)
    summary["path"] = str(latest)
    return summary


def _load_latest_report() -> dict:
    latest = _latest_file(REPORT_DIR, "relatorio_*.md")
    if not latest:
        return {}
    return {
        "path": str(latest),
        "name": latest.name,
        "updated_at": datetime.fromtimestamp(latest.stat().st_mtime).isoformat(timespec="seconds"),
    }


def _load_execution_history(limit: int = 6) -> list[dict]:
    history: list[dict] = []
    for path in sorted(EXECUTION_DIR.glob("*_resumo_execucao_mvp.json"), reverse=True)[:limit]:
        payload = _load_json(path)
        history.append(
            {
                "executed_at": payload.get("executed_at", ""),
                "connectors_total": payload.get("connectors_total", 0),
                "connectors_success": payload.get("connectors_success", 0),
                "connectors_error": payload.get("connectors_error", 0),
                "records_total": payload.get("records_total", 0),
                "path": str(path),
            }
        )
    return history


def _load_report_history(limit: int = 6) -> list[dict]:
    history: list[dict] = []
    for path in sorted(REPORT_DIR.glob("relatorio_*.md"), reverse=True)[:limit]:
        history.append(
            {
                "name": path.name,
                "updated_at": datetime.fromtimestamp(path.stat().st_mtime).isoformat(timespec="seconds"),
                "path": str(path),
            }
        )
    return history


def _load_records_from_summary(summary: dict) -> list[SourceRecord]:
    records: list[SourceRecord] = []
    for item in summary.get("results", []):
        output_path = item.get("output_path", "").strip()
        if not output_path:
            continue
        path = Path(output_path)
        if not path.exists():
            continue
        for payload in _load_json(path):
            records.append(SourceRecord(**payload))
    return records


def _format_currency(value: float | None) -> str:
    if value is None:
        return "-"
    inteiro = f"{value:,.2f}"
    return f"R$ {inteiro}".replace(",", "X").replace(".", ",").replace("X", ".")


def _window_preview(items: list[dict], limit: int = 8) -> list[dict]:
    return [
        {
            "title": item.get("title", "Ativo sem titulo"),
            "city": item.get("city", "") or "-",
            "state": item.get("state", "") or "-",
            "source_name": item.get("source_name", "") or "-",
            "price_label": _format_currency(item.get("price")),
            "asset_type": item.get("asset_type", "") or "-",
            "link": item.get("link", "") or "",
        }
        for item in items[:limit]
    ]


def build_dashboard_payload() -> dict:
    summary = _load_latest_execution_summary()
    report = _load_latest_report()
    raw_records = _load_records_from_summary(summary)
    enriched_objects = enrich_records(raw_records)
    enriched_records = [asdict(record) for record in enriched_objects]
    enriched_records.sort(
        key=lambda item: (
            -item["investment_score"],
            -item["operational_score"],
            item["investment_decision"],
            item["decision"],
            item["source_name"],
            item["title"],
        )
    )

    decision_counter = Counter(item["decision"] for item in enriched_records)
    investment_counter = Counter(item["investment_decision"] for item in enriched_records)
    source_counter = Counter(item["source_name"] for item in enriched_records)
    radar_counter = Counter("No Radar" if item["radar_match"] else "Fora do Radar" for item in enriched_records)

    decorated_records = [
        {
            **item,
            "price_label": _format_currency(item["price"]),
            "price_per_m2_label": _format_currency(item["price_per_m2"]),
            "comparable_price_per_m2_label": _format_currency(item["comparable_price_per_m2"]),
            "discount_label": f"{item['discount_vs_comparable_pct']:.1f}%" if item["discount_vs_comparable_pct"] is not None else "-",
            "area_label": f"{item['area_m2']:.0f} m²" if item["area_m2"] else "-",
        }
        for item in enriched_records
    ]

    blocked_sources = [
        {
            "source_name": item["source_name"],
            "connector_name": item["connector_name"],
            "error": item["error"],
        }
        for item in summary.get("results", [])
        if item.get("status") == "error"
    ]

    radar_cities = sorted(
        [
            {
                "city_state": f"{item['cidade']}/{item['estado']}",
                "priority": item.get("prioridade", "media"),
            }
            for item in _load_json(CONFIG_DIR / "cidades.json")
        ],
        key=lambda item: item["city_state"],
    )

    weekly_window = load_latest_weekly_window()
    weekly_summary = weekly_window.get("summary", {})
    execution_history = _load_execution_history()
    report_history = _load_report_history()

    return {
        "generated_at": datetime.now().isoformat(timespec="seconds"),
        "status": {
            "project_stage": "MVP Real em Operacao",
            "dashboard_stage": "Painel Web Executivo",
            "last_report": report,
            "latest_execution": {
                "executed_at": summary.get("executed_at", ""),
                "summary_path": summary.get("path", ""),
                "connectors_total": summary.get("connectors_total", 0),
                "connectors_success": summary.get("connectors_success", 0),
                "connectors_error": summary.get("connectors_error", 0),
                "records_total": summary.get("records_total", 0),
            },
        },
        "kpis": {
            "connectors_total": summary.get("connectors_total", 0),
            "success_sources": summary.get("connectors_success", 0),
            "blocked_sources": summary.get("connectors_error", 0),
            "records_total": len(decorated_records),
            "radar_matches": sum(1 for item in decorated_records if item["radar_match"]),
            "rio_grande_do_sul": sum(1 for item in decorated_records if item["state"] == "RS"),
            "attack_now": decision_counter.get("Atacar Agora", 0),
            "investment_attack_now": investment_counter.get("Atacar Agora", 0),
            "entered_week": weekly_summary.get("entered_total", 0),
            "changed_week": weekly_summary.get("changed_total", 0),
            "exited_week": weekly_summary.get("exited_total", 0),
        },
        "decision_breakdown": [
            {"label": label, "value": value}
            for label, value in sorted(decision_counter.items(), key=lambda item: (-item[1], item[0]))
        ],
        "investment_breakdown": [
            {"label": label, "value": value}
            for label, value in sorted(investment_counter.items(), key=lambda item: (-item[1], item[0]))
        ],
        "source_breakdown": [{"label": label, "value": value} for label, value in source_counter.most_common(8)],
        "radar_breakdown": [{"label": label, "value": value} for label, value in radar_counter.items()],
        "blocked_sources": blocked_sources,
        "weekly_window": weekly_window,
        "weekly_movement": {
            "summary": weekly_summary,
            "entered": _window_preview(weekly_window.get("entered", [])),
            "changed": _window_preview(weekly_window.get("changed", [])),
            "exited": _window_preview(weekly_window.get("exited", [])),
        },
        "execution_history": execution_history,
        "report_history": report_history,
        "top_opportunities": decorated_records[:12],
        "all_opportunities": decorated_records,
        "filters": {
            "sources": sorted({item["source_name"] for item in decorated_records if item["source_name"]}),
            "decisions": sorted({item["decision"] for item in decorated_records if item["decision"]}),
            "investment_decisions": sorted(
                {item["investment_decision"] for item in decorated_records if item["investment_decision"]}
            ),
            "states": sorted({item["state"] for item in decorated_records if item["state"]}),
            "geo_status": sorted({item["geo_status"] for item in decorated_records if item["geo_status"]}),
        },
        "radar_cities": radar_cities,
    }
