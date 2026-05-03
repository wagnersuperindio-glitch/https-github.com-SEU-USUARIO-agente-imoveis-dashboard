from __future__ import annotations

import subprocess
import sys
from pathlib import Path


BASE_DIR = Path(__file__).resolve().parents[1]


def run_step(label: str, command: list[str]) -> None:
    print(f"[rotina] {label}")
    subprocess.run(command, cwd=BASE_DIR, check=True)


def main() -> None:
    python = sys.executable
    run_step("coleta MVP", [python, r".\scripts\executar_coleta_mvp.py"])
    run_step("inteligencia operacional", [python, r".\scripts\gerar_inteligencia_operacional.py"])
    run_step("dashboard local", [python, r".\scripts\gerar_dashboard_data.py"])
    run_step("relatorio imobiliario", [python, r".\scripts\gerar_relatorio_imobiliario.py"])
    run_step("publicacao online", [python, r".\scripts\publicar_dashboard_online.py"])
    print("[rotina] concluida com sucesso")


if __name__ == "__main__":
    main()
