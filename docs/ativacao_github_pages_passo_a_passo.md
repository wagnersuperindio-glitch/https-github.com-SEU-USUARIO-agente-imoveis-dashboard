# Ativacao do Dashboard no GitHub Pages

## Leitura do cenario

O projeto ja esta:
- commitado localmente
- na branch `main`
- conectado ao repositório GitHub remoto
- com workflow pronto para publicar o dashboard externo

O ponto restante e concluir o `push` no GitHub e ativar o `GitHub Pages`.

## Passo 1: publicar o projeto no GitHub

Use:

- `publicar_no_github_pages.bat`

Ou no terminal:

```powershell
git push -u origin main
```

Se o GitHub pedir autenticacao:
- conclua o login
- permita o acesso

## Passo 2: ativar o GitHub Pages

No repositório:

1. abrir `Settings`
2. abrir `Pages`
3. em `Build and deployment`
4. escolher `GitHub Actions`

## Passo 3: validar o workflow

Depois do push:

1. abrir a aba `Actions`
2. procurar o workflow:
   - `Publicar Dashboard Online`
3. aguardar o workflow concluir

## Passo 4: abrir o link publico

O endereço esperado deve ficar parecido com:

- `https://wagnersuperindio-glitch.github.io/https-github.com-SEU-USUARIO-agente-imoveis-dashboard/`

## O que o workflow faz

1. prepara a pasta publica do dashboard online
2. publica `saida/dashboard_online_publico`
3. entrega o dashboard externo lendo o snapshot do Supabase

## Recomendacao executiva

O caminho mais rapido agora e:

1. rodar `publicar_no_github_pages.bat`
2. concluir o login do GitHub se for pedido
3. ativar `GitHub Actions` em `Pages`
4. validar a URL publica final
