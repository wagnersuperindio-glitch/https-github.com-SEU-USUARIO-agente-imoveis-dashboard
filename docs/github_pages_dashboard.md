# GitHub Pages do Dashboard

## Leitura do cenario

O projeto foi preparado para publicar o dashboard externo no GitHub Pages sem depender de build manual no GitHub. O workflow gera a pasta publica automaticamente e faz o deploy.

## O que foi criado

- `.github/workflows/github-pages-dashboard.yml`
- `.gitignore`

## Como funciona

1. o repositorio sobe para o GitHub
2. a branch principal recebe push
3. o GitHub Actions executa `scripts/preparar_publicacao_dashboard_online.py`
4. o artifact `saida/dashboard_online_publico` e publicado no GitHub Pages

## O que publicar

Subir este projeto para um repositorio GitHub.

## Como ativar no GitHub

1. criar um repositorio no GitHub
2. enviar este projeto para a branch `main`
3. abrir `Settings`
4. entrar em `Pages`
5. em `Build and deployment`, escolher `GitHub Actions`
6. o workflow `Publicar Dashboard Online` fara o deploy

## Resultado esperado

O site ficara em um endereco parecido com:

- `https://SEU-USUARIO.github.io/NOME-DO-REPOSITORIO/`

## Observacao importante

O dashboard externo ja le o snapshot online direto do Supabase, entao ele nao depende da rede interna do supermercado.

## Recomendacao executiva

O melhor caminho agora e:

1. criar o repositorio GitHub
2. subir este projeto
3. ativar Pages via `GitHub Actions`
4. validar o link publico final
