#!/bin/bash
# TikTok Live Streamer Search - Wrapper Script

# Get the directory where the script is located
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
cd "$SCRIPT_DIR"

# Check if virtual environment exists
if [ ! -d "venv" ]; then
    echo "Error: Virtual environment not found!"
    exit 1
fi

# Activate virtual environment
source venv/bin/activate

# Get query from command line or use default
QUERY="${1:-maquillaje}"

# Run the search script
python search_live.py "$QUERY"
