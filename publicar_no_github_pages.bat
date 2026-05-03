@echo off
cd /d "C:\Users\Administrador\Desktop\CODEX PROJETOS\AGENTE IMOVEIS CODEX"
echo Publicando projeto no GitHub...
echo Se o GitHub pedir autenticacao, conclua o login na janela que abrir.
git push -u origin main
echo.
echo Se o push concluir com sucesso, o proximo passo e ativar GitHub Pages em Settings > Pages > Build and deployment > GitHub Actions.
pause
