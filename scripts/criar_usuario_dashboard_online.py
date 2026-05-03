from __future__ import annotations

import argparse
import json
import sys
import urllib.error
import urllib.parse
import urllib.request
from pathlib import Path


BASE_DIR = Path(__file__).resolve().parents[1]
if str(BASE_DIR) not in sys.path:
    sys.path.insert(0, str(BASE_DIR))

from src.agente_imoveis.integrations.supabase_sync import load_supabase_config


def _request(url: str, method: str, service_role_key: str, payload: dict | None = None) -> dict | list | None:
    data = None
    if payload is not None:
        data = json.dumps(payload, ensure_ascii=False).encode("utf-8")

    request = urllib.request.Request(url=url, data=data, method=method)
    request.add_header("apikey", service_role_key)
    request.add_header("Authorization", f"Bearer {service_role_key}")
    request.add_header("Content-Type", "application/json")
    request.add_header("Accept", "application/json")

    try:
        with urllib.request.urlopen(request, timeout=30) as response:
            body = response.read().decode("utf-8").strip()
            return json.loads(body) if body else None
    except urllib.error.HTTPError as error:
        details = error.read().decode("utf-8", errors="ignore")
        raise RuntimeError(f"Falha Supabase Auth {method} {url}: {error.code} {details}") from error


def find_user(base_url: str, service_role_key: str, email: str) -> dict | None:
    page = 1
    while True:
        url = f"{base_url}/auth/v1/admin/users?page={page}&per_page=200"
        payload = _request(url, "GET", service_role_key) or {}
        users = payload.get("users", []) if isinstance(payload, dict) else []
        if not users:
            return None

        for user in users:
            if (user.get("email") or "").lower() == email.lower():
                return user

        if len(users) < 200:
            return None
        page += 1


def create_user(base_url: str, service_role_key: str, email: str, password: str, display_name: str, role: str) -> dict:
    payload = {
        "email": email,
        "password": password,
        "email_confirm": True,
        "user_metadata": {
            "display_name": display_name,
            "role": role,
        },
    }
    return _request(f"{base_url}/auth/v1/admin/users", "POST", service_role_key, payload) or {}


def update_user(base_url: str, service_role_key: str, user_id: str, password: str, display_name: str, role: str) -> dict:
    payload = {
        "password": password,
        "user_metadata": {
            "display_name": display_name,
            "role": role,
        },
    }
    safe_user_id = urllib.parse.quote(user_id, safe="")
    return _request(f"{base_url}/auth/v1/admin/users/{safe_user_id}", "PUT", service_role_key, payload) or {}


def main() -> None:
    parser = argparse.ArgumentParser(description="Cria ou redefine um usuario do dashboard online no Supabase.")
    parser.add_argument("--email", default="wagner.admin@superindio.local")
    parser.add_argument("--password", default="Dash#SuperIndio2026!")
    parser.add_argument("--display-name", default="Wagner Admin")
    parser.add_argument("--role", default="admin")
    args = parser.parse_args()

    config = load_supabase_config()
    if not config:
        raise SystemExit("SUPABASE_URL e SUPABASE_SERVICE_ROLE_KEY precisam estar configurados no .env.")

    base_url = config.project_url.rstrip("/")
    user = find_user(base_url, config.service_role_key, args.email)
    if user:
        result = update_user(base_url, config.service_role_key, user["id"], args.password, args.display_name, args.role)
        action = "atualizado"
    else:
        result = create_user(base_url, config.service_role_key, args.email, args.password, args.display_name, args.role)
        action = "criado"

    user_id = result.get("id") or (user.get("id") if user else None)

    print(
        json.dumps(
            {
                "status": "ok",
                "action": action,
                "email": args.email,
                "password": args.password,
                "user_id": user_id,
            },
            ensure_ascii=False,
            indent=2,
        )
    )


if __name__ == "__main__":
    main()
