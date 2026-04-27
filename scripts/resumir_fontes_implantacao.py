from __future__ import annotations

import json
from pathlib import Path


BASE_DIR = Path(__file__).resolve().parents[1]
CONFIG_PATH = BASE_DIR / "config" / "fontes_implantacao_v1.json"


def main() -> None:
    data = json.loads(CONFIG_PATH.read_text(encoding="utf-8"))
    print("Plano de implantacao de fontes")
    print(f"MVP imediato: {len(data['mvp_imediato'])} fontes")
    print(f"Segunda onda: {len(data['segunda_onda'])} fontes")
    print(f"Fontes especiais: {len(data['fontes_especiais'])} fontes")
    print("")
    print("Top do MVP:")
    for nome in data["mvp_imediato"][:10]:
        print(f"- {nome}")


if __name__ == "__main__":
    main()
