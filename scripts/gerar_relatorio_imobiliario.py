from __future__ import annotations

import json
from collections import Counter, defaultdict
from datetime import datetime
from pathlib import Path


BASE_DIR = Path(__file__).resolve().parents[1]
OUTPUT_DIR = BASE_DIR / "saida"
REPORT_DIR = OUTPUT_DIR / "relatorios"
EXECUTION_DIR = OUTPUT_DIR / "execucoes"
INTELLIGENCE_PATH = OUTPUT_DIR / "inteligencia" / "oportunidades_inteligencia.json"


def _format_currency(value: float | None) -> str:
    if value is None:
        return "-"
    inteiro = f"{value:,.2f}"
    return f"R$ {inteiro}".replace(",", "X").replace(".", ",").replace("X", ".")


def _format_datetime(value: str) -> str:
    if not value:
        return "-"
    try:
        return datetime.fromisoformat(value).strftime("%d/%m/%Y %H:%M")
    except ValueError:
        return value


def _load_json(path: Path) -> dict | list:
    return json.loads(path.read_text(encoding="utf-8"))


def load_latest_execution_summary() -> dict:
    if not EXECUTION_DIR.exists():
        return {}
    files = sorted(EXECUTION_DIR.glob("*_resumo_execucao_mvp.json"))
    if not files:
        return {}
    payload = _load_json(files[-1])
    payload["path"] = str(files[-1])
    return payload


def load_intelligence_payload() -> dict:
    if not INTELLIGENCE_PATH.exists():
        return {}
    payload = _load_json(INTELLIGENCE_PATH)
    payload["path"] = str(INTELLIGENCE_PATH)
    return payload


def _weekly_window_lines(weekly_window: dict) -> list[str]:
    summary = weekly_window.get("summary", {})
    baseline = weekly_window.get("baseline_snapshot", {})
    lines = [
        "### Janela semanal travada",
        "",
        f"- Semana de referencia: {_format_datetime(weekly_window.get('week_start', ''))}",
        f"- Base comparativa: {_format_datetime(baseline.get('executed_at', ''))}",
        f"- O que entrou desde a ultima segunda: {summary.get('entered_total', 0)} ativos",
        f"- O que mudou desde a ultima segunda: {summary.get('changed_total', 0)} ativos",
        f"- O que saiu desde a ultima segunda: {summary.get('exited_total', 0)} ativos",
        "",
    ]

    def sort_priority(item: dict) -> tuple:
        radar_match = item.get("radar_match", False)
        state = item.get("state", "")
        score = item.get("investment_score", 0)
        decision = item.get("investment_decision", "")
        return (
            0 if radar_match else 1,
            0 if state == "RS" else 1,
            0 if decision == "Atacar Agora" else 1,
            -score,
        )

    entered = sorted(weekly_window.get("entered", []), key=sort_priority)[:8]
    changed = sorted((item.get("current", {}) | {"_fields_changed": item.get("fields_changed", []), "_previous": item.get("previous", {})} for item in weekly_window.get("changed", [])), key=sort_priority)[:8]
    exited = sorted(weekly_window.get("exited", []), key=sort_priority)[:8]

    lines.extend(["### Entradas da semana", ""])
    if entered:
        for item in entered:
            lines.append(
                f"- {item.get('city', '-')}/"
                f"{item.get('state', '-')} | {item.get('source_name', '-')} | "
                f"{item.get('title', '-')[:120]} | {item.get('investment_decision', '-')} | "
                f"{_format_currency(item.get('price'))}"
            )
    else:
        lines.append("- Nenhuma entrada nova identificada na janela semanal.")

    lines.extend(["", "### Mudancas da semana", ""])
    if changed:
        for item in changed:
            current = item
            previous = item.get("_previous", {})
            fields = ", ".join(item.get("_fields_changed", [])) or "-"
            lines.append(
                f"- {current.get('city', '-')}/{current.get('state', '-')} | "
                f"{current.get('title', '-')[:100]} | mudou: {fields} | "
                f"preco {_format_currency(previous.get('price'))} -> {_format_currency(current.get('price'))} | "
                f"decisao {previous.get('decision', '-')} -> {current.get('decision', '-')}"
            )
    else:
        lines.append("- Nenhuma mudanca relevante identificada na janela semanal.")

    lines.extend(["", "### Saidas da semana", ""])
    if exited:
        for item in exited:
            lines.append(
                f"- {item.get('city', '-')}/{item.get('state', '-')} | "
                f"{item.get('source_name', '-')} | {item.get('title', '-')[:120]} | "
                f"{_format_currency(item.get('price'))}"
            )
    else:
        lines.append("- Nenhuma saida identificada na janela semanal.")

    return lines


