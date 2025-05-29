@echo off
cd /d %~dp0
echo Starting EmpathAI...

REM === Check for Python ===
where python >nul 2>&1 || (
    echo Python is not installed or not in PATH.
    pause
    exit /b
)

REM === Check for Node.js and npm ===
where npm >nul 2>&1 || (
    echo Node.js and npm are not installed or not in PATH.
    pause
    exit /b
)

REM === Backend Setup ===
cd Backend

IF NOT EXIST venv (
    echo Creating virtual environment...
    python -m venv venv
)

call venv\Scripts\activate

IF EXIST requirements.txt (
    echo Installing Python requirements...
    pip install -r requirements.txt
)

cd ..

REM === Frontend Setup ===
cd Frontend

IF NOT EXIST node_modules (
    echo Installing frontend npm packages...
    npm install
)

cd ..

REM === Launch Backend in new terminal ===
start cmd /k "cd Backend && call venv\Scripts\activate && python app.py"

REM === Launch Frontend in new terminal ===
start cmd /k "cd Frontend && npm start"

echo All systems go! You can close this window if needed.
