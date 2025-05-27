@echo off
echo Starting EmpathAI...


start cmd /k "cd Backend && python app.py"


start cmd /k "cd Frontend\empathai-ui && npm start"

echo Backend and frontend launched in separate terminals.
