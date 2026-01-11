@echo off
echo [INFO] Starting Visual Translator Setup...

:: 1. Check Python
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo [ERROR] Python is not installed or not in PATH.
    echo Please install Python 3.10+ from python.org
    pause
    exit /b
)

:: 2. Create Virtual Environment
if not exist ".venv" (
    echo [INFO] Creating virtual environment (.venv)...
    python -m venv .venv
) else (
    echo [INFO] .venv already exists. skipping creation.
)

:: 3. Activate and Install
echo [INFO] Activating .venv and installing dependencies...
call .venv\Scripts\activate.bat

echo [INFO] Upgrading pip...
python -m pip install --upgrade pip

echo [INFO] Installing requirements...
pip install -r requirements.txt

if %errorlevel% neq 0 (
    echo [ERROR] Installation failed.
    echo Common Issue: Microsoft Visual C++ 14.0+ is required.
    echo Download "Build Tools for Visual Studio" if you see compilation errors.
    pause
    exit /b
)

echo [INFO] Setup Complete!
echo You can run the translator using: .venv\Scripts\python.exe main.py ...
pause
