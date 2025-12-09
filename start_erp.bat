@echo off
echo Starting ERP Catala Web Server...
echo.
echo Access the application at: http://localhost:8000
echo.

start "" "http://localhost:8000"
python -m uvicorn app.interface.api.main:app --reload --host 0.0.0.0 --port 8000
