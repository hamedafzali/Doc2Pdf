FROM python:3.13-slim

WORKDIR /app

RUN apt-get update && apt-get install -y \
    gcc \
    g++ \
    libffi-dev \
    libssl-dev \
    && rm -rf /var/lib/apt/lists/*

# Copy application code
COPY *.py ./
COPY requirements.txt ./
COPY templates/ ./templates/
COPY static/ ./static/

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Create debug output directory with proper permissions
RUN mkdir -p debug_output && chmod 777 debug_output

# Create non-root user for security
RUN groupadd -r -g docker docker || true && \
    useradd --create-home --shell /bin/bash -G docker appuser && \
    chown -R appuser:appuser /app && \
    chmod 755 /app

USER appuser

# Environment variables
ENV PYTHONPATH=/app
ENV LOG_LEVEL=INFO

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD python -c "import requests; requests.get('http://localhost:5000/api/status')" || \
    python -c "import subprocess; subprocess.run(['pgrep', '-f', 'python'], check=True)" || \
    exit 1

# Default command (can be overridden)
CMD ["python", "web_runner.py"]
