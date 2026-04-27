from __future__ import annotations

import hashlib
import json
import secrets
import sys
from pathlib import Path


BASE_DIR = Path(__file__).resolve().parents[1]
USERS_PATH = BASE_DIR / "config" / "painel_usuarios.json"


def hash_password(password: str, salt: str) -> str:
    return hashlib.pbkdf2_hmac(
        "sha256",
        password.encode("utf-8"),
        salt.encode("utf-8"),
        120000,
    ).hex()


def main() -> None:
    if len(sys.argv) < 3:
        print("Uso: python .\\scripts\\rotacionar_senha_usuario_painel.py <username> <nova_senha>")
        raise SystemExit(1)

    username = sys.argv[1].strip().lower()
    new_password = sys.argv[2]

    payload = json.loads(USERS_PATH.read_text(encoding="utf-8"))
    for user in payload.get("users", []):
        if user.get("username", "").lower() != username:
            continue
        salt = secrets.token_hex(16)
        user["salt"] = salt
        user["password_hash"] = hash_password(new_password, salt)
        USERS_PATH.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")
        print(f"Senha atualizada para o usuario: {user['username']}")
        return

    print(f"Usuario nao encontrado: {username}")
    raise SystemExit(2)


if __name__ == "__main__":
    main()
