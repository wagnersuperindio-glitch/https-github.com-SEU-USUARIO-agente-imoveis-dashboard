from __future__ import annotations

import hashlib
import json
import secrets
import sys


def main() -> None:
    if len(sys.argv) < 4:
        print("Uso: python .\\scripts\\gerar_hash_usuario_painel.py <username> <display_name> <senha> [role]")
        raise SystemExit(1)

    username = sys.argv[1]
    display_name = sys.argv[2]
    password = sys.argv[3]
    role = sys.argv[4] if len(sys.argv) > 4 else "consulta"

    salt = secrets.token_hex(16)
    password_hash = hashlib.pbkdf2_hmac(
        "sha256",
        password.encode("utf-8"),
        salt.encode("utf-8"),
        120000,
    ).hex()

    print(
        json.dumps(
            {
                "username": username,
                "display_name": display_name,
                "role": role,
                "salt": salt,
                "password_hash": password_hash,
                "active": True,
            },
            ensure_ascii=False,
            indent=2,
        )
    )


if __name__ == "__main__":
    main()
