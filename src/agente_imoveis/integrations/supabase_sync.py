from __future__ import annotations

import json
import os
import urllib.error
import urllib.request
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path


BASE_DIR = Path(__file__).resolve().parents[3]


def _read_env_file(env_path: Path) -> None:
    if not env_path.exists():
        return

    for raw_line in env_path.read_text(encoding="utf-8").splitlines():
        line = raw_line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, value = line.split("=", 1)
        os.environ.setdefault(key.strip(), value.strip())


_read_env_file(BASE_DIR / ".env")


@dataclass
class SupabaseSyncConfig:
    project_url: str
    service_role_key: str
    current_table: str = "dashboard_current"
    history_table: str = "dashboard_history"
    dashboard_slug: str = "agente-imoveis"

    @property
    def rest_base(self) -> str:
        return f"{self.project_url.rstrip('/')}/rest/v1"


def load_supabase_config() -> SupabaseSyncConfig | None:
    project_url = os.getenv("SUPABASE_URL", "").strip()
    service_role_key = os.getenv("SUPABASE_SERVICE_ROLE_KEY", "").strip()
    current_table = os.getenv("SUPABASE_CURRENT_TABLE", "dashboard_current").strip() or "dashboard_current"
    history_table = os.getenv("SUPABASE_HISTORY_TABLE", "dashboard_history").strip() or "dashboard_history"
    dashboard_slug = os.getenv("SUPABASE_DASHBOARD_SLUG", "agente-imoveis").strip() or "agente-imoveis"

    if not project_url or not service_role_key:
        return None

    return SupabaseSyncConfig(
        project_url=project_url,
        service_role_key=service_role_key,
        current_table=current_table,
        history_table=history_table,
        dashboard_slug=dashboard_slug,
    )


def _request(url: str, method: str, config: SupabaseSyncConfig, payload: dict | list | None = None) -> dict | list | None:
    data = None
    if payload is not None:
        data = json.dumps(payload, ensure_ascii=False).encode("utf-8")

    request = urllib.request.Request(url=url, data=data, method=method)
    request.add_header("apikey", config.service_role_key)
    request.add_header("Authorization", f"Bearer {config.service_role_key}")
    request.add_header("Content-Type", "application/json")
    request.add_header("Accept", "application/json")
    if method in {"POST", "PATCH"}:
        request.add_header("Prefer", "return=representation")

    try:
        with urllib.request.urlopen(request, timeout=30) as response:
            body = response.read().decode("utf-8").strip()
            if not body:
                return None
            return json.loads(body)
    except urllib.error.HTTPError as error:
        details = error.read().decode("utf-8", errors="ignore")
        raise RuntimeError(f"Falha Supabase {method} {url}: {error.code} {details}") from error


def publish_dashboard_payload(payload: dict, config: SupabaseSyncConfig) -> dict:
    executed_at = payload.get("status", {}).get("latest_execution", {}).get("executed_at", "")
    generated_at = payload.get("generated_at") or datetime.now(timezone.utc).isoformat(timespec="seconds")

    current_record = {
        "dashboard_slug": config.dashboard_slug,
        "generated_at": generated_at,
        "executed_at": executed_at,
        "project_stage": payload.get("status", {}).get("project_stage", ""),
        "dashboard_stage": payload.get("status", {}).get("dashboard_stage", ""),
        "records_total": payload.get("kpis", {}).get("records_total", 0),
        "radar_matches": payload.get("kpis", {}).get("radar_matches", 0),
        "investment_attack_now": payload.get("kpis", {}).get("investment_attack_now", 0),
        "payload": payload,
    }

    history_record = {
        "dashboard_slug": config.dashboard_slug,
        "generated_at": generated_at,
        "executed_at": executed_at,
        "payload": payload,
    }

    current_url = (
        f"{config.rest_base}/{config.current_table}"
        f"?dashboard_slug=eq.{config.dashboard_slug}"
    )
    history_url = f"{config.rest_base}/{config.history_table}"

    current_result = _request(current_url, "PATCH", config, current_record)
    if not current_result:
        current_result = _request(f"{config.rest_base}/{config.current_table}", "POST", config, current_record)

    history_result = _request(history_url, "POST", config, history_record)

    return {
        "current": current_result,
        "history": history_result,
        "generated_at": generated_at,
        "executed_at": executed_at,
    }


def load_dashboard_payload(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))
