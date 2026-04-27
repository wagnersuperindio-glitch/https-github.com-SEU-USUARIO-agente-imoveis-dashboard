from __future__ import annotations

import os
import threading
import webbrowser
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path


BASE_DIR = Path(__file__).resolve().parents[1]
WEB_DIR = BASE_DIR / "web" / "dashboard_online"
HOST = os.getenv("DASHBOARD_ONLINE_HOST", "127.0.0.1").strip() or "127.0.0.1"
PORT = int(os.getenv("DASHBOARD_ONLINE_PORT", "8877"))
OPEN_BROWSER = os.getenv("DASHBOARD_ONLINE_OPEN_BROWSER", "1").strip() not in {"0", "false", "False"}


class OnlinePreviewHandler(SimpleHTTPRequestHandler):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, directory=str(WEB_DIR), **kwargs)


def main() -> None:
    WEB_DIR.mkdir(parents=True, exist_ok=True)
    server = ThreadingHTTPServer((HOST, PORT), OnlinePreviewHandler)
    url = f"http://{HOST}:{PORT}"
    print(f"Preview do dashboard online disponivel em {url}")
    if OPEN_BROWSER:
        threading.Timer(1.0, lambda: webbrowser.open(url)).start()
    server.serve_forever()


if __name__ == "__main__":
    main()
