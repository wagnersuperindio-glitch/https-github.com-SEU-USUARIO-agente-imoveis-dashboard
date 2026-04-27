from __future__ import annotations

import sys
from pathlib import Path


BASE_DIR = Path(__file__).resolve().parents[1]
SRC_DIR = BASE_DIR / "src"
if str(SRC_DIR) not in sys.path:
    sys.path.insert(0, str(SRC_DIR))

from agente_imoveis.capture.mvp_capture_plan import build_mvp_connectors


def main() -> None:
    connectors = build_mvp_connectors()
    print("Arquitetura MVP - conectores previstos")
    print(f"Total de conectores no MVP imediato: {len(connectors)}")
    print("")
    for connector in connectors:
        status = connector.healthcheck()
        print(f"- {status['source']} -> {status['connector']} [{status['status']}]")


if __name__ == "__main__":
    main()
