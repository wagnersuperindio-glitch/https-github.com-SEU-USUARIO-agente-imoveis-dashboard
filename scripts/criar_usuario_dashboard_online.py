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


def build_user_metadata(
    display_name: str,
    role: str,
    cpf: str = "",
    document_type: str = "",
    document_number: str = "",
    phone: str = "",
    company_name: str = "",
) -> dict:
    metadata = {
        "display_name": display_name,
        "role": role,
    }
    if cpf:
        metadata["cpf"] = cpf
    if document_type:
        metadata["document_type"] = document_type
    if document_number:
        metadata["document_number"] = document_number
    if phone:
        metadata["phone"] = phone
    if company_name:
        metadata["company_name"] = company_name
    return metadata


def create_user(
    base_url: str,
    service_role_key: str,
    email: str,
    password: str,
    display_name: str,
    role: str,
    cpf: str = "",
    document_type: str = "",
    document_number: str = "",
    phone: str = "",
    company_name: str = "",
) -> dict:
    payload = {
        "email": email,
        "password": password,
        "email_confirm": True,
        "user_metadata": build_user_metadata(display_name, role, cpf, document_type, document_number, phone, company_name),
    }
    return _request(f"{base_url}/auth/v1/admin/users", "POST", service_role_key, payload) or {}


def update_user(
    base_url: str,
    service_role_key: str,
    user_id: str,
    password: str,
    display_name: str,
    role: str,
    cpf: str = "",
    document_type: str = "",
    document_number: str = "",
    phone: str = "",
    company_name: str = "",
) -> dict:
    payload = {
        "password": password,
        "user_metadata": build_user_metadata(display_name, role, cpf, document_type, document_number, phone, company_name),
    }
    safe_user_id = urllib.parse.quote(user_id, safe="")
    return _request(f"{base_url}/auth/v1/admin/users/{safe_user_id}", "PUT", service_role_key, payload) or {}


def main() -> None:
    parser = argparse.ArgumentParser(description="Cria ou redefine um usuario do dashboard online no Supabase.")
    parser.add_argument("--email", default="wagner.admin@superindio.local")
    parser.add_argument("--password", default="Dash#SuperIndio2026!")
    parser.add_argument("--display-name", default="Wagner Admin")
    parser.add_argument("--role", default="admin")
    parser.add_argument("--cpf", default="")
    parser.add_argument("--document-type", default="")
    parser.add_argument("--document-number", default="")
    parser.add_argument("--phone", default="")
    parser.add_argument("--company-name", default="")
    args = parser.parse_args()

    config = load_supabase_config()
    if not config:
        raise SystemExit("SUPABASE_URL e SUPABASE_SERVICE_ROLE_KEY precisam estar configurados no .env.")

    base_url = config.project_url.rstrip("/")
    user = find_user(base_url, config.service_role_key, args.email)
    if user:
        result = update_user(
            base_url,
            config.service_role_key,
            user["id"],
            args.password,
            args.display_name,
            args.role,
            args.cpf,
            args.document_type,
            args.document_number,
            args.phone,
            args.company_name,
        )
        action = "atualizado"
    else:
        result = create_user(
            base_url,
            config.service_role_key,
            args.email,
            args.password,
            args.display_name,
            args.role,
            args.cpf,
            args.document_type,
            args.document_number,
            args.phone,
            args.company_name,
        )
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
                "cpf": args.cpf,
            },
            ensure_ascii=False,
            indent=2,
        )
    )


if __name__ == "__main__":
    main()
