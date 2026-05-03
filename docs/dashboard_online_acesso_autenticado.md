# Dashboard Online Autenticado

## O que foi implantado

- tela de login no dashboard online externo;
- bloqueio de autoinscricao publica;
- solicitacao de acesso controlada pelo proprio painel;
- painel admin no web app para revisar a fila de solicitacoes;
- troca de senha pelo proprio painel;
- script para criar ou redefinir o usuario inicial no Supabase;
- script para aprovar ou recusar solicitacoes de acesso;
- SQL de endurecimento para permitir leitura apenas por usuarios autenticados.
- SQL de fila de solicitacoes de acesso com CPF e documento obrigatorios.

## Arquivos principais

- `web/dashboard_online/index.html`
- `web/dashboard_online/app.css`
- `web/dashboard_online/app.js`
- `scripts/criar_usuario_dashboard_online.py`
- `scripts/aprovar_solicitacao_dashboard_online.py`
- `sql/supabase_dashboard_auth_lockdown.sql`
- `sql/supabase_dashboard_access_requests.sql`

## Usuario inicial sugerido

- e-mail: `wagner.admin@superindio.local`
- senha inicial de teste: `Dash#SuperIndio2026!`

## Como aplicar a protecao real

1. Abrir o `SQL Editor` do Supabase.
2. Colar e rodar o conteudo de `sql/supabase_dashboard_auth_lockdown.sql`.
3. Colar e rodar o conteudo de `sql/supabase_dashboard_access_requests.sql`.
4. Criar ou redefinir o usuario inicial com:

```powershell
python .\scripts\criar_usuario_dashboard_online.py
```

## Como aprovar novos acessos

1. Listar solicitacoes pendentes:

```powershell
python .\scripts\aprovar_solicitacao_dashboard_online.py --list-pending
```

2. Aprovar uma solicitacao:

```powershell
python .\scripts\aprovar_solicitacao_dashboard_online.py --request-id 1 --approve --reviewed-by wagner.admin
```

Se voce nao informar `--password`, o script usa a senha inicial padrao:

- `Acesso#Dash_2026!`

3. Recusar uma solicitacao:

```powershell
python .\scripts\aprovar_solicitacao_dashboard_online.py --request-id 1 --reject --reviewed-by wagner.admin --reason "Acesso nao autorizado"
```

## O que o painel admin web faz

- lista solicitacoes pendentes, aprovadas e recusadas;
- filtra por status, nome, e-mail, CPF e empresa;
- permite aprovar ou recusar a solicitacao na propria interface;
- gera o comando de provisionamento para criacao do usuario final no Auth.

## Limite atual da web

O dashboard web ja faz a governanca da fila, mas a criacao do usuario final no Supabase Auth ainda depende de backend privilegiado.
Por isso, a interface copia o comando de provisionamento e o script local faz a liberacao final com seguranca.

## Observacao executiva

Sem o SQL de endurecimento, o login vira apenas uma camada visual.
Sem a tabela de solicitacoes, o pedido de acesso nao entra em fila controlada.
Com os dois SQLs aplicados, o dashboard passa a exigir autenticacao real e o cadastro deixa de ser publico.
