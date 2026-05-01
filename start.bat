@echo off
echo Activating virtual environment...
if not exist "venv\" (
    echo Virtual environment not found. Please run setup first.
    pause
    exit /b
)
call venv\Scripts\activate

echo Starting backend...
start cmd /k uvicorn backend.main:app --reload

echo Starting monitoring system...
start cmd /k python runner.py

echo Opening frontend...
start frontend\index.html

echo System started.
pause
