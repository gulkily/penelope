#!/usr/bin/env bash

# Exit immediately if a command exits with a non-zero status, 
#undefined variable is used, or a command in a pipeline fails
set -euo pipefail

# Start the FastAPI server with auto-reload enabled for local development
exec uvicorn app.main:app --reload
