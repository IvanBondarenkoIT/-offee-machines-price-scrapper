# Step 2: Add full api_server.py with inventory upload
# Still NO Chrome, NO pandas global import
# Memory: ~100-150MB

FROM python:3.11-slim

WORKDIR /app

# Install minimal system dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    curl \
    ca-certificates \
    && rm -rf /var/lib/apt/lists/*

# Install Python dependencies (NO selenium, NO webdriver-manager, NO Chrome deps)
RUN pip install --no-cache-dir \
    fastapi==0.109.0 \
    uvicorn==0.27.0 \
    pydantic==2.5.3 \
    aiofiles==23.2.1 \
    python-multipart \
    openpyxl==3.1.4 \
    python-docx==1.2.0 \
    beautifulsoup4==4.12.3 \
    lxml==5.3.0 \
    requests==2.31.0 \
    python-dotenv==1.0.1 \
    xlrd>=2.0.1

# pandas installed but imported lazily (only when needed)
RUN pip install --no-cache-dir pandas==2.1.4

# Copy necessary files and folders
COPY api_server.py .
COPY config.py .
COPY scrapers/ ./scrapers/
COPY utils/ ./utils/
COPY run_full_cycle.py .
COPY build_price_comparison.py .
COPY generate_executive_report.py .

# Create directories
RUN mkdir -p /app/data/inbox /app/data/output /app/logs

# Run on port 8080
CMD ["python", "-m", "uvicorn", "api_server:app", "--host", "0.0.0.0", "--port", "8080", "--log-level", "info"]

