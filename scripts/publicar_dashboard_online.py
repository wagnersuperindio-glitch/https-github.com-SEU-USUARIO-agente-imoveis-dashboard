from __future__ import annotations

import sys
from pathlib import Path


BASE_DIR = Path(__file__).resolve().parents[1]
SRC_DIR = BASE_DIR / "src"
if str(SRC_DIR) not in sys.path:
    sys.path.insert(0, str(SRC_DIR))

from agente_imoveis.integrations.supabase_sync import (
    load_dashboard_payload,
    load_supabase_config,
    publish_dashboard_payload,
)


def main() -> None:
    payload_path = BASE_DIR / "saida" / "dashboard" / "dashboard_data.json"
    if not payload_path.exists():
        raise SystemExit(f"Arquivo nao encontrado: {payload_path}")

    config = load_supabase_config()
    if not config:
        raise SystemExit(
            "Variaveis SUPABASE_URL e SUPABASE_SERVICE_ROLE_KEY nao configuradas."
        )

    payload = load_dashboard_payload(payload_path)
    result = publish_dashboard_payload(payload, config)
    print("Dashboard publicado com sucesso no banco online.")
    print(f"Executado em: {result['executed_at'] or 'sem data de execucao'}")
    print(f"Gerado em: {result['generated_at']}")


if __name__ == "__main__":
    main()
