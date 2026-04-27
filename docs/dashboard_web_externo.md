# Dashboard Web Externo

## Leitura do cenario

O desktop continua sendo a cabine de comando operacional. Ja o dashboard web externo foi preparado para leitura do snapshot online salvo no Supabase.

## O que foi criado

- `web/dashboard_online/index.html`
- `web/dashboard_online/app.css`
- `web/dashboard_online/app.js`
- `web/dashboard_online/supabase-config.js`
- `sql/supabase_dashboard_tables.sql`

## Como funciona

1. o desktop gera o `dashboard_data.json`
2. o desktop publica no Supabase
3. o dashboard externo le `dashboard_current`

## O que falta para ativar

Hoje o bloqueio real e apenas este:
- rodar `sql/supabase_dashboard_tables.sql` no `SQL Editor` do Supabase

Sem essas tabelas, a publicacao falha com:
- `Could not find the table 'public.dashboard_current' in the schema cache`

## Onde abrir depois

Depois que as tabelas existirem, este dashboard externo ja podera ser publicado como pagina estatica ou aberto localmente:

- `web/dashboard_online/index.html`
- `abrir_dashboard_online_preview.bat`
- `python .\scripts\iniciar_dashboard_online_preview.py`

## Recomendacao executiva

O melhor caminho agora e:

1. rodar o SQL das tabelas no Supabase
2. publicar o snapshot com `python .\\scripts\\publicar_dashboard_online.py`
3. validar o dashboard externo lendo a base online
4. depois publicar essa pasta em uma hospedagem estatica

Essa e a virada que tira o acesso da dependencia da rede interna do supermercado.
