@echo off
title JYOTI SINGH - Personal AI Super Trading Terminal
cd /d "d:\AGI"
echo ========================================================
echo   JYOTI SINGH - Personal AI Super Trading Terminal
echo ========================================================
echo Starting Server & Ngrok Tunnel...

:: Kill any old lingering instances
taskkill /f /im python.exe /fi "WINDOWTITLE eq JYOTI*" 2>nul
taskkill /f /im ngrok.exe 2>nul

:: Start permanent ngrok tunnel
start "Ngrok Tunnel" /min "d:\AGI\tools\ngrok.exe" http 127.0.0.1:8000 --url "https://pastrami-troubling-heave.ngrok-free.dev"

:: Start python server
set PYTHONIOENCODING=utf-8
"d:\AGI\.venv\Scripts\python.exe" "d:\AGI\server.py"

pause
