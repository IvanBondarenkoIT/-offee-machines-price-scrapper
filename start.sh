#!/bin/bash
# Startup script for Railway deployment

# Print environment info for debugging
echo "========================================="
echo "Starting Coffee Price Monitor API"
echo "========================================="
echo "PORT: ${PORT:-8000}"
echo "PYTHON_ENV: ${PYTHON_ENV:-development}"
echo "Working directory: $(pwd)"
echo "Python version: $(python --version)"
echo "========================================="

# Create data directories if they don't exist
mkdir -p /app/data/inbox /app/data/output /app/logs

# Start the FastAPI server
# Railway sets PORT env variable
exec uvicorn api_server:app \
    --host 0.0.0.0 \
    --port ${PORT:-8000} \
    --log-level info \
    --access-log

