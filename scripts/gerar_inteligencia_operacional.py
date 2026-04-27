from __future__ import annotations

import json
import sys
from pathlib import Path


BASE_DIR = Path(__file__).resolve().parents[1]
SRC_DIR = BASE_DIR / "src"
if str(SRC_DIR) not in sys.path:
    sys.path.insert(0, str(SRC_DIR))

from agente_imoveis.models import SourceRecord
from agente_imoveis.processing.intelligence import enrich_records, save_intelligence_payload
from agente_imoveis.storage.capture_store import EXECUTION_DIR


def _latest_summary_path() -> Path:
    files = sorted(EXECUTION_DIR.glob("*_resumo_execucao_mvp.json"))
    if not files:
        raise RuntimeError("Nenhuma execução do MVP encontrada para gerar inteligência.")
    return files[-1]


def main() -> None:
    summary = json.loads(_latest_summary_path().read_text(encoding="utf-8"))
    records: list[SourceRecord] = []
    for item in summary.get("results", []):
        output_path = item.get("output_path", "").strip()
        if not output_path:
            continue
        payload = json.loads(Path(output_path).read_text(encoding="utf-8"))
        records.extend(SourceRecord(**row) for row in payload)

    enriched = enrich_records(records)
    target = save_intelligence_payload(enriched, executed_at=summary.get("executed_at"))
    print(f"Inteligência operacional gerada: {target}")
    print(f"Registros enriquecidos: {len(enriched)}")
    print(f"No radar: {sum(1 for item in enriched if item.radar_match)}")


if __name__ == "__main__":
    main()
