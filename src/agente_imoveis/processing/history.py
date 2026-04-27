from __future__ import annotations

import json
from dataclasses import asdict
from datetime import datetime, timedelta
from pathlib import Path

from agente_imoveis.models import IntelligenceRecord
from agente_imoveis.utils.normalization import normalize_text, slugify


BASE_DIR = Path(__file__).resolve().parents[3]
HISTORY_DIR = BASE_DIR / "saida" / "historico"
SNAPSHOT_DIR = HISTORY_DIR / "snapshots"
WINDOW_DIR = HISTORY_DIR / "janelas"


def _ensure_dirs() -> None:
    SNAPSHOT_DIR.mkdir(parents=True, exist_ok=True)
    WINDOW_DIR.mkdir(parents=True, exist_ok=True)


def _parse_timestamp(value: str | None) -> datetime:
    if value:
        try:
            return datetime.fromisoformat(value)
        except ValueError:
            pass
    return datetime.now()


def _extract_numeric_token(value: float | None) -> str:
    if value is None:
        return ""
    return f"{value:.2f}"


def build_asset_key(record: IntelligenceRecord) -> str:
    title_token = slugify(record.title)[:80]
    address_token = slugify(record.address)[:80]
    city_token = slugify(record.city)[:40]
    area_token = _extract_numeric_token(record.area_m2)
    price_token = _extract_numeric_token(record.price)
    source_token = slugify(record.source_name)
    if record.link:
        link_token = slugify(record.link)[:120]
        return f"{source_token}__{link_token}"
    return "__".join(token for token in [source_token, city_token, title_token, address_token, area_token, price_token] if token)


def _snapshot_entry(record: IntelligenceRecord) -> dict:
    payload = asdict(record)
    payload["asset_key"] = build_asset_key(record)
    return payload


def save_history_snapshot(records: list[IntelligenceRecord], executed_at: str | None = None) -> dict:
    _ensure_dirs()
    snapshot_time = _parse_timestamp(executed_at)
    snapshot_token = snapshot_time.strftime("%Y-%m-%d_%H-%M-%S")
    entries = [_snapshot_entry(record) for record in records]
    snapshot_payload = {
        "generated_at": datetime.now().isoformat(timespec="seconds"),
        "executed_at": snapshot_time.isoformat(timespec="seconds"),
        "records_total": len(entries),
        "records": entries,
    }
    target = SNAPSHOT_DIR / f"{snapshot_token}_snapshot_inteligencia.json"
    target.write_text(json.dumps(snapshot_payload, ensure_ascii=False, indent=2), encoding="utf-8")
    return {
        "path": str(target),
        "executed_at": snapshot_payload["executed_at"],
        "records_total": len(entries),
    }


def list_snapshots() -> list[Path]:
    _ensure_dirs()
    return sorted(SNAPSHOT_DIR.glob("*_snapshot_inteligencia.json"))


def load_snapshot(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def _start_of_week(reference: datetime) -> datetime:
    return datetime(reference.year, reference.month, reference.day) - timedelta(days=reference.weekday())


def select_baseline_snapshot(current_snapshot_path: Path) -> Path | None:
    snapshots = list_snapshots()
    if current_snapshot_path not in snapshots:
        snapshots.append(current_snapshot_path)
        snapshots = sorted(snapshots)
    current_snapshot = load_snapshot(current_snapshot_path)
    current_time = _parse_timestamp(current_snapshot.get("executed_at"))
    week_start = _start_of_week(current_time)

    baseline_candidates: list[Path] = []
    previous_candidates: list[Path] = []
    for path in snapshots:
        if path == current_snapshot_path:
            continue
        executed_at = _parse_timestamp(load_snapshot(path).get("executed_at"))
        if executed_at < week_start:
            baseline_candidates.append(path)
        if executed_at < current_time:
            previous_candidates.append(path)

    if baseline_candidates:
        return baseline_candidates[-1]
    if previous_candidates:
        return previous_candidates[-1]
    return None


def _diff_fields(current: dict, previous: dict) -> list[str]:
    changes: list[str] = []
    if current.get("price") != previous.get("price"):
        changes.append("preco")
    if current.get("operational_score") != previous.get("operational_score"):
        changes.append("score")
    if current.get("investment_score") != previous.get("investment_score"):
        changes.append("score_investimento")
    if current.get("decision") != previous.get("decision"):
        changes.append("decisao")
    if current.get("investment_decision") != previous.get("investment_decision"):
        changes.append("decisao_investimento")
    if current.get("geo_status") != previous.get("geo_status"):
        changes.append("geografia")
    if current.get("city") != previous.get("city") or current.get("state") != previous.get("state"):
        changes.append("cidade_estado")
    return changes


def build_weekly_window(current_snapshot_path: Path) -> dict:
    current_snapshot = load_snapshot(current_snapshot_path)
    baseline_path = select_baseline_snapshot(current_snapshot_path)
    baseline_snapshot = load_snapshot(baseline_path) if baseline_path else {"records": [], "executed_at": ""}

    current_records = {item["asset_key"]: item for item in current_snapshot.get("records", [])}
    baseline_records = {item["asset_key"]: item for item in baseline_snapshot.get("records", [])}

    entered = [current_records[key] for key in sorted(current_records.keys() - baseline_records.keys())]
    exited = [baseline_records[key] for key in sorted(baseline_records.keys() - current_records.keys())]

    changed: list[dict] = []
    for key in sorted(current_records.keys() & baseline_records.keys()):
        current = current_records[key]
        previous = baseline_records[key]
        fields = _diff_fields(current, previous)
        if not fields:
            continue
        changed.append(
            {
                "asset_key": key,
                "fields_changed": fields,
                "current": current,
                "previous": previous,
            }
        )

    current_time = _parse_timestamp(current_snapshot.get("executed_at"))
    week_start = _start_of_week(current_time)
    payload = {
        "generated_at": datetime.now().isoformat(timespec="seconds"),
        "week_reference": current_time.isoformat(timespec="seconds"),
        "week_start": week_start.isoformat(timespec="seconds"),
        "current_snapshot": {
            "path": str(current_snapshot_path),
            "executed_at": current_snapshot.get("executed_at", ""),
            "records_total": current_snapshot.get("records_total", len(current_snapshot.get("records", []))),
        },
        "baseline_snapshot": {
            "path": str(baseline_path) if baseline_path else "",
            "executed_at": baseline_snapshot.get("executed_at", ""),
            "records_total": baseline_snapshot.get("records_total", len(baseline_snapshot.get("records", []))),
        },
        "summary": {
            "entered_total": len(entered),
            "changed_total": len(changed),
            "exited_total": len(exited),
        },
        "entered": entered,
        "changed": changed,
        "exited": exited,
    }

    _ensure_dirs()
    target = WINDOW_DIR / f"{current_time.strftime('%Y-%m-%d_%H-%M-%S')}_janela_semanal.json"
    target.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")
    payload["path"] = str(target)
    return payload


def load_latest_weekly_window() -> dict:
    _ensure_dirs()
    files = sorted(WINDOW_DIR.glob("*_janela_semanal.json"))
    if not files:
        return {}
    payload = load_snapshot(files[-1])
    payload["path"] = str(files[-1])
    return payload
