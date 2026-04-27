from __future__ import annotations

import json
import sys
from pathlib import Path


BASE_DIR = Path(__file__).resolve().parents[1]
SRC_DIR = BASE_DIR / "src"
if str(SRC_DIR) not in sys.path:
    sys.path.insert(0, str(SRC_DIR))

from agente_imoveis.dashboard import build_dashboard_payload


def main() -> None:
    target_dir = BASE_DIR / "saida" / "dashboard"
    target_dir.mkdir(parents=True, exist_ok=True)
    payload = build_dashboard_payload()
    target = target_dir / "dashboard_data.json"
    target.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"Dashboard data gerado: {target}")


if __name__ == "__main__":
    main()
