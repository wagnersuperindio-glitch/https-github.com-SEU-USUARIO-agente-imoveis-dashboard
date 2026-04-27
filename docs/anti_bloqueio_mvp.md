# Anti-Bloqueio MVP

## Objetivo

Criar uma camada inicial para fontes que bloqueiam captura HTTP simples.

## Estrategia implantada

- utilitario browser-based em `src/agente_imoveis/utils/browser.py`
- fallback por navegador local headless
- mixin de conector anti-bloqueio em `src/agente_imoveis/connectors/anti_bot.py`
- aplicacao no MVP para:
  - OLX Imoveis
  - ZAP Imoveis
  - Facebook Marketplace
  - Leilao Imovel

## Resultado atual

- `Leilao Imovel` passou a responder com sucesso no MVP
- `Facebook Marketplace` passou a responder com sucesso via captura browser-based com parser do feed
- `OLX` e `ZAP` seguem bloqueados por Cloudflare/HTTP 403 e ainda exigem camada mais forte

## Diagnostico

- o navegador local ja consegue chegar mais perto da origem do bloqueio
- o caso do Facebook mostrou que nem toda pagina com termo sensivel e bloqueio real; em alguns casos o DOM ja esta utilizavel e o parser precisa reconhecer isso
- OLX e ZAP continuam trazendo protecao real, com pagina de bloqueio do Cloudflare e 403 no fallback HTTP
- isso mostra que a direcao tecnica esta correta, mas o nivel atual ainda nao e suficiente para todas as fontes

## Proxima camada recomendada

- Playwright com estrategia dedicada por portal
- opcao complementar com Apify para fontes mais sensiveis
- rotinas de validacao de DOM apos renderizacao
- tratamento de challenge page e classificacao automatica do motivo do bloqueio
- estrategia especifica para:
  - OLX: browser automation mais forte ou Apify
  - ZAP: browser automation mais forte ou Apify
