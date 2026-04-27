# Score de Investimento v1

## Objetivo

Separar a leitura de triagem da leitura de capital.

- `operational_score`: organiza a prioridade operacional do radar
- `investment_score`: organiza a prioridade de investimento e decisao de capital

## Logica

O `investment_score` vai de `0 a 10` e usa a mesma regra de decisao da regua v1, mas com leitura diferente:

1. `Desconto vs comparavel interno por m2`
2. `Liquidez provavel`
3. `Risco controlado`
4. `Aderencia estrategica do ativo`
5. `Facilidade de execucao`

## Fonte do comparativo

Nesta fase o desconto nao depende de API externa.

O agente calcula:

- preco por m2 do ativo
- mediana interna de preco por m2 por `cidade + familia de ativo`
- desconto percentual do ativo contra essa referencia interna

Familias principais:

- terreno
- casa
- apartamento
- comercial
- galpao
- rural

## Leitura estrategica

O `investment_score` nao substitui diligencia juridica, visita ou analise financeira final.

Ele serve para:

- reduzir o numero de ativos que parecem bons, mas nao merecem capital agora
- destacar ativos com assimetria real
- organizar o bloco de `oportunidades de ataque`

## Resultado esperado

- menos falso positivo no topo do radar
- melhor comparacao entre ativos da mesma cidade
- melhor priorizacao de terreno, comercial e ativos com assimetria real

## Regra de uso

- painel: usar `investment_score` como score principal de decisao
- relatorio: usar `investment_decision` no bloco de ataque
- operacao: manter `operational_score` para governanca do pipeline
