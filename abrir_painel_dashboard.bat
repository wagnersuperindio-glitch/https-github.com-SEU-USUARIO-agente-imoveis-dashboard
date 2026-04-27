@echo off
cd /d "C:\Users\Administrador\Desktop\CODEX PROJETOS\AGENTE IMOVEIS CODEX"
set PAINEL_HOST=0.0.0.0
set PAINEL_PORT=8765
python .\scripts\gerar_dashboard_data.py
python .\scripts\iniciar_painel_web.py