def _city_radar_lines(records: list[dict]) -> list[str]:
    grouped: dict[str, list[dict]] = defaultdict(list)
    for record in records:
        if not record.get("radar_match"):
            continue
        city_key = f"{record.get('city', '-')}/{record.get('state', '-')}"
        grouped[city_key].append(record)

    lines = ["## Cidades do radar", ""]
    if not grouped:
        lines.append("- Nenhum ativo do radar foi identificado na base atual.")
        return lines

    for city_key in sorted(grouped):
        items = sorted(grouped[city_key], key=lambda item: (-item.get("investment_score", 0), item.get("source_name", "")))
        decision_counter = Counter(item.get("investment_decision", "-") for item in items)
        top_sources = Counter(item.get("source_name", "-") for item in items).most_common(3)
        avg_score = round(sum(item.get("investment_score", 0) for item in items) / len(items), 2)
        lines.extend(
            [
                f"### {city_key}",
                "",
                f"- Ativos no radar: {len(items)}",
                f"- Score de investimento medio: {avg_score}",
                f"- Breakdown de decisao de investimento: {', '.join(f'{key}: {value}' for key, value in sorted(decision_counter.items()))}",
                f"- Fontes mais presentes: {', '.join(f'{source} ({count})' for source, count in top_sources)}",
                "",
            ]
        )

    return lines


def _attack_lines(records: list[dict]) -> list[str]:
    candidates = [
        record
        for record in records
        if record.get("investment_decision") in {"Atacar Agora", "Aprofundar Analise"} or record.get("radar_match")
    ]
    candidates.sort(
        key=lambda item: (
            0 if item.get("investment_decision") == "Atacar Agora" else 1,
            0 if item.get("radar_match") else 1,
            -item.get("investment_score", 0),
        )
    )
    lines = ["## Oportunidades de ataque", ""]
    if not candidates:
        lines.append("- Nenhuma oportunidade de ataque foi classificada nesta rodada.")
        return lines

    for item in candidates[:15]:
        discount_label = f"{item.get('discount_vs_comparable_pct'):.1f}%" if item.get("discount_vs_comparable_pct") is not None else "-"
        lines.append(
            f"- {item.get('city', '-')}/{item.get('state', '-')} | {item.get('source_name', '-')} | "
            f"{item.get('title', '-')[:120]} | inv {item.get('investment_score', 0)} | "
            f"{item.get('investment_decision', '-')} | desc {discount_label} | "
            f"{_format_currency(item.get('price'))} | {item.get('link', '-')}"
        )
    return lines


def build_report() -> str:
    execution_summary = load_latest_execution_summary()
    intelligence = load_intelligence_payload()
    generated_at = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    records = intelligence.get("records", [])
    history = intelligence.get("history", {})
    weekly_window_meta = history.get("weekly_window", {})
    weekly_window = _load_json(Path(weekly_window_meta["path"])) if weekly_window_meta.get("path") else {}

    success_sources = [item for item in execution_summary.get("results", []) if item.get("status") == "success"]
    error_sources = [item for item in execution_summary.get("results", []) if item.get("status") == "error"]
    source_counter = Counter(item.get("source_name", "-") for item in records)

    lines = [
        "# Relatorio Operacional do Agente Imobiliario",
        "",
        f"- Gerado em: {generated_at}",
        f"- Ultima execucao: {_format_datetime(execution_summary.get('executed_at', ''))}",
        f"- Resumo operacional: {execution_summary.get('path', '-')}",
        f"- Base de inteligencia: {intelligence.get('path', '-')}",
        "",
        "## Panorama geral",
        "",
        f"- Conectores previstos: {execution_summary.get('connectors_total', 0)}",
        f"- Fontes com sucesso: {execution_summary.get('connectors_success', 0)}",
        f"- Fontes com erro: {execution_summary.get('connectors_error', 0)}",
        f"- Ativos enriquecidos na inteligencia: {len(records)}",
        f"- Ativos no radar: {sum(1 for item in records if item.get('radar_match'))}",
        f"- Ativos no RS: {sum(1 for item in records if item.get('state') == 'RS')}",
        f"- Ativos em ataque imediato operacional: {sum(1 for item in records if item.get('decision') == 'Atacar Agora')}",
        f"- Ativos em ataque imediato de investimento: {sum(1 for item in records if item.get('investment_decision') == 'Atacar Agora')}",
        f"- Principais fontes ativas: {', '.join(f'{name} ({count})' for name, count in source_counter.most_common(5))}",
        "",
    ]

    if error_sources:
        lines.extend(["### Fontes com tratamento especial", ""])
        for item in error_sources:
            lines.append(f"- {item.get('source_name', '-')} | {item.get('error', '-')}")
        lines.append("")

    lines.extend(_weekly_window_lines(weekly_window))
    lines.append("")
    lines.extend(_city_radar_lines(records))
    lines.append("")
    lines.extend(_attack_lines(records))
    lines.extend(
        [
            "",
            "## Governanca da entrega",
            "",
            "- O relatorio segue estruturado para painel web, Notion e Gmail.",
            "- O historico por ativo agora cria snapshot por execucao e comparativo semanal.",
            "- A janela semanal passa a responder o que entrou, o que mudou e o que saiu desde a base anterior.",
            "",
            "## Recomendacao executiva",
            "",
            "- Usar o panorama geral para governanca da operacao.",
            "- Usar o bloco de cidades do radar para alinhamento geografico e expansao.",
            "- Usar o bloco de oportunidades de ataque para decisao comercial e de capital.",
        ]
    )
    return "\n".join(lines) + "\n"


def main() -> None:
    REPORT_DIR.mkdir(parents=True, exist_ok=True)
    report = build_report()
    file_name = f"relatorio_{datetime.now().strftime('%Y-%m-%d_%H-%M-%S')}.md"
    target = REPORT_DIR / file_name
    target.write_text(report, encoding="utf-8")
    print(f"Relatorio gerado: {target}")


if __name__ == "__main__":
    main()
