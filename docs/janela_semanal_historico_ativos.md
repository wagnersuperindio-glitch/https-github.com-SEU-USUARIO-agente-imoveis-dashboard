# Janela Semanal e Historico por Ativo

## Objetivo

Profissionalizar o agente imobiliario para responder, em cada rodada relevante:

- o que entrou desde a ultima segunda
- o que mudou desde a ultima segunda
- o que saiu desde a ultima segunda

## O que foi implantado

- snapshot historico por execucao de inteligencia
- chave de identidade por ativo
- comparativo semanal automatico
- relatorio executivo reorganizado em 3 blocos:
  - panorama geral
  - cidades do radar
  - oportunidades de ataque

## Estrutura tecnica

- historico dos snapshots:
  - `saida/historico/snapshots`
- janelas comparativas:
  - `saida/historico/janelas`
- inteligencia consolidada:
  - `saida/inteligencia/oportunidades_inteligencia.json`

## Regra operacional

- a execucao atual grava um snapshot dos ativos enriquecidos
- o sistema procura a base comparativa anterior ao inicio da semana corrente
- se nao existir base anterior ao inicio da semana, usa a ultima execucao anterior disponivel
- com isso o agente separa:
  - ativos que entraram
  - ativos que mudaram
  - ativos que sairam

## Ganho estrategico

- o agente deixa de ser apenas fotografia operacional
- passa a ter memoria por ativo
- melhora governanca
- melhora leitura de movimento real de mercado
- prepara a base para historico de preco e score de investimento

## Recomendacao executiva

- manter a janela semanal como padrao da governanca
- usar o bloco de cidades do radar para priorizacao geografica
- usar o bloco de oportunidades de ataque para decisao comercial e de capital
