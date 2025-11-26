#!/bin/bash
# TikTok Live Monitor - Stop Script

# Get the directory where the script is located
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
cd "$SCRIPT_DIR"

PID_FILE="$SCRIPT_DIR/tiktok_monitor.pid"

if [ ! -f "$PID_FILE" ]; then
    echo "TikTok Live Monitor is not running (no PID file found)"
    exit 1
fi

PID=$(cat "$PID_FILE")

if ps -p $PID > /dev/null 2>&1; then
    echo "Stopping TikTok Live Monitor (PID: $PID)..."
    kill $PID

    # Wait for process to stop
    for i in {1..10}; do
        if ! ps -p $PID > /dev/null 2>&1; then
            echo "TikTok Live Monitor stopped successfully"
            rm -f "$PID_FILE"
            exit 0
        fi
        sleep 1
    done

    # Force kill if still running
    if ps -p $PID > /dev/null 2>&1; then
        echo "Force stopping..."
        kill -9 $PID
        rm -f "$PID_FILE"
        echo "TikTok Live Monitor force stopped"
    fi
else
    echo "Process not running, removing stale PID file"
    rm -f "$PID_FILE"
fi
