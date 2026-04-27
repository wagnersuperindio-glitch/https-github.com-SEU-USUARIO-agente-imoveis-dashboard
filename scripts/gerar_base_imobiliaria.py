import csv
import json
import unicodedata
from collections import Counter
from datetime import datetime
from pathlib import Path


BASE_DIR = Path(__file__).resolve().parents[1]
CONFIG_DIR = BASE_DIR / "config"
OUTPUT_DIR = BASE_DIR / "saida"


def load_json(path: Path):
    with path.open("r", encoding="utf-8") as file:
        return json.load(file)


def normalize_text(value: str) -> str:
    normalized = unicodedata.normalize("NFKD", value)
    return "".join(char for char in normalized if not unicodedata.combining(char))


def slug_city(city_name: str) -> str:
    return normalize_text(city_name).lower().replace(" ", "-")


def classify_default_stage(category: str) -> str:
    if category == "banco_leilao":
        return "verificar_edital"
    if category in {"leiloeiro", "agregador_leilao"}:
        return "verificar_pracas"
    if category == "leilao_publico":
        return "monitorar_evento"
    return "nao_se_aplica"


def categorize_source_focus(category: str) -> str:
    if category in {"banco_leilao", "leiloeiro", "agregador_leilao", "leilao_publico"}:
        return "captar desconto e assimetria"
    if category == "marketplace":
        return "captar urgencia e dono direto"
    return "comparar mercado e preco"


def priority_weight(priority: str) -> int:
    return {"alta": 3, "media": 2, "baixa": 1}.get(priority, 1)


def recommended_monitoring_window(source_priority: str, city_priority: str) -> str:
    combined_priority = priority_weight(source_priority) + priority_weight(city_priority)
    if combined_priority >= 6:
        return "duas janelas por dia"
    if combined_priority >= 4:
        return "uma janela por dia"
    return "tres vezes por semana"


def build_search_term(city: str, state: str, source: dict) -> str:
    asset_terms = " OR ".join(
        normalize_text(asset).replace("_", " ") for asset in source["tipos_ativos"]
    )
    return f"{city}/{state} | {asset_terms}"


def build_search_url(source_name: str, source_url: str, city: str, state: str) -> str:
    city_state = f"{city}-{state}"
    city_slug = slug_city(city)
    city_query = city_state.replace(" ", "%20")

    if "OLX" in source_name:
        return f"{source_url.rstrip('/')}/brasil/imoveis?o=1&q={city_query}"
    if "Mercado Livre" in source_name:
        return f"{source_url.rstrip('/')}/_Desde_1_NoIndex_True_ITEM*{city_slug}"
    if "Facebook Marketplace" in source_name:
        return f"{source_url.rstrip('/')}/search/?query={city_query}"
    if "ZAP" in source_name or "Viva Real" in source_name:
        return f"{source_url.rstrip('/')}/venda/imoveis/rs+{city_slug}/"
    return source_url


def build_source_score(city_priority: str, source_priority: str, category: str) -> int:
    score = priority_weight(city_priority) * 10 + priority_weight(source_priority) * 15
    category_bonus = {
        "banco_leilao": 20,
        "agregador_leilao": 15,
        "leiloeiro": 15,
        "marketplace": 10,
        "portal_venda": 8,
        "leilao_publico": 4,
    }
    return min(score + category_bonus.get(category, 0), 100)


def classify_score_band(score: int) -> str:
    if score >= 85:
        return "ataque_imediato"
    if score >= 65:
        return "monitoramento_estruturado"
    return "radar_complementar"


def write_csv(path: Path, fieldnames, rows):
    with path.open("w", newline="", encoding="utf-8-sig") as file:
        writer = csv.DictWriter(file, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)


