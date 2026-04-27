# Implantacao do Painel em Maquina Fixa

## Leitura do cenario

O painel ja esta pronto para operar como produto interno. O que falta para estabilizar o uso no dia a dia e publicar em uma maquina fixa da operacao, com rotina previsivel e acesso controlado.

## Objetivo

Colocar o painel para rodar continuamente em uma maquina dedicada ou semi-dedicada da empresa, acessivel pela rede interna e com caminho claro para HTTPS.

## Recomendacao executiva

O melhor caminho agora e:

1. escolher uma maquina fixa do escritorio ou da operacao
2. reservar IP interno para essa maquina
3. instalar o projeto nela
4. rodar o launcher corporativo
5. testar o acesso em outras maquinas da rede
6. depois adicionar HTTPS

## Checklist de implantacao

### 1. Preparar a maquina
- Windows com Python operacional
- pasta do projeto copiada para a maquina
- firewall liberado para a porta `8765`
- IP interno estavel ou reserva DHCP

### 2. Publicar o painel
- usar `abrir_painel_dashboard_corporativo.bat`
- validar no navegador local
- validar em outra maquina da empresa usando `http://IP_DA_MAQUINA:8765`

### 3. Validar atualizacao
- confirmar se `dashboard_data.json` esta sendo regenerado
- confirmar se o relatorio mais recente esta atualizando
- confirmar se a automacao semanal continua ativa

### 4. Validar acesso
- testar `wagner.admin`
- testar `diretoria.indio`
- testar `expansao.indio`
- confirmar login, sessao e logout

### 5. Elevar para HTTPS
- obter certificado e chave privada
- preencher os caminhos em `abrir_painel_dashboard_https_modelo.bat`
- subir o servidor com HTTPS
- trocar os links internos para `https://`

## Credenciais atuais

### Usuarios
- `wagner.admin`
- `diretoria.indio`
- `expansao.indio`

### Senhas fortes atuais
- `wagner.admin` -> `Wag#Radar_2026!Prime`
- `diretoria.indio` -> `Dir#Expansao_2026!Visao`
- `expansao.indio` -> `Exp#Ativos_2026!Mapa`

## Como trocar senha depois

Exemplo:

```powershell
python .\scripts\rotacionar_senha_usuario_painel.py wagner.admin "NovaSenhaForte@2026!"
```

## Operacao recomendada

### Modo imediato
- usar HTTP interno apenas na rede da empresa ou via VPN

### Modo seguinte
- habilitar HTTPS
- opcionalmente colocar um nome interno, como:
  - `painel-imoveis.indio.local`

## Riscos principais

- deixar a porta liberada fora da rede interna sem HTTPS
- manter senhas padrao por muito tempo
- rodar em maquina instavel ou desligada com frequencia
- nao reservar IP da maquina

## Prioridades

1. colocar em maquina fixa
2. validar acesso em outras maquinas
3. trocar senhas se desejar novas combinacoes
4. subir HTTPS
5. depois avaliar proxy reverso e dominio interno
