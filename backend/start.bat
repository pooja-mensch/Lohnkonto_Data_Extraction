@echo off
echo Starting Lohnkonto Data Extraction Backend...
echo.

REM Check if template.xlsx exists
if not exist "template.xlsx" (
    echo [WARNING] template.xlsx not found!
    echo Please place your Excel template file in this directory.
    echo.
    pause
    exit /b 1
)

REM Check if .env exists
if not exist ".env" (
    echo Creating .env file from .env.example...
    copy .env.example .env
    echo.
)

echo Starting server on http://localhost:8000
echo API Documentation: http://localhost:8000/docs
echo Health Check: http://localhost:8000/health
echo.

python api.py

pause
