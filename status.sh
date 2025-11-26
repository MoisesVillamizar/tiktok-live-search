#!/bin/bash
# TikTok Live Monitor - Status Script

# Get the directory where the script is located
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
cd "$SCRIPT_DIR"

PID_FILE="$SCRIPT_DIR/tiktok_monitor.pid"

echo "==================================================="
echo "TikTok Live Monitor - Status"
echo "==================================================="

if [ -f "$PID_FILE" ]; then
    PID=$(cat "$PID_FILE")

    if ps -p $PID > /dev/null 2>&1; then
        echo "Status: RUNNING ✓"
        echo "PID: $PID"
        echo ""

        # Show process info
        echo "Process Info:"
        ps -p $PID -o pid,ppid,user,%cpu,%mem,etime,command

        echo ""
        echo "Server URL: http://localhost:8000"
        echo "Health Check: http://localhost:8000/health"
        echo "API Docs: http://localhost:8000/docs"
        echo ""
        echo "Log file: tail -f tiktok_monitor.log"

        # Try to get health status
        echo ""
        echo "Health Status:"
        curl -s http://localhost:8000/health 2>/dev/null | python3 -m json.tool 2>/dev/null || echo "Server not responding to HTTP requests"
    else
        echo "Status: NOT RUNNING ✗"
        echo "PID file exists but process is not running"
        echo "Run: ./start-background.sh to start"
    fi
else
    echo "Status: NOT RUNNING ✗"
    echo "No PID file found"
    echo "Run: ./start-background.sh to start"
fi

echo "==================================================="
