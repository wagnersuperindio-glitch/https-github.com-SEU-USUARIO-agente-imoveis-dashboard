from __future__ import annotations

import sys
from pathlib import Path


BASE_DIR = Path(__file__).resolve().parents[1]
SRC_DIR = BASE_DIR / "src"
if str(SRC_DIR) not in sys.path:
    sys.path.insert(0, str(SRC_DIR))

from agente_imoveis.capture.run_mvp_capture import execute_mvp_capture


def main() -> None:
    result = execute_mvp_capture()
    payloads = result["records"]
    summary = result["summary"]
    print("Coleta MVP executada.")
    print(f"Conectores executados: {summary['connectors_total']}")
    print(f"Sucesso: {summary['connectors_success']}")
    print(f"Falha: {summary['connectors_error']}")
    print(f"Registros normalizados gerados: {len(payloads)}")
    print("Saidas:")
    print(f"- Capturas brutas: {BASE_DIR / 'saida' / 'capturas_brutas'}")
    print(f"- Capturas normalizadas: {BASE_DIR / 'saida' / 'capturas_normalizadas'}")
    print(f"- Resumo de execucao: {summary['summary_path']}")


if __name__ == "__main__":
    main()
