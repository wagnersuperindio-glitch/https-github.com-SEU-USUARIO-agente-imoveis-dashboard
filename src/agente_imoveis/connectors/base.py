from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Any

from agente_imoveis.models import SourceDefinition
from agente_imoveis.storage.capture_store import save_raw_capture
from agente_imoveis.utils.http import fetch_text


class BaseConnector(ABC):
    connector_name = "base"

    def __init__(self, source: SourceDefinition) -> None:
        self.source = source

    @abstractmethod
    def collect(self) -> list[SourceRecord]:
        """Collect raw or normalized records from the source."""

    def fetch_page(self, url: str | None = None, method: str = "GET", data: dict[str, Any] | None = None) -> str:
        target_url = url or self.source.url
        result = fetch_text(target_url, method=method, data=data)
        save_raw_capture(self.source.nome, result.text)
        return result.text

    def healthcheck(self) -> dict[str, str]:
        return {
            "connector": self.connector_name,
            "source": self.source.nome,
            "status": "configured",
        }
