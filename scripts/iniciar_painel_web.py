from __future__ import annotations

import hashlib
import hmac
import json
import os
import secrets
import socket
import ssl
import sys
import threading
import webbrowser
from datetime import datetime, timedelta, timezone
from http import HTTPStatus
from http.cookies import SimpleCookie
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib.parse import urlparse


BASE_DIR = Path(__file__).resolve().parents[1]
SRC_DIR = BASE_DIR / "src"
if str(SRC_DIR) not in sys.path:
    sys.path.insert(0, str(SRC_DIR))

from agente_imoveis.dashboard import build_dashboard_payload


WEB_DIR = BASE_DIR / "web" / "dashboard"
CONFIG_DIR = BASE_DIR / "config"
USERS_PATH = CONFIG_DIR / "painel_usuarios.json"
HOST = os.getenv("PAINEL_HOST", "0.0.0.0").strip() or "0.0.0.0"
PORT = int(os.getenv("PAINEL_PORT", "8765"))
OPEN_BROWSER = os.getenv("PAINEL_OPEN_BROWSER", "1").strip() not in {"0", "false", "False"}
SESSION_TTL_HOURS = int(os.getenv("PAINEL_SESSION_TTL_HOURS", "12"))
SSL_CERT_PATH = os.getenv("PAINEL_SSL_CERT", "").strip()
SSL_KEY_PATH = os.getenv("PAINEL_SSL_KEY", "").strip()

ROLE_PERMISSIONS = {
    "admin": ["dashboard:view", "users:manage", "reports:view"],
    "diretoria": ["dashboard:view", "reports:view"],
    "analista": ["dashboard:view"],
    "consulta": ["dashboard:view"],
}

SESSIONS: dict[str, dict] = {}


def _discover_lan_ip() -> str:
    try:
        with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as sock:
            sock.connect(("8.8.8.8", 80))
            return sock.getsockname()[0]
    except OSError:
        try:
            return socket.gethostbyname(socket.gethostname())
        except OSError:
            return "127.0.0.1"


def _users_config() -> dict:
    if not USERS_PATH.exists():
        return {"users": []}
    return json.loads(USERS_PATH.read_text(encoding="utf-8"))


def _hash_password(password: str, salt: str) -> str:
    raw = hashlib.pbkdf2_hmac("sha256", password.encode("utf-8"), salt.encode("utf-8"), 120000)
    return raw.hex()


def _cookie_session_id(headers) -> str:
    cookie_header = headers.get("Cookie", "")
    cookie = SimpleCookie()
    cookie.load(cookie_header)
    morsel = cookie.get("painel_session")
    return morsel.value if morsel else ""


def _session_cookie(session_id: str, secure: bool) -> str:
    parts = [
        f"painel_session={session_id}",
        "Path=/",
        "HttpOnly",
        "SameSite=Lax",
        f"Max-Age={SESSION_TTL_HOURS * 3600}",
    ]
    if secure:
        parts.append("Secure")
    return "; ".join(parts)


def _clear_session_cookie(secure: bool) -> str:
    parts = [
        "painel_session=",
        "Path=/",
        "HttpOnly",
        "SameSite=Lax",
        "Max-Age=0",
    ]
    if secure:
        parts.append("Secure")
    return "; ".join(parts)


def _authenticate_user(username: str, password: str) -> dict | None:
    config = _users_config()
    for user in config.get("users", []):
        if user.get("username", "").lower() != username.lower():
            continue
        if not user.get("active", True):
            return None
        salt = user.get("salt", "")
        expected = user.get("password_hash", "")
        provided = _hash_password(password, salt)
        if hmac.compare_digest(provided, expected):
            return user
        return None
    return None


def _create_session(user: dict) -> str:
    session_id = secrets.token_urlsafe(32)
    expires_at = datetime.now(timezone.utc) + timedelta(hours=SESSION_TTL_HOURS)
    SESSIONS[session_id] = {
        "user": {
            "username": user.get("username", ""),
            "display_name": user.get("display_name", user.get("username", "")),
            "role": user.get("role", "consulta"),
            "permissions": ROLE_PERMISSIONS.get(user.get("role", "consulta"), ["dashboard:view"]),
        },
        "expires_at": expires_at,
    }
    return session_id


def _get_session(headers) -> dict | None:
    session_id = _cookie_session_id(headers)
    if not session_id:
        return None
    session = SESSIONS.get(session_id)
    if not session:
        return None
    if session["expires_at"] <= datetime.now(timezone.utc):
        SESSIONS.pop(session_id, None)
        return None
    return {"id": session_id, **session}


def _network_urls(host: str, port: int) -> tuple[str, str]:
    scheme = "https" if SSL_CERT_PATH and SSL_KEY_PATH else "http"
    local_display_host = "127.0.0.1" if host == "0.0.0.0" else host
    local_url = f"{scheme}://{local_display_host}:{port}"
    network_url = f"{scheme}://{LAN_IP}:{port}"
    return local_url, network_url


LAN_IP = _discover_lan_ip()


