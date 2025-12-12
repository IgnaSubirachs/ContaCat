@echo off
echo ========================================
echo   ERP System - Full Rebuild & Start
echo ========================================
echo.

echo [1/3] Stopping existing containers...
docker-compose down

echo.
echo [2/3] Rebuilding Docker image (installing new dependencies)...
docker-compose build --no-cache

echo.
echo [3/3] Starting services...
docker-compose up -d

echo.
echo ========================================
echo   ✅ Rebuild Complete!
echo ========================================
echo.
echo Open http://localhost:8000 to verify.
echo.
pause
