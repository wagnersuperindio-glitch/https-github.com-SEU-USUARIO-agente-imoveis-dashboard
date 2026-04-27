from __future__ import annotations

from dataclasses import asdict
from datetime import datetime

from agente_imoveis.capture.mvp_capture_plan import build_mvp_connectors
from agente_imoveis.processing.filters import deduplicate_records, record_has_minimum_data
from agente_imoveis.storage.capture_store import save_execution_summary, save_records


def execute_mvp_capture() -> dict:
    all_payloads: list[dict] = []
    connector_results: list[dict] = []
    connectors = build_mvp_connectors()

    for connector in connectors:
        try:
            records = connector.collect()
            filtered = [record for record in records if record_has_minimum_data(record)]
            unique = deduplicate_records(filtered)
            output_path = save_records(connector.source.nome, unique)
            all_payloads.extend(asdict(record) for record in unique)
            connector_results.append(
                {
                    "source_name": connector.source.nome,
                    "connector_name": connector.connector_name,
                    "status": "success",
                    "records_collected": len(records),
                    "records_filtered": len(filtered),
                    "records_unique": len(unique),
                    "output_path": str(output_path),
                    "error": "",
                }
            )
        except Exception as exc:
            connector_results.append(
                {
                    "source_name": connector.source.nome,
                    "connector_name": connector.connector_name,
                    "status": "error",
                    "records_collected": 0,
                    "records_filtered": 0,
                    "records_unique": 0,
                    "output_path": "",
                    "error": str(exc),
                }
            )

    summary = {
        "executed_at": datetime.now().isoformat(timespec="seconds"),
        "connectors_total": len(connectors),
        "connectors_success": sum(1 for item in connector_results if item["status"] == "success"),
        "connectors_error": sum(1 for item in connector_results if item["status"] == "error"),
        "records_total": len(all_payloads),
        "results": connector_results,
    }
    summary_path = save_execution_summary(summary)
    summary["summary_path"] = str(summary_path)
    return {
        "records": all_payloads,
        "summary": summary,
    }
