@echo off
echo ========================================
echo   ERP System - Quick Start Script
echo ========================================
echo.

echo [1/4] Checking Docker Desktop...
docker ps >nul 2>&1
if %errorlevel% neq 0 (
    echo ❌ Docker Desktop is not running!
    echo.
    echo Please start Docker Desktop manually:
    echo   1. Open Docker Desktop from Start Menu
    echo   2. Wait for it to fully start
    echo   3. Run this script again
    echo.
    pause
    exit /b 1
)
echo ✅ Docker Desktop is running

echo.
echo [2/4] Starting MySQL database...
docker-compose up -d
if %errorlevel% neq 0 (
    echo ❌ Failed to start database
    pause
    exit /b 1
)
echo ✅ Database started

echo.
echo [3/4] Waiting for MySQL to be ready...
timeout /t 10 /nobreak >nul
echo ✅ MySQL should be ready

echo.
echo [4/4] Initializing database tables...
python scripts/init_db.py
if %errorlevel% neq 0 (
    echo ⚠️  Database initialization had issues (might be OK if tables exist)
)

echo.
echo ========================================
echo   🚀 Ready to start the application!
echo ========================================
echo.
echo Run this command to start the server:
echo   uvicorn app.interface.api.main:app --reload --host 0.0.0.0 --port 8000
echo.
echo Then open: http://localhost:8000
echo.
pause
