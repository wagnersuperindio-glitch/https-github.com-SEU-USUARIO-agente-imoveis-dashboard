from __future__ import annotations

from dataclasses import dataclass
import ssl
from typing import Any
from urllib.error import HTTPError, URLError
from urllib.parse import urlencode
from urllib.request import Request, urlopen


DEFAULT_HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/123.0.0.0 Safari/537.36"
    ),
    "Accept-Language": "pt-BR,pt;q=0.9,en-US;q=0.8,en;q=0.7",
}


@dataclass(slots=True)
class HttpFetchResult:
    url: str
    status_code: int
    text: str
    headers: dict[str, Any]


def fetch_text(url: str, method: str = "GET", data: dict[str, Any] | None = None) -> HttpFetchResult:
    encoded_data = None
    if data:
        encoded_data = urlencode(data).encode("utf-8")

    request = Request(
        url=url,
        headers=DEFAULT_HEADERS,
        data=encoded_data,
        method=method.upper(),
    )
    ssl_context = ssl.create_default_context()

    try:
        with urlopen(request, timeout=40, context=ssl_context) as response:
            body = response.read().decode("utf-8", errors="ignore")
            headers = dict(response.info().items())
            status_code = getattr(response, "status", 200)
            final_url = getattr(response, "url", url)
    except HTTPError as exc:
        body = exc.read().decode("utf-8", errors="ignore")
        raise RuntimeError(f"HTTP {exc.code} ao acessar {url}") from exc
    except URLError as exc:
        raise RuntimeError(f"Falha de rede ao acessar {url}: {exc.reason}") from exc

    return HttpFetchResult(
        url=final_url,
        status_code=status_code,
        text=body,
        headers=headers,
    )
