# Status das integracoes no Codex

## Validado nesta fase

- Gmail conectado
- Notion conectado
- Google Calendar conectado

## O que isso significa na pratica

- Ja podemos usar o Gmail para resumos e validacoes operacionais dentro do Codex.
- Ja podemos criar ou estruturar a base no Notion sem depender de nova autenticacao.
- Ja podemos usar agenda e cadencia de execucao com apoio do Google Calendar, se fizer sentido mais adiante.

## O que ainda nao precisamos para iniciar

- API externa da OpenAI para desenvolvimento dentro do Codex
- infraestrutura separada de WhatsApp
- VPS
- n8n

## O que so entra depois

- API externa da OpenAI quando quisermos rodar o agente fora do Codex
- automacao recorrente independente
- alertas externos em tempo real

## Gargalo atual

O principal bloqueio agora nao e integracao. E definir:

- onde vai nascer a estrutura principal no Notion
- quais databases serao criadas primeiro
- quais campos sao obrigatorios no fluxo real
- qual criterio final de score e alerta
