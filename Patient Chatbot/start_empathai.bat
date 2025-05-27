@echo off
REM === Navigate to script directory ===
cd /d %~dp0

REM === Check for Python ===
where python >nul 2>&1 || (
    echo  Python is not installed or not in PATH.
    pause
    exit /b
)

REM === Check for Node.js and npm ===
where npm >nul 2>&1 || (
    echo  Node.js and npm are not installed or not in PATH.
    pause
    exit /b
)

REM === Setup Python virtual environment ===
cd "Backend"
if not exist venv (
    echo  Creating Python virtual environment...
    python -m venv venv
)
call venv\Scripts\activate
echo  Installing Python packages...
pip install --upgrade pip >nul
pip install -r requirements.txt >nul
cd ..

REM === Setup React frontend dependencies ===
cd "Frontend\empathai-ui"
if not exist node_modules (
    echo  Installing npm packages...
    npm install
)
cd ../..

REM === Start Backend ===
start cmd /k "cd Backend && call venv\Scripts\activate && python app.py"

REM === Start Frontend ===
start cmd /k "cd Frontend\\empathai-ui && npm start"

echo  EmpathAI has launched! You can close this window.