def build_monitoring_rows(cities, sources):
    rows = []
    generated_at = datetime.now()
    today = generated_at.strftime("%Y-%m-%d")
    timestamp = generated_at.strftime("%Y-%m-%d %H:%M:%S")

    for city in cities:
        for source in sources:
            for schedule_time in source["horarios_recomendados"]:
                score = build_source_score(
                    city["prioridade"], source["prioridade"], source["categoria"]
                )
                rows.append(
                    {
                        "registro": f"{city['cidade']} | {source['nome']} | {schedule_time}",
                        "data_monitoramento": today,
                        "hora_monitoramento": schedule_time,
                        "cidade": city["cidade"],
                        "estado": city["estado"],
                        "prioridade_cidade": city["prioridade"],
                        "fonte": source["nome"],
                        "categoria_fonte": source["categoria"],
                        "url_base": source["url"],
                        "url_busca_recomendada": build_search_url(
                            source["nome"], source["url"], city["cidade"], city["estado"]
                        ),
                        "termo_busca_recomendado": build_search_term(
                            city["cidade"], city["estado"], source
                        ),
                        "tipo_monitoramento": source["tipo_monitoramento"],
                        "janela_operacional": recommended_monitoring_window(
                            source["prioridade"], city["prioridade"]
                        ),
                        "tipos_ativos": ", ".join(source["tipos_ativos"]),
                        "etapa_leilao_padrao": classify_default_stage(source["categoria"]),
                        "foco_estrategico": categorize_source_focus(source["categoria"]),
                        "prioridade_fonte": source["prioridade"],
                        "score_fonte_cidade": score,
                        "faixa_acao": classify_score_band(score),
                        "status": "pendente",
                        "responsavel": "agente_pesquisa_imobiliaria",
                        "ultima_atualizacao": timestamp,
                        "observacoes": source["observacoes"],
                    }
                )
    return rows


def build_capture_template_rows(cities, sources):
    rows = []
    for city in cities:
        for source in sources:
            rows.append(
                {
                    "titulo_oportunidade": "",
                    "data_captura": "",
                    "hora_captura": "",
                    "cidade": city["cidade"],
                    "estado": city["estado"],
                    "bairro_regiao": "",
                    "tipo_ativo": "",
                    "origem": source["nome"],
                    "categoria_origem": source["categoria"],
                    "link_anuncio": "",
                    "valor_pedido_ou_lance_minimo": "",
                    "valor_mercado_estimado": "",
                    "desconto_estimado_percentual": "",
                    "desconto_estimado_absoluto": "",
                    "preco_m2_pedido": "",
                    "preco_m2_mercado": "",
                    "etapa_leilao": "",
                    "data_1o_leilao": "",
                    "hora_1o_leilao": "",
                    "data_2o_leilao": "",
                    "hora_2o_leilao": "",
                    "data_3o_leilao": "",
                    "hora_3o_leilao": "",
                    "comissao_leiloeiro": "",
                    "ocupado": "",
                    "metragem_terreno_m2": "",
                    "metragem_construida_m2": "",
                    "zoneamento_uso_potencial": "",
                    "vocacao_estrategica": "",
                    "custo_reforma_estimado": "",
                    "custo_desocupacao_estimado": "",
                    "custo_regularizacao_estimado": "",
                    "investimento_total_estimado": "",
                    "lance_maximo_recomendado": "",
                    "margem_seguranca_percentual": "",
                    "estrategia_de_saida": "",
                    "potencial_locacao_mensal": "",
                    "potencial_revenda": "",
                    "prazo_liquidez_estimado": "",
                    "analise_financeira_inicial": "",
                    "risco_juridico_inicial": "",
                    "riscos_operacionais": "",
                    "score_localizacao": "",
                    "score_liquidez": "",
                    "score_desconto": "",
                    "score_risco": "",
                    "status_pipeline": "monitorar",
                    "score_prioridade": "",
                    "decisao_preliminar": "",
                    "observacoes": "",
                }
            )
    return rows


