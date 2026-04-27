# Agente de Pesquisa Imobiliaria

Este projeto monta a base operacional de um agente para pesquisar oportunidades de:

- terrenos
- casas
- sitios e chacaras
- predios comerciais
- galpoes e ativos industriais

O foco inicial esta nas cidades:

- Guaiba/RS
- Eldorado do Sul/RS
- Sao Jeronimo/RS
- Arroio dos Ratos/RS
- Charqueadas/RS
- Tapes/RS
- Barra do Ribeiro/RS
- Capao da Canoa/RS
- Xangrila/RS

## O que este agente entrega

1. Lista estruturada de fontes para monitoramento:
- portais de venda de imoveis
- marketplace
- bancos com venda e leilao de imoveis
- leiloes publicos
- leiloeiros relevantes

2. Agenda de monitoramento por data e horario para importacao no Notion.

3. Template de captura de oportunidades com campos para:
- cidade
- tipo de ativo
- origem
- valor
- etapa do leilao
- data e hora de cada praca
- status de analise

4. Camada inicial de inteligencia operacional:
- score por combinacao cidade + fonte
- faixa de acao para priorizacao
- foco estrategico por tipo de canal
- janela operacional sugerida

5. Template de viabilidade preliminar com campos para:
- valor de mercado estimado
- desconto absoluto e percentual
- preco por m2
- custo de reforma, desocupacao e regularizacao
- lance maximo recomendado
- estrategia de saida
- potencial de locacao, revenda e liquidez
- decisao preliminar

## Estrutura

- [agente_pesquisa_imoveis.md](C:/Users/Administrador/Desktop/CODEX%20PROJETOS/AGENTE%20IMOVEIS%20CODEX/agente_pesquisa_imoveis.md)
- [config/cidades.json](C:/Users/Administrador/Desktop/CODEX%20PROJETOS/AGENTE%20IMOVEIS%20CODEX/config/cidades.json)
- [config/fontes.json](C:/Users/Administrador/Desktop/CODEX%20PROJETOS/AGENTE%20IMOVEIS%20CODEX/config/fontes.json)
- [scripts/gerar_base_imobiliaria.py](C:/Users/Administrador/Desktop/CODEX%20PROJETOS/AGENTE%20IMOVEIS%20CODEX/scripts/gerar_base_imobiliaria.py)

## Como usar

Execute:

```powershell
python .\scripts\gerar_base_imobiliaria.py
```

O script gera:

- `saida/agenda_monitoramento_notion.csv`
- `saida/captura_oportunidades_notion.csv`
- `saida/fontes_priorizadas.md`

Para relatorio operacional:

```powershell
python .\scripts\gerar_relatorio_imobiliario.py
```

O script gera:

- `saida/relatorios/relatorio_YYYY-MM-DD_HH-MM-SS.md`

Para validar a regua inicial de score:

```powershell
python .\scripts\calcular_score_oportunidade.py
```

Para revisar as ondas de implantacao das fontes:

```powershell
python .\scripts\resumir_fontes_implantacao.py
```

Para apresentar a arquitetura MVP de conectores:

```powershell
python .\scripts\apresentar_arquitetura_mvp.py
```

Para executar a coleta inicial do MVP:

```powershell
python .\scripts\executar_coleta_mvp.py
```

Para gerar a base do painel interno:

```powershell
python .\scripts\gerar_dashboard_data.py
```

Para gerar a inteligencia operacional da ultima coleta:

```powershell
python .\scripts\gerar_inteligencia_operacional.py
```

Para subir o painel web interno:

```powershell
python .\scripts\iniciar_painel_web.py
```

Painel local:

- `http://127.0.0.1:8765`

## Status atual do MVP real

- O MVP de coleta real ja esta operacional.
- Ultima execucao validada: 15 conectores previstos, 12 com sucesso, 3 com bloqueio e 93 registros normalizados.
- As fontes bloqueadas hoje sao `OLX Imoveis`, `ZAP Imoveis` e `Facebook Marketplace`.
- O status executivo desta etapa esta em [docs/status_coleta_real_mvp.md](C:/Users/Administrador/Desktop/CODEX%20PROJETOS/AGENTE%20IMOVEIS%20CODEX/docs/status_coleta_real_mvp.md).
- A fase 1 do painel web interno esta documentada em [docs/painel_web_interno_fase_1.md](C:/Users/Administrador/Desktop/CODEX%20PROJETOS/AGENTE%20IMOVEIS%20CODEX/docs/painel_web_interno_fase_1.md).
- A fase 2 do motor geografico e da inteligencia operacional esta em [docs/fase_2_motor_inteligencia_geografica.md](C:/Users/Administrador/Desktop/CODEX%20PROJETOS/AGENTE%20IMOVEIS%20CODEX/docs/fase_2_motor_inteligencia_geografica.md).
- A camada anti-bloqueio do MVP esta em [docs/anti_bloqueio_mvp.md](C:/Users/Administrador/Desktop/CODEX%20PROJETOS/AGENTE%20IMOVEIS%20CODEX/docs/anti_bloqueio_mvp.md).

## Observacoes estrategicas

- O arquivo de fontes ja separa o que e canal de venda, canal de leilao bancario, canal publico, agregador e leiloeiro.
- A agenda agora sai com `score_fonte_cidade`, `faixa_acao`, `foco_estrategico` e `janela_operacional`, o que melhora a disciplina de execucao.
- A coluna `etapa_leilao` aceita `1o leilao`, `2o leilao`, `3o leilao`, `venda direta` e `nao se aplica`.
- A base de captura foi ampliada para ajudar decisao real, nao apenas cadastro.
- A ultima etapa que depende de voce e informar em qual pagina do Notion a base deve ser criada. O projeto ja deixa o CSV pronto para importacao imediata.

## Integracoes ja validadas no Codex

- Gmail conectado
- Notion conectado
- Google Calendar conectado

Nesta fase, o projeto pode evoluir usando as integracoes nativas ja liberadas no Codex. APIs externas entram depois, quando quisermos transformar o agente em operacao autonoma fora desta conversa.

## Direcao operacional

- O catalogo de fontes foi ampliado para contemplar bancos, leiloeiros, agregadores, fontes publicas, portais e imobiliarias locais.
- O relatorio deve existir em markdown, no Notion e no email `wagnersuperindio@gmail.com`.
- A coleta real ja roda fonte por fonte sem derrubar o pipeline inteiro quando uma origem bloqueia acesso.
- O painel web interno funciona como cabine de comando executiva sobre a ultima execucao real do agente.
- O geofiltro e o score operacional agora ja rodam sobre a coleta real.
