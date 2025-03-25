#!/bin/bash
set -e

echo "Starting DataForge Backend API..."
echo "Python version: $(python --version)"
echo "Pandas version: $(python -c 'import pandas; print(pandas.__version__)')"

# Create tmp directory if it doesn't exist
mkdir -p /app/tmp

# Log configuration
echo "Environment: ${ENVIRONMENT:-development}"
echo "Port: ${PORT:-8000}"

# Check for installed dependencies
echo "Checking installed dependencies..."
pip list

# Start the FastAPI application
echo "Starting Uvicorn server..."
exec uvicorn main:app --host 0.0.0.0 --port ${PORT:-8000} --workers 1 --log-level info 