class DashboardHandler(SimpleHTTPRequestHandler):
    server_version = "PainelExecutivo/2.0"

    def __init__(self, *args, **kwargs):
        super().__init__(*args, directory=str(WEB_DIR), **kwargs)

    def _is_secure(self) -> bool:
        return bool(SSL_CERT_PATH and SSL_KEY_PATH)

    def _send_json(self, payload: dict, status: HTTPStatus = HTTPStatus.OK, cookie: str | None = None) -> None:
        body = json.dumps(payload, ensure_ascii=False).encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Cache-Control", "no-store")
        self.send_header("Content-Length", str(len(body)))
        if cookie:
            self.send_header("Set-Cookie", cookie)
        self.end_headers()
        self.wfile.write(body)

    def _read_json(self) -> dict:
        content_length = int(self.headers.get("Content-Length", "0") or "0")
        raw = self.rfile.read(content_length) if content_length else b"{}"
        return json.loads(raw.decode("utf-8") or "{}")

    def _session_required(self) -> dict | None:
        session = _get_session(self.headers)
        if not session:
            self._send_json(
                {
                    "error": "Nao autenticado",
                    "message": "Entre com usuario e senha para acessar o painel corporativo.",
                },
                status=HTTPStatus.UNAUTHORIZED,
            )
            return None
        return session

    def _handle_login(self) -> None:
        payload = self._read_json()
        username = str(payload.get("username", "")).strip()
        password = str(payload.get("password", "")).strip()
        if not username or not password:
            self._send_json(
                {"error": "Credenciais invalidas", "message": "Informe usuario e senha."},
                status=HTTPStatus.BAD_REQUEST,
            )
            return

        user = _authenticate_user(username, password)
        if not user:
            self._send_json(
                {"error": "Acesso negado", "message": "Usuario ou senha invalidos."},
                status=HTTPStatus.UNAUTHORIZED,
            )
            return

        session_id = _create_session(user)
        self._send_json(
            {
                "authenticated": True,
                "user": {
                    "username": user.get("username", ""),
                    "display_name": user.get("display_name", user.get("username", "")),
                    "role": user.get("role", "consulta"),
                    "permissions": ROLE_PERMISSIONS.get(user.get("role", "consulta"), ["dashboard:view"]),
                },
            },
            cookie=_session_cookie(session_id, self._is_secure()),
        )

    def _handle_logout(self) -> None:
        session_id = _cookie_session_id(self.headers)
        if session_id:
            SESSIONS.pop(session_id, None)
        self._send_json({"authenticated": False}, cookie=_clear_session_cookie(self._is_secure()))

    def _handle_session(self) -> None:
        session = _get_session(self.headers)
        if not session:
            self._send_json({"authenticated": False, "user": None}, status=HTTPStatus.UNAUTHORIZED)
            return
        self._send_json({"authenticated": True, "user": session["user"]})

    def do_POST(self) -> None:
        parsed = urlparse(self.path)
        if parsed.path == "/api/auth/login":
            self._handle_login()
            return
        if parsed.path == "/api/auth/logout":
            self._handle_logout()
            return
        self._send_json({"error": "Nao encontrado"}, status=HTTPStatus.NOT_FOUND)

    def do_GET(self) -> None:
        parsed = urlparse(self.path)

        if parsed.path == "/api/auth/session":
            self._handle_session()
            return

        if parsed.path == "/api/dashboard":
            session = self._session_required()
            if not session:
                return
            local_url, network_url = _network_urls(HOST, PORT)
            payload = build_dashboard_payload()
            payload["access"] = {
                "host": HOST,
                "port": PORT,
                "local_url": local_url,
                "network_url": network_url,
                "access_mode": "autenticado por usuario",
                "access_key_enabled": False,
                "https_enabled": self._is_secure(),
            }
            payload["auth"] = {
                "authenticated": True,
                "user": session["user"],
            }
            self._send_json(payload)
            return

        if parsed.path in {"/", "/index.html"}:
            self.path = "/index.html"
        super().do_GET()


def _wrap_server_with_ssl(server: ThreadingHTTPServer) -> ThreadingHTTPServer:
    if not (SSL_CERT_PATH and SSL_KEY_PATH):
        return server
    context = ssl.SSLContext(ssl.PROTOCOL_TLS_SERVER)
    context.load_cert_chain(certfile=SSL_CERT_PATH, keyfile=SSL_KEY_PATH)
    server.socket = context.wrap_socket(server.socket, server_side=True)
    return server


def main() -> None:
    WEB_DIR.mkdir(parents=True, exist_ok=True)
    server = ThreadingHTTPServer((HOST, PORT), DashboardHandler)
    server = _wrap_server_with_ssl(server)

    local_url, network_url = _network_urls(HOST, PORT)

    print(f"Painel web corporativo disponivel em {local_url}")
    if LAN_IP and "127.0.0.1" not in network_url:
        print(f"Acesso pela rede interna: {network_url}")
    print("Painel com autenticacao por usuario e sessao.")
    if SSL_CERT_PATH and SSL_KEY_PATH:
        print("HTTPS habilitado com certificado configurado.")
    else:
        print("HTTPS ainda nao habilitado. Configure certificado para uso corporativo completo.")

    if OPEN_BROWSER:
        threading.Timer(1.0, lambda: webbrowser.open(local_url)).start()

    server.serve_forever()


if __name__ == "__main__":
    main()
