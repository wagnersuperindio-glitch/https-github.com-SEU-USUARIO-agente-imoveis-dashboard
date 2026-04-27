from __future__ import annotations

from typing import Any

import requests


class NotionClient:
    def __init__(self, api_key: str) -> None:
        self.api_key = api_key
        self.base_url = "https://api.notion.com/v1"
        self.headers = {
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json",
            "Notion-Version": "2022-06-28",
        }

    def consultar_database(self, database_id: str) -> dict[str, Any]:
        response = requests.post(
            f"{self.base_url}/databases/{database_id}/query",
            headers=self.headers,
            json={},
            timeout=30,
        )
        response.raise_for_status()
        return response.json()

    def criar_pagina(self, database_id: str, properties: dict[str, Any]) -> dict[str, Any]:
        payload = {
            "parent": {"database_id": database_id},
            "properties": properties,
        }
        response = requests.post(
            f"{self.base_url}/pages",
            headers=self.headers,
            json=payload,
            timeout=30,
        )
        response.raise_for_status()
        return response.json()
