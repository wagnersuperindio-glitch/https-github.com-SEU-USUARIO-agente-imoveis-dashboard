# Dashboard Online Autenticado

## O que foi implantado

- tela de login no dashboard online externo;
- cadastro de novo usuario pelo proprio painel;
- troca de senha pelo proprio painel;
- script para criar ou redefinir o usuario inicial no Supabase;
- SQL de endurecimento para permitir leitura apenas por usuarios autenticados.

## Arquivos principais

- `web/dashboard_online/index.html`
- `web/dashboard_online/app.css`
- `web/dashboard_online/app.js`
- `scripts/criar_usuario_dashboard_online.py`
- `sql/supabase_dashboard_auth_lockdown.sql`

## Usuario inicial sugerido

- e-mail: `wagner.admin@superindio.local`
- senha inicial de teste: `Dash#SuperIndio2026!`

## Como aplicar a protecao real

1. Abrir o `SQL Editor` do Supabase.
2. Colar e rodar o conteudo de `sql/supabase_dashboard_auth_lockdown.sql`.
3. Criar ou redefinir o usuario inicial com:

```powershell
python .\scripts\criar_usuario_dashboard_online.py
```

## Observacao executiva

Sem o SQL de endurecimento, o login vira apenas uma camada visual.
Com o SQL aplicado, o dashboard passa a exigir autenticacao real para leitura do snapshot.
