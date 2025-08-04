#!/bin/bash

# Send message to LLM agent in tmux window via llm_handler.py
# Usage: send-claude-message.sh <session:window> <message>
# Note: This script now uses the multi-LLM handler instead of direct Claude API

if [ $# -lt 2 ]; then
    echo "Usage: $0 <session:window> <message>"
    echo "Example: $0 agentic-seek:3 'Hello LLM!'"
    exit 1
fi

WINDOW="$1"
shift  # Remove first argument, rest is the message
MESSAGE="$*"

# Get the directory where this script is located
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

# Execute the Python handler and capture its output
LLM_RESPONSE=$(python3 "$SCRIPT_DIR/llm_handler.py" "$WINDOW" "$MESSAGE")

# Send the LLM's response back to the tmux window
tmux send-keys -t "$WINDOW" "$LLM_RESPONSE"

# Wait 0.5 seconds for UI to register
sleep 0.5

# Send Enter to submit the response
tmux send-keys -t "$WINDOW" Enter

echo "Message sent to LLM via $WINDOW. Response received and sent back to tmux."