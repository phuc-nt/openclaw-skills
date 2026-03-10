#!/bin/bash
# Wrapper script for goodreads-writer.py with flexible venv support
# Usage: ./goodreads-write.sh <command> [args...]
# Example: ./goodreads-write.sh rate 40121378 5

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
WRITER="$SCRIPT_DIR/goodreads-writer.py"

# Venv priority: 1) GR_VENV env var  2) co-located .venv  3) system python
if [ -n "$GR_VENV" ] && [ -d "$GR_VENV" ]; then
    source "$GR_VENV/bin/activate"
elif [ -d "$SCRIPT_DIR/.venv" ]; then
    source "$SCRIPT_DIR/.venv/bin/activate"
fi

python3 "$WRITER" "$@"
