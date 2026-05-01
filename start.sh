#!/bin/bash

# Check if venv exists
if [ ! -d "venv" ]; then
    echo "Virtual environment not found. Please run setup first."
    exit 1
fi

source venv/bin/activate

echo "Starting backend..."
uvicorn backend.main:app --reload &

echo "Starting monitoring..."
python3 runner.py &

echo "Opening frontend..."
# Try xdg-open (Linux) then open (Mac)
if command -v xdg-open > /dev/null; then
    xdg-open frontend/index.html
elif command -v open > /dev/null; then
    open frontend/index.html
else
    echo "Please open frontend/index.html manually in your browser."
fi

echo "Sentinel system started. Press Ctrl+C to stop all processes."
wait
