@echo off
setlocal
cd /d "%~dp0"
powershell -NoProfile -ExecutionPolicy Bypass -Command "schtasks /Create /TN \"Agente Imoveis - Seg Qua 10h\" /SC WEEKLY /D MON,WED /ST 10:00 /TR '\"C:\Users\Administrador\AppData\Local\Programs\Python\Python312\python.exe\" \"%CD%\scripts\executar_rotina_programada_imoveis.py\"' /F"
endlocal
