#!/usr/bin/env bash

# Exit immediately if a command exits with a non-zero status, 
#undefined variable is used, or a command in a pipeline fails
set -euo pipefail

# Hide ^C echo when stopping the server, restore on exit.
if [[ -t 0 ]]; then
  stty -echoctl
  trap 'stty echoctl' EXIT
fi

# Start the FastAPI server with auto-reload enabled for local development
exec uvicorn app.main:app --reload
