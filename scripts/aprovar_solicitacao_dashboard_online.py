from __future__ import annotations

import argparse
import json
import sys
import urllib.error
import urllib.parse
import urllib.request
from datetime import datetime, timezone
from pathlib import Path


BASE_DIR = Path(__file__).resolve().parents[1]
if str(BASE_DIR) not in sys.path:
    sys.path.insert(0, str(BASE_DIR))

from scripts.criar_usuario_dashboard_online import create_user, find_user, update_user
from src.agente_imoveis.integrations.supabase_sync import load_supabase_config


TABLE_NAME = "dashboard_access_requests"
DEFAULT_APPROVED_PASSWORD = "Acesso#Dash_2026!"


def _request(url: str, method: str, service_role_key: str, payload: dict | None = None) -> dict | list | None:
    data = None
    if payload is not None:
        data = json.dumps(payload, ensure_ascii=False).encode("utf-8")

    request = urllib.request.Request(url=url, data=data, method=method)
    request.add_header("apikey", service_role_key)
    request.add_header("Authorization", f"Bearer {service_role_key}")
    request.add_header("Content-Type", "application/json")
    request.add_header("Accept", "application/json")
    request.add_header("Prefer", "return=representation")

    try:
        with urllib.request.urlopen(request, timeout=30) as response:
            body = response.read().decode("utf-8").strip()
            return json.loads(body) if body else None
    except urllib.error.HTTPError as error:
        details = error.read().decode("utf-8", errors="ignore")
        raise RuntimeError(f"Falha Supabase REST {method} {url}: {error.code} {details}") from error


def list_pending(rest_base: str, service_role_key: str) -> list[dict]:
    url = f"{rest_base}/{TABLE_NAME}?status=eq.pendente&order=created_at.asc"
    payload = _request(url, "GET", service_role_key)
    return payload if isinstance(payload, list) else []


def get_request(rest_base: str, service_role_key: str, request_id: str) -> dict | None:
    url = f"{rest_base}/{TABLE_NAME}?id=eq.{urllib.parse.quote(request_id, safe='')}&select=*"
    payload = _request(url, "GET", service_role_key)
    rows = payload if isinstance(payload, list) else []
    return rows[0] if rows else None


def update_request(rest_base: str, service_role_key: str, request_id: str, payload: dict) -> dict | None:
    url = f"{rest_base}/{TABLE_NAME}?id=eq.{urllib.parse.quote(request_id, safe='')}"
    result = _request(url, "PATCH", service_role_key, payload)
    rows = result if isinstance(result, list) else []
    return rows[0] if rows else None


def main() -> None:
    parser = argparse.ArgumentParser(description="Aprova ou recusa solicitacoes de acesso do dashboard online.")
    parser.add_argument("--list-pending", action="store_true")
    parser.add_argument("--request-id", default="")
    parser.add_argument("--approve", action="store_true")
    parser.add_argument("--reject", action="store_true")
    parser.add_argument("--reviewed-by", default="wagner.admin")
    parser.add_argument("--role", default="")
    parser.add_argument("--password", default="")
    parser.add_argument("--reason", default="")
    args = parser.parse_args()

    config = load_supabase_config()
    if not config:
        raise SystemExit("SUPABASE_URL e SUPABASE_SERVICE_ROLE_KEY precisam estar configurados no .env.")

    rest_base = config.rest_base
    base_url = config.project_url.rstrip("/")

    if args.list_pending:
        pending = list_pending(rest_base, config.service_role_key)
        print(json.dumps(pending, ensure_ascii=False, indent=2))
        return

    if not args.request_id:
        raise SystemExit("Informe --request-id para aprovar ou recusar uma solicitacao.")

    record = get_request(rest_base, config.service_role_key, args.request_id)
    if not record:
        raise SystemExit("Solicitacao nao encontrada.")

    if args.reject:
        updated = update_request(
            rest_base,
            config.service_role_key,
            args.request_id,
            {
                "status": "recusado",
                "reviewed_by": args.reviewed_by,
                "reviewed_at": datetime.now(timezone.utc).isoformat(timespec="seconds"),
                "justification": args.reason or record.get("justification", ""),
            },
        )
        print(json.dumps({"status": "ok", "action": "recusado", "request": updated}, ensure_ascii=False, indent=2))
        return

    if not args.approve:
        raise SystemExit("Use --approve ou --reject.")

    email = record["email"]
    password = args.password or DEFAULT_APPROVED_PASSWORD
    role = args.role or record["role_requested"]
    display_name = record["full_name"]

    user = find_user(base_url, config.service_role_key, email)
    if user:
        auth_result = update_user(
            base_url,
            config.service_role_key,
            user["id"],
            password,
            display_name,
            role,
            record.get("cpf", ""),
            record.get("document_type", ""),
            record.get("document_number", ""),
            record.get("phone", ""),
            record.get("company_name", ""),
        )
        auth_action = "atualizado"
    else:
        auth_result = create_user(
            base_url,
            config.service_role_key,
            email,
            password,
            display_name,
            role,
            record.get("cpf", ""),
            record.get("document_type", ""),
            record.get("document_number", ""),
            record.get("phone", ""),
            record.get("company_name", ""),
        )
        auth_action = "criado"

    updated = update_request(
        rest_base,
        config.service_role_key,
        args.request_id,
        {
            "status": "aprovado",
            "reviewed_by": args.reviewed_by,
            "reviewed_at": datetime.now(timezone.utc).isoformat(timespec="seconds"),
            "role_requested": role,
        },
    )

    user_id = auth_result.get("id") or (user.get("id") if user else None)

    print(
        json.dumps(
            {
                "status": "ok",
                "action": "aprovado",
                "auth_action": auth_action,
                "request": updated,
                "user_email": email,
                "password": password,
                "user_id": user_id,
            },
            ensure_ascii=False,
            indent=2,
        )
    )


if __name__ == "__main__":
    main()
