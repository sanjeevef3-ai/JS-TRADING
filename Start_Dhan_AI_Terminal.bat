@echo off
title Indian Stock Market MiroFish AI + Dhan Terminal Launcher
color 0A
echo =====================================================================
echo   INDIAN STOCK MARKET MIROFISH AI + DHAN TERMINAL (ID: 1000659782)
echo =====================================================================
echo.
echo [1/2] Starting MiroFish AI Backend Server on http://127.0.0.1:8000 ...
set PYTHONIOENCODING=utf-8
start "MiroFish AI Server" /min "d:\AGI\.venv\Scripts\python.exe" "d:\AGI\server.py"
timeout /t 3 /nobreak >nul

echo [2/2] Opening AI Dashboard and Dhan Trading Terminal ...
start http://127.0.0.1:8000
start https://web.dhan.co

echo.
echo =====================================================================
echo   DONE! Both AI Dashboard and Dhan Terminal are now LIVE!
echo   To install the AI Widget directly inside Dhan screen:
echo   1. Open Chrome -> Go to chrome://extensions
echo   2. Turn ON 'Developer mode' (top-right)
echo   3. Click 'Load unpacked' -> Select folder: d:\AGI\dhan_chrome_extension
echo =====================================================================
pause
