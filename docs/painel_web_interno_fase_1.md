# Painel Web Interno - Fase 1

## Objetivo

Criar uma camada web profissional sobre o motor do agente imobiliário sem travar a evolução técnica do núcleo.

## O que entra nesta fase

- backend leve em Python para servir painel interno
- endpoint interno `/api/dashboard`
- leitura automática da última execução real do MVP
- consolidação de KPIs operacionais
- lista de fontes bloqueadas
- top oportunidades por score de inteligência
- visão do radar geográfico do RS

## Arquivos principais

- `src/agente_imoveis/dashboard/service.py`
- `scripts/gerar_dashboard_data.py`
- `scripts/iniciar_painel_web.py`
- `web/dashboard/index.html`
- `web/dashboard/app.css`
- `web/dashboard/app.js`

## Leitura estratégica

- esta fase não tenta substituir o Notion
- esta fase cria uma cabine de comando interna
- o Notion continua como base operacional
- o painel web vira a visão executiva rápida

## Próxima fase recomendada

- filtros interativos por cidade e fonte
- reprocessamento sob demanda
- publicação assistida de oportunidades no Notion
- autenticação interna
- fila de coleta e status em tempo real
