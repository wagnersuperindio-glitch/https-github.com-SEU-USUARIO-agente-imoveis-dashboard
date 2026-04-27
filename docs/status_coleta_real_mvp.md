# Status da Coleta Real MVP

## Leitura do cenario

- O agente saiu da fase apenas estrutural e ja executa coleta real no bloco MVP.
- A execucao mais recente confirmou funcionamento em 15 conectores planejados.
- O projeto agora tem separacao clara entre fontes ja coletaveis e fontes que exigem stack anti-bloqueio.

## Resultado atual

- Conectores previstos no MVP: 15
- Fontes com sucesso: 13
- Fontes com bloqueio ou erro: 2
- Registros normalizados gerados: 99
- Ultimo resumo operacional: `saida/execucoes/2026-04-21_10-16-58_resumo_execucao_mvp.json`

## Fontes operacionais no MVP

- Imoveis Caixa
- Caixa - Lista Completa por Estado
- Seu Imovel BB
- Banrisul - Bens a Venda
- Moraes Leiloes
- Zago Leiloes
- Mega Leiloes
- Leilao Imovel
- Facebook Marketplace
- Imobiliaria Guaiba
- Imobsul Imobiliaria
- Almeida e Koch
- Zicuri Imoveis

## Fontes com tratamento especial necessario

- OLX Imoveis
- ZAP Imoveis

## Diagnostico estrategico

- O bloco de bancos, leiloeiros e imobiliarias locais ja permite evolucao real do agente.
- O maior gargalo agora nao e mais estrutura; e qualidade de parser, filtro geografico e camada anti-bloqueio.
- BB e Mega Leiloes ja estao em patamar melhor de utilidade, com menos ruido e melhor leitura de titulo, cidade e metragem.
- A camada anti-bloqueio ja entregou ganho concreto: `Leilao Imovel` e `Facebook Marketplace` entraram no bloco operacional.
- O gargalo tecnico ficou mais concentrado e mais claro: `OLX` e `ZAP` exigem nivel superior de browser automation ou plataforma dedicada.

## Recomendacao executiva

- Tratar imediatamente OLX e ZAP com Playwright ou Apify.
- Evoluir os conectores liberados para identificar cidade do radar, tipo de ativo, metragem, data do evento e potencial estrategico.
- Consolidar cada execucao relevante em tres destinos: markdown local, Notion e Gmail.

## Proxima fase

- parser geografico para priorizar RS e cidades-alvo
- score automatico em cima da coleta real
- publicacao assistida no Notion para entradas selecionadas
- rotina recorrente de relatorio operacional
