#!/bin/bash
# TikTok Live Monitor - Start in Background

# Get the directory where the script is located
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
cd "$SCRIPT_DIR"

# PID file
PID_FILE="$SCRIPT_DIR/tiktok_monitor.pid"

# Check if already running
if [ -f "$PID_FILE" ]; then
    PID=$(cat "$PID_FILE")
    if ps -p $PID > /dev/null 2>&1; then
        echo "TikTok Live Monitor is already running (PID: $PID)"
        exit 1
    else
        echo "Removing stale PID file..."
        rm -f "$PID_FILE"
    fi
fi

# Check if virtual environment exists
if [ ! -d "venv" ]; then
    echo "Error: Virtual environment not found!"
    exit 1
fi

# Activate virtual environment and start
source venv/bin/activate

# Start in background
nohup python main.py > tiktok_monitor.log 2>&1 &
PID=$!

# Save PID
echo $PID > "$PID_FILE"

echo "TikTok Live Monitor started in background (PID: $PID)"
echo "Log file: tiktok_monitor.log"
echo ""
echo "To stop: ./stop.sh"
echo "To view logs: tail -f tiktok_monitor.log"
