FROM python:3.13-slim

WORKDIR /app

RUN apt-get update && apt-get install -y \
    gcc \
    g++ \
    libffi-dev \
    libssl-dev \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .

RUN pip install --no-cache-dir -r requirements.txt

COPY image_converter.py .
COPY telegram_bot.py .
COPY bot_runner.py .
COPY main.py .

# Create debug output directory with proper permissions
RUN mkdir -p debug_output && chmod 777 debug_output

# Create non-root user for security
RUN useradd --create-home --shell /bin/bash appuser && \
    chown -R appuser:appuser /app && \
    chmod 755 /app
USER appuser

EXPOSE 8080

ENV PYTHONPATH=/app
ENV PYTHONUNBUFFERED=1

HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD python -c "import telegram_bot; print('OK')" || exit 1

CMD ["python", "bot_runner.py"]
