from __future__ import annotations

import os
from dataclasses import dataclass
from pathlib import Path


BASE_DIR = Path(__file__).resolve().parents[2]


def _read_env_file(env_path: Path) -> None:
    if not env_path.exists():
        return

    for raw_line in env_path.read_text(encoding="utf-8").splitlines():
        line = raw_line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, value = line.split("=", 1)
        os.environ.setdefault(key.strip(), value.strip())


def _required(name: str) -> str:
    value = os.getenv(name, "").strip()
    if not value:
        raise RuntimeError(f"Variavel obrigatoria ausente: {name}")
    return value


_read_env_file(BASE_DIR / ".env")


@dataclass(frozen=True)
class Settings:
    openai_api_key: str
    openai_model: str
    notion_api_key: str
    notion_database_leiloes_id: str
    notion_database_oportunidades_id: str
    gmail_sender_email: str
    gmail_app_password: str
    whatsapp_provider: str
    whatsapp_base_url: str
    whatsapp_api_token: str
    whatsapp_target_phone: str
    report_output_dir: Path
    log_level: str


def load_settings() -> Settings:
    return Settings(
        openai_api_key=_required("OPENAI_API_KEY"),
        openai_model=os.getenv("OPENAI_MODEL", "gpt-4.1").strip(),
        notion_api_key=_required("NOTION_API_KEY"),
        notion_database_leiloes_id=_required("NOTION_DATABASE_LEILOES_ID"),
        notion_database_oportunidades_id=_required("NOTION_DATABASE_OPORTUNIDADES_ID"),
        gmail_sender_email=_required("GMAIL_SENDER_EMAIL"),
        gmail_app_password=_required("GMAIL_APP_PASSWORD"),
        whatsapp_provider=os.getenv("WHATSAPP_PROVIDER", "").strip(),
        whatsapp_base_url=os.getenv("WHATSAPP_BASE_URL", "").strip(),
        whatsapp_api_token=os.getenv("WHATSAPP_API_TOKEN", "").strip(),
        whatsapp_target_phone=os.getenv("WHATSAPP_TARGET_PHONE", "").strip(),
        report_output_dir=BASE_DIR / os.getenv("REPORT_OUTPUT_DIR", r"saida\relatorios"),
        log_level=os.getenv("LOG_LEVEL", "INFO").strip(),
    )
