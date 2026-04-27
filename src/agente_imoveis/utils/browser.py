from __future__ import annotations

import subprocess
from dataclasses import dataclass
from pathlib import Path


BROWSER_CANDIDATES = [
    Path(r"C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe"),
    Path(r"C:\Program Files\Microsoft\Edge\Application\msedge.exe"),
    Path(r"C:\Program Files\Google\Chrome\Application\chrome.exe"),
]

BROWSER_STRATEGIES = {
    "default": [
        "--headless",
        "--disable-gpu",
        "--dump-dom",
    ],
    "stealth_property": [
        "--headless=new",
        "--disable-gpu",
        "--disable-blink-features=AutomationControlled",
        (
            "--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
            "AppleWebKit/537.36 (KHTML, like Gecko) "
            "Chrome/123.0.0.0 Safari/537.36"
        ),
        "--dump-dom",
    ],
}


@dataclass(slots=True)
class BrowserFetchResult:
    browser_path: str
    url: str
    stdout: str
    stderr: str
    returncode: int

    @property
    def anti_bot_reason(self) -> str:
        html = self.stdout.lower()
        if self.has_usable_content:
            return ""
        if "attention required!" in html and "cloudflare" in html:
            return "cloudflare"
        if "sorry, you have been blocked" in html:
            return "blocked"
        if "captcha" in html:
            return "captcha"
        if "access denied" in html:
            return "access_denied"
        return ""

    @property
    def has_usable_marketplace_content(self) -> bool:
        html = self.stdout.lower()
        marketplace_signals = (
            'application-name" content="facebook marketplace"',
            "marketplace_home_feed",
            "marketplacefeedgenerallistingobject",
        )
        return "facebook marketplace" in html and any(signal in html for signal in marketplace_signals)

    @property
    def has_usable_property_content(self) -> bool:
        html = self.stdout.lower()
        olx_signals = (
            'data-testid="adcard-link"',
            "olx-adcard__price",
            "olx-adcard__location",
        )
        zap_signals = (
            "https://www.zapimoveis.com.br/imovel/",
            "para comprar com",
            "tamanho do imovel",
        )
        return any(signal in html for signal in olx_signals) or any(signal in html for signal in zap_signals)

    @property
    def has_usable_content(self) -> bool:
        return self.has_usable_marketplace_content or self.has_usable_property_content


def find_browser() -> Path | None:
    for candidate in BROWSER_CANDIDATES:
        if candidate.exists():
            return candidate
    return None


def dump_dom(url: str, timeout_seconds: int = 45, strategy: str = "default") -> BrowserFetchResult:
    browser = find_browser()
    if browser is None:
        raise RuntimeError("Nenhum navegador compativel encontrado para captura browser-based.")
    browser_args = BROWSER_STRATEGIES.get(strategy)
    if browser_args is None:
        available = ", ".join(sorted(BROWSER_STRATEGIES))
        raise RuntimeError(f"Estrategia de navegador invalida: {strategy}. Disponiveis: {available}")

    process = subprocess.run(
        [
            str(browser),
            *browser_args,
            url,
        ],
        capture_output=True,
        text=True,
        encoding="utf-8",
        errors="ignore",
        timeout=timeout_seconds,
    )
    result = BrowserFetchResult(
        browser_path=str(browser),
        url=url,
        stdout=process.stdout,
        stderr=process.stderr,
        returncode=process.returncode,
    )
    if not result.stdout.strip():
        detail = result.stderr.strip() or "saida vazia"
        raise RuntimeError(f"Navegador headless sem DOM util para {url}: {detail}")
    return result
