# Publicacao do Dashboard Externo

## Leitura do cenario

O dashboard externo ja esta pronto tecnicamente. O dado ja esta no Supabase e a interface ja le o snapshot online. O que falta agora e apenas hospedar a pasta estatica em um provedor acessivel pela internet.

## Melhor caminho

Hoje, para este caso, eu recomendo `Vercel`.

Motivos:
- plano `Hobby` gratuito, segundo a documentacao oficial da Vercel
- HTTPS automatico
- deploy muito simples para site estatico
- bom encaixe para dashboard que so consome API externa

Alternativas:
- `Netlify`: tambem muito bom e com plano Free
- `GitHub Pages`: excelente se quiser publicar direto via repositorio, especialmente em site estatico simples

Referencias oficiais:
- [Vercel pricing](https://vercel.com/pricing)
- [Vercel Hobby plan](https://vercel.com/docs/accounts/plans/hobby)
- [Netlify pricing](https://www.netlify.com/pricing/)
- [GitHub Pages docs](https://docs.github.com/pages)

## Pacote pronto para publicar

Use:
- `preparar_dashboard_online_publico.bat`
- ou `python .\\scripts\\preparar_publicacao_dashboard_online.py`

Saida gerada:
- `saida/dashboard_online_publico`

Essa pasta sai pronta com:
- `index.html`
- `app.css`
- `app.js`
- `supabase-config.js`
- `.nojekyll`
- `vercel.json`
- `netlify.toml`

## Caminho por provedor

### Vercel
1. preparar a pasta publica
2. criar novo projeto no Vercel
3. importar a pasta ou o repositorio
4. apontar a raiz para `saida/dashboard_online_publico`
5. publicar

### Netlify
1. preparar a pasta publica
2. arrastar a pasta `saida/dashboard_online_publico` para o painel da Netlify
3. publicar

### GitHub Pages
1. subir a pasta como site estatico em um repositorio
2. ativar Pages
3. publicar

## Recomendacao executiva

Se o objetivo e velocidade e simplicidade:

1. `Vercel` como primeira escolha
2. `Netlify` como segunda
3. `GitHub Pages` se quiser tudo amarrado ao GitHub

## O que ja esta pronto

- Supabase online validado
- snapshot online validado
- preview local validado
- automacao semanal publicando online
- pacote estatico pronto para hospedagem

## O que falta de verdade

- escolher o provedor
- publicar a pasta
- validar o link publico final
