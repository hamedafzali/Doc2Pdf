FROM python:3.13-slim

WORKDIR /app

RUN apt-get update && apt-get install -y \
    gcc \
    g++ \
    libffi-dev \
    libssl-dev \
    libreoffice \
    fonts-dejavu-core \
    wkhtmltopdf \
    qpdf \
    tesseract-ocr \
    tesseract-ocr-deu \
    tesseract-ocr-fas \
    ghostscript \
    && rm -rf /var/lib/apt/lists/*

# Copy application files
COPY requirements.txt ./
COPY *.py ./

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Create debug output directory with proper permissions
RUN mkdir -p debug_output && chmod 777 debug_output

# Create non-root user for security
RUN useradd --create-home --shell /bin/bash appuser && \
    chown -R appuser:appuser /app && \
    chmod 755 /app

USER appuser

# Environment variables
ENV PYTHONPATH=/app
ENV LOG_LEVEL=INFO

# Default command
CMD ["python", "bot_runner.py"]
