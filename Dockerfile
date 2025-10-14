# Dockerfile for Coffee Price Monitoring API
# Optimized for Railway.com deployment

FROM python:3.11-slim

# Set environment variables
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    DEBIAN_FRONTEND=noninteractive \
    CHROME_VERSION=120.0.6099.109

# Install system dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    # Chrome dependencies
    wget \
    gnupg \
    gpg \
    unzip \
    curl \
    ca-certificates \
    fonts-liberation \
    libasound2 \
    libatk-bridge2.0-0 \
    libatk1.0-0 \
    libatspi2.0-0 \
    libcups2 \
    libdbus-1-3 \
    libdrm2 \
    libgbm1 \
    libgtk-3-0 \
    libnspr4 \
    libnss3 \
    libwayland-client0 \
    libxcomposite1 \
    libxdamage1 \
    libxfixes3 \
    libxkbcommon0 \
    libxrandr2 \
    xdg-utils \
    # Additional utilities
    && rm -rf /var/lib/apt/lists/*

# Install Google Chrome (modern method without apt-key)
RUN wget -q -O /tmp/google-chrome-key.pub https://dl-ssl.google.com/linux/linux_signing_key.pub \
    && gpg --dearmor -o /usr/share/keyrings/google-chrome-keyring.gpg /tmp/google-chrome-key.pub \
    && echo "deb [arch=amd64 signed-by=/usr/share/keyrings/google-chrome-keyring.gpg] http://dl.google.com/linux/chrome/deb/ stable main" > /etc/apt/sources.list.d/google-chrome.list \
    && apt-get update \
    && apt-get install -y google-chrome-stable \
    && rm -rf /var/lib/apt/lists/* /tmp/google-chrome-key.pub

# Install ChromeDriver
RUN CHROMEDRIVER_VERSION=$(curl -sS chromedriver.storage.googleapis.com/LATEST_RELEASE) && \
    wget -O /tmp/chromedriver.zip https://chromedriver.storage.googleapis.com/$CHROMEDRIVER_VERSION/chromedriver_linux64.zip && \
    unzip /tmp/chromedriver.zip chromedriver -d /usr/local/bin/ && \
    chmod +x /usr/local/bin/chromedriver && \
    rm /tmp/chromedriver.zip

# Verify Chrome and ChromeDriver installation
RUN google-chrome --version && chromedriver --version

# Create app user (security best practice)
RUN useradd -m -u 1000 appuser && \
    mkdir -p /app && \
    chown appuser:appuser /app

# Set working directory
WORKDIR /app

# Copy requirements first for better caching
COPY requirements.railway.txt requirements.txt

# Install Python dependencies
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY --chown=appuser:appuser . .

# Create necessary directories
RUN mkdir -p data/output data/inbox logs && \
    chown -R appuser:appuser data logs

# Switch to non-root user
USER appuser

# Expose port (Railway uses 8080 by default)
# Note: Railway ignores EXPOSE, uses PORT env variable
EXPOSE 8080

# Health check (disabled for Railway - they handle it differently)
# HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
#     CMD curl -f http://localhost:${PORT:-8080}/health || exit 1

# Run FastAPI server directly (simplified for Railway)
# Use shell form to support echo and shell commands
CMD echo "========== Starting Coffee Price Monitor API ==========" && \
    echo "Working directory: $(pwd)" && \
    echo "Files in /app:" && ls -la /app | head -20 && \
    echo "Python version:" && python --version && \
    echo "Checking api_server.py:" && ls -la api_server.py && \
    echo "Testing Python import:" && python -c "import sys; print('Python executable:', sys.executable)" && \
    echo "Testing api_server import:" && python -c "import api_server; print('api_server imported successfully')" && \
    echo "Starting uvicorn on port 8080..." && \
    exec python -m uvicorn api_server:app --host 0.0.0.0 --port 8080 --log-level debug

