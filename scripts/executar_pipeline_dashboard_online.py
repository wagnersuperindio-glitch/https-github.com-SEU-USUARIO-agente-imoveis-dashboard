from __future__ import annotations

import subprocess
import sys
from pathlib import Path


BASE_DIR = Path(__file__).resolve().parents[1]


def run_step(label: str, command: list[str]) -> None:
    print(f"[pipeline] {label}")
    subprocess.run(command, cwd=BASE_DIR, check=True)


def main() -> None:
    python = sys.executable
    run_step("gerando dashboard local", [python, r".\scripts\gerar_dashboard_data.py"])
    run_step("tentando publicar dashboard online", [python, r".\scripts\publicar_dashboard_online.py"])
    print("[pipeline] concluido com sucesso")


if __name__ == "__main__":
    main()
