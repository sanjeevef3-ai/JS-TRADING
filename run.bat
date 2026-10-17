@echo off
chcp 65001 >nul
title Indian Stock Market MiroFish AI Engine
set PYTHONIOENCODING=utf-8

echo ====================================================================
echo  🇮🇳 Indian Stock Market MiroFish AI Swarm Engine
echo  Deep Chart Patterns + Multi-Timeframe Confluence + Bounded Swarm
echo ====================================================================
echo.

if not exist ".venv\Scripts\python.exe" (
    echo [ERROR] Virtual environment not found in .venv!
    echo Please install dependencies first using uv.
    pause
    exit /b 1
)

echo Select launch mode:
echo   1. Launch Interactive Web Dashboard (http://127.0.0.1:8000)
echo   2. Run Terminal CLI Analysis (Interactive)
echo   3. Run Quick NIFTY 50 Analysis
echo   4. Run Self-Refining AI Diagnostics & Health Check
echo.
set /p choice="Enter choice (1-4) [default: 1]: "

if "%choice%"=="" set choice=1

if "%choice%"=="1" (
    echo.
    echo Starting Web Server... Open your browser at http://127.0.0.1:8000
    .venv\Scripts\python.exe main.py --web
) else if "%choice%"=="2" (
    echo.
    .venv\Scripts\python.exe cli.py
) else if "%choice%"=="3" (
    echo.
    .venv\Scripts\python.exe cli.py --symbol NIFTY
) else if "%choice%"=="4" (
    echo.
    .venv\Scripts\python.exe main.py --refine
) else (
    echo Invalid choice. Starting Web Server by default...
    .venv\Scripts\python.exe main.py --web
)

pause
