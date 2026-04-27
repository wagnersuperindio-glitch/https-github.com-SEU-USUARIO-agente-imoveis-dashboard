# Fase 2 - Motor de Inteligencia Geografica

## Leitura do cenario

- O agente ja deixou de ser somente coletor.
- Agora existe uma camada propria de inteligencia operacional baseada na coleta real.
- O foco desta fase foi transformar dado bruto em priorizacao executiva.

## O que foi implantado

- geofiltro forte para RS e cidades-alvo
- inferencia geografica por cidade, estado, titulo, link e textos auxiliares
- score operacional por oportunidade real
- classificacao por decisao: `Atacar Agora`, `Aprofundar Analise`, `Monitorar`, `Descartar`
- consolidacao da inteligencia em `saida/inteligencia/oportunidades_inteligencia.json`

## Resultado da ultima execucao validada

- conectores previstos: 15
- fontes com sucesso: 12
- fontes com erro: 3
- registros enriquecidos: 93
- oportunidades no radar: 2
- ativos identificados no RS: 5

## Leitura estrategica

- o motor agora separa melhor o que e oportunidade aderente ao mapa do grupo
- o painel web interno ganhou filtros para navegar por fonte, decisao, estado e status geografico
- `Leilao Imovel` saiu do bloco travado e entrou no conjunto operacional do MVP

## Gargalos atuais

- OLX continua bloqueando com `403`
- ZAP continua bloqueando com `403`
- Facebook Marketplace continua bloqueando com `400`
- ainda ha muitos registros com geografia indefinida, principalmente em fontes genericas

## Recomendacao executiva

- aprofundar parser geografico dos conectores ja liberados
- ampliar coleta de cidades do RS com mais fontes locais
- tratar OLX, ZAP e Facebook com stack dedicada de navegador e/ou fornecedor externo
- evoluir o score operacional para score de investimento quando houver valor de mercado e desconto real
