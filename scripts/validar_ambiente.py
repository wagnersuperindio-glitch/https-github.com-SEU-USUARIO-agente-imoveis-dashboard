from __future__ import annotations

import sys
from pathlib import Path


BASE_DIR = Path(__file__).resolve().parents[1]
SRC_DIR = BASE_DIR / "src"
if str(SRC_DIR) not in sys.path:
    sys.path.insert(0, str(SRC_DIR))

from agente_imoveis.integrations.gmail_client import GmailClient
from agente_imoveis.integrations.notion_client import NotionClient
from agente_imoveis.settings import load_settings


def main() -> None:
    settings = load_settings()
    settings.report_output_dir.mkdir(parents=True, exist_ok=True)

    notion = NotionClient(settings.notion_api_key)
    leiloes = notion.consultar_database(settings.notion_database_leiloes_id)
    oportunidades = notion.consultar_database(settings.notion_database_oportunidades_id)

    gmail = GmailClient(settings.gmail_sender_email, settings.gmail_app_password)

    print("Ambiente carregado com sucesso.")
    print(f"Modelo OpenAI: {settings.openai_model}")
    print(f"Database Leiloes acessivel: {len(leiloes.get('results', []))} registros lidos")
    print(
        f"Database Oportunidades acessivel: {len(oportunidades.get('results', []))} registros lidos"
    )
    print(f"Gmail configurado para envio: {gmail.sender_email}")
    print(f"Saida de relatorios: {settings.report_output_dir}")


if __name__ == "__main__":
    main()
