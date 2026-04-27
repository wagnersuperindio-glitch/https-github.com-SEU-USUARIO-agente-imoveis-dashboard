# Arquitetura Visual Profissional

## Visao executiva

O agente imobiliario foi estruturado como uma plataforma em camadas.

O objetivo e evitar um sistema bonito na teoria e fraco na pratica.

A arquitetura abaixo foi desenhada para:

- capturar oportunidades com amplitude
- limpar e organizar dados com disciplina
- priorizar com criterio economico e operacional
- registrar decisao no Notion
- gerar relatorio executivo e alertas

## Fluxo macro

```mermaid
flowchart TD
    A["1. Fontes de Pesquisa"] --> B["2. Coleta do MVP"]
    B --> C["3. Normalizacao e Deduplicacao"]
    C --> D["4. Score e Inteligencia"]
    D --> E["5. Registro no Notion"]
    D --> F["6. Relatorio Markdown"]
    F --> G["7. Envio por Email"]
    D --> H["8. Alertas Urgentes"]
```

## Camadas operacionais

```mermaid
flowchart LR
    subgraph S1["Camada 1 - Origem"]
        A1["Bancos"]
        A2["Leiloeiros"]
        A3["Agregadores"]
        A4["Portais"]
        A5["Marketplace"]
        A6["Imobiliarias Locais"]
        A7["Fontes Publicas"]
    end

    subgraph S2["Camada 2 - Ingestao"]
        B1["Conectores MVP"]
        B2["Coleta Estruturada"]
        B3["Captura Bruta"]
    end

    subgraph S3["Camada 3 - Processamento"]
        C1["Padronizacao"]
        C2["Geofiltro"]
        C3["Filtro de Data"]
        C4["Deduplicacao"]
    end

    subgraph S4["Camada 4 - Inteligencia"]
        D1["Regua de Score v1"]
        D2["CMA / Preco m2"]
        D3["Tese do Ativo"]
        D4["Decisao Preliminar"]
    end

    subgraph S5["Camada 5 - Entrega"]
        E1["Notion"]
        E2["Markdown"]
        E3["Gmail"]
        E4["Alertas"]
    end

    S1 --> S2 --> S3 --> S4 --> S5
```

## Mapa dos modulos

```mermaid
flowchart TD
    M1["connectors/"]
    M2["capture/"]
    M3["processing/"]
    M4["scoring/"]
    M5["reporting/"]
    M6["integrations/"]

    M1 --> M2
    M2 --> M3
    M3 --> M4
    M4 --> M5
    M5 --> M6
```

## Prioridade de implantacao

```mermaid
flowchart TD
    P1["Onda 1 - MVP imediato"] --> P2["Onda 2 - Expansao controlada"]
    P2 --> P3["Onda 3 - Fontes especiais"]

    P1a["Caixa / BB / Banrisul"]
    P1b["Leilao Imovel / Mega"]
    P1c["OLX / ZAP / Facebook"]
    P1d["Imobiliarias locais chave"]

    P1 --> P1a
    P1 --> P1b
    P1 --> P1c
    P1 --> P1d
```

## Regra de arquitetura

- nenhuma fonte nova entra sem estabilidade da anterior
- o dado bruto nunca pula direto para a decisao
- o score organiza prioridade, mas nao substitui julgamento executivo
- o Notion e o centro operacional
- o relatorio precisa existir em markdown, Notion e email
