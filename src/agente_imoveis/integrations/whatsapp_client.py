from __future__ import annotations

from typing import Any

import requests


class WhatsAppClient:
    def __init__(self, provider: str, base_url: str, api_token: str) -> None:
        self.provider = provider
        self.base_url = base_url.rstrip("/")
        self.api_token = api_token

    def enviar_texto(self, numero: str, mensagem: str) -> dict[str, Any]:
        if not self.base_url or not self.api_token:
            raise RuntimeError("WhatsApp nao configurado.")

        payload = {"number": numero, "text": mensagem}
        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {self.api_token}",
        }

        response = requests.post(
            f"{self.base_url}/message/sendText",
            headers=headers,
            json=payload,
            timeout=30,
        )
        response.raise_for_status()
        return response.json()