def write_markdown_summary(path: Path, cities, sources):
    counts = Counter(source["categoria"] for source in sources)
    high_priority = [source for source in sources if source["prioridade"] == "alta"]

    lines = [
        "# Fontes priorizadas",
        "",
        "## Cidades alvo",
        "",
    ]

    for city in cities:
        lines.append(f"- {city['cidade']}/{city['estado']} ({city['prioridade']})")

    lines.extend(
        [
            "",
            "## Volume por categoria",
            "",
            f"- portais de venda: {counts.get('portal_venda', 0)}",
            f"- marketplace: {counts.get('marketplace', 0)}",
            f"- bancos e leiloes bancarios: {counts.get('banco_leilao', 0)}",
            f"- leiloes publicos: {counts.get('leilao_publico', 0)}",
            f"- leiloeiros: {counts.get('leiloeiro', 0)}",
            f"- agregadores de leilao: {counts.get('agregador_leilao', 0)}",
            "",
            "## Logica operacional",
            "",
            "- Fontes de alta prioridade em cidades de alta prioridade entram em rotina de ataque diario.",
            "- Canais de leilao servem para capturar assimetria de preco, nao apenas volume.",
            "- Portais e marketplace ajudam a formar referencia de mercado e detectar urgencia.",
            "",
            "## Fontes de maior prioridade",
            "",
        ]
    )

    for source in high_priority:
        horarios = ", ".join(source["horarios_recomendados"])
        foco = categorize_source_focus(source["categoria"])
        lines.append(
            f"- {source['nome']} | {source['categoria']} | foco: {foco} | horarios sugeridos: {horarios} | {source['url']}"
        )

    lines.extend(
        [
            "",
            "## Regra de classificacao de leilao",
            "",
            "- 1o leilao: usar quando o edital indicar primeira praca.",
            "- 2o leilao: usar quando o edital indicar segunda praca.",
            "- 3o leilao: usar somente quando houver terceira rodada formal.",
            "- venda direta: usar para bancos e proprietarios sem praca de leilao.",
            "- nao se aplica: usar para anuncio comum sem formato de leilao.",
            "",
            "## Regra de decisao preliminar",
            "",
            "- atacar agora: desconto real, risco administravel e liquidez clara.",
            "- aprofundar analise: potencial bom, mas dependente de validacao juridica ou comercial.",
            "- monitorar: informacao incompleta ou assimetria ainda insuficiente.",
            "- descartar: risco alto, baixa liquidez ou retorno fraco frente ao trabalho exigido.",
        ]
    )

    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main():
    OUTPUT_DIR.mkdir(exist_ok=True)

    cities = load_json(CONFIG_DIR / "cidades.json")
    sources = load_json(CONFIG_DIR / "fontes.json")

    monitoring_rows = build_monitoring_rows(cities, sources)
    capture_rows = build_capture_template_rows(cities, sources)

    write_csv(
        OUTPUT_DIR / "agenda_monitoramento_notion.csv",
        [
            "registro",
            "data_monitoramento",
            "hora_monitoramento",
            "cidade",
            "estado",
            "prioridade_cidade",
            "fonte",
            "categoria_fonte",
            "url_base",
            "url_busca_recomendada",
            "termo_busca_recomendado",
            "tipo_monitoramento",
            "janela_operacional",
            "tipos_ativos",
            "etapa_leilao_padrao",
            "foco_estrategico",
            "prioridade_fonte",
            "score_fonte_cidade",
            "faixa_acao",
            "status",
            "responsavel",
            "ultima_atualizacao",
            "observacoes",
        ],
        monitoring_rows,
    )

    write_csv(
        OUTPUT_DIR / "captura_oportunidades_notion.csv",
        [
            "titulo_oportunidade",
            "data_captura",
            "hora_captura",
            "cidade",
            "estado",
            "bairro_regiao",
            "tipo_ativo",
            "origem",
            "categoria_origem",
            "link_anuncio",
            "valor_pedido_ou_lance_minimo",
            "valor_mercado_estimado",
            "desconto_estimado_percentual",
            "desconto_estimado_absoluto",
            "preco_m2_pedido",
            "preco_m2_mercado",
            "etapa_leilao",
            "data_1o_leilao",
            "hora_1o_leilao",
            "data_2o_leilao",
            "hora_2o_leilao",
            "data_3o_leilao",
            "hora_3o_leilao",
            "comissao_leiloeiro",
            "ocupado",
            "metragem_terreno_m2",
            "metragem_construida_m2",
            "zoneamento_uso_potencial",
            "vocacao_estrategica",
            "custo_reforma_estimado",
            "custo_desocupacao_estimado",
            "custo_regularizacao_estimado",
            "investimento_total_estimado",
            "lance_maximo_recomendado",
            "margem_seguranca_percentual",
            "estrategia_de_saida",
            "potencial_locacao_mensal",
            "potencial_revenda",
            "prazo_liquidez_estimado",
            "analise_financeira_inicial",
            "risco_juridico_inicial",
            "riscos_operacionais",
            "score_localizacao",
            "score_liquidez",
            "score_desconto",
            "score_risco",
            "status_pipeline",
            "score_prioridade",
            "decisao_preliminar",
            "observacoes",
        ],
        capture_rows,
    )

    write_markdown_summary(OUTPUT_DIR / "fontes_priorizadas.md", cities, sources)

    print("Base do agente imobiliario gerada com sucesso.")
    print(f"Agenda Notion: {OUTPUT_DIR / 'agenda_monitoramento_notion.csv'}")
    print(f"Captura Notion: {OUTPUT_DIR / 'captura_oportunidades_notion.csv'}")
    print(f"Resumo: {OUTPUT_DIR / 'fontes_priorizadas.md'}")


if __name__ == "__main__":
    main()
