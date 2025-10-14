# MINIMAL TEST DOCKERFILE for Railway
# No Chrome, no Selenium, no pandas - just FastAPI!

FROM python:3.11-slim

WORKDIR /app

# Install ONLY FastAPI and Uvicorn (minimal dependencies)
RUN pip install --no-cache-dir \
    fastapi==0.109.0 \
    uvicorn==0.27.0

# Copy ONLY minimal app
COPY api_minimal.py .

# Run on port 8080 (Railway default)
CMD ["python", "-m", "uvicorn", "api_minimal:app", "--host", "0.0.0.0", "--port", "8080", "--log-level", "info"]

