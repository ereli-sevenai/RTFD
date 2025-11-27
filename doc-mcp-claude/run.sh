#!/bin/bash
# Startup script for Documentation Gateway MCP Server

# Activate virtual environment
source venv/bin/activate

# Load environment variables
if [ -f .env ]; then
    export $(cat .env | grep -v '^#' | xargs)
fi

# Run the server
python server.py
