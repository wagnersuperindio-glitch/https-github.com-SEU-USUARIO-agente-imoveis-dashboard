from __future__ import annotations

from agente_imoveis.connectors.base import BaseConnector
from agente_imoveis.storage.capture_store import save_raw_capture
from agente_imoveis.utils.browser import dump_dom


class BrowserBackedConnector(BaseConnector):
    anti_bot_mode = "browser_headless"

    def fetch_page_with_browser(self, url: str | None = None, strategy: str = "default") -> str:
        target_url = url or self.source.url
        result = dump_dom(target_url, strategy=strategy)
        save_raw_capture(self.source.nome, result.stdout, suffix="browser.html")
        if result.anti_bot_reason:
            raise RuntimeError(
                f"Bloqueio anti-bot detectado em {self.source.nome} via navegador: {result.anti_bot_reason}"
            )
        return result.stdout
