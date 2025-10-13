@echo off
REM Quick start script for Account Plan Agent (Windows)
REM This script sets up and runs the application

echo ==================================
echo Account Plan Agent - Quick Start
echo ==================================
echo.

REM Check Python version
echo Checking Python version...
python --version
if %errorlevel% neq 0 (
    echo Python not found! Please install Python 3.8-3.11
    pause
    exit /b 1
)

REM Check if .env file exists
if not exist .env (
    echo.
    echo Warning: .env file not found!
    echo Creating from env.example...
    if exist env.example (
        copy env.example .env
        echo Created .env file
        echo Please edit .env and add your OpenAI API key before continuing
        pause
    ) else (
        echo env.example not found!
        pause
        exit /b 1
    )
)

REM Check if virtual environment exists
if not exist venv (
    echo.
    echo Creating virtual environment...
    python -m venv venv
    echo Virtual environment created
)

REM Activate virtual environment
echo.
echo Activating virtual environment...
call venv\Scripts\activate.bat

REM Install dependencies
echo.
echo Installing dependencies...
pip install -r requirements.txt
if %errorlevel% neq 0 (
    echo Failed to install dependencies
    pause
    exit /b 1
)
echo Dependencies installed

REM Initialize database
if not exist account_plan_agent.db (
    echo.
    echo Initializing database...
    python init_database.py
    if %errorlevel% neq 0 (
        echo Failed to initialize database
        pause
        exit /b 1
    )
    echo Database initialized
    echo.
    echo Default admin credentials:
    echo   Username: admin
    echo   Password: admin
    echo   Please change the password after first login!
) else (
    echo.
    echo Database already exists, skipping initialization
)

echo.
echo ==================================
echo Setup Complete!
echo ==================================
echo.
echo Starting the application...
echo.
echo Backend (FastAPI) will start on: http://localhost:8000
echo Frontend (Streamlit) will start on: http://localhost:8501
echo.
echo Press Ctrl+C to stop
echo.

REM Start backend in new window
echo Starting backend...
start "Account Plan Agent - Backend" python main.py

REM Wait a moment for backend to start
timeout /t 3 /nobreak > nul

REM Start frontend
echo Starting frontend...
streamlit run app.py

echo.
echo Application stopped.
pause

