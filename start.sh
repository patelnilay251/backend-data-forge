#!/bin/bash
set -e

echo "Starting DataForge Backend API..."

# Create tmp directory if it doesn't exist
mkdir -p /app/tmp

# Start the FastAPI application
exec uvicorn main:app --host 0.0.0.0 --port ${PORT:-8000} --workers 1 