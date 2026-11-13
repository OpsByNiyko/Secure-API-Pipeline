FROM python:3.14-slim

# Python runtime configuration
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1

WORKDIR /app

RUN apt-get update \
    && apt-get install -y --no-install-recommends --only-upgrade zlib1g \
    && rm -rf /var/lib/apt/lists/*


# Create a dedicated non-root user and writable data directory
RUN groupadd --system sentinel && \
    useradd --system \
    --gid sentinel \
    --home-dir /app \
    --shell /usr/sbin/nologin \
    sentinel && \
    mkdir -p /app/data && \
    chown -R sentinel:sentinel /app

COPY requirements.txt .

RUN python -m pip install --no-cache-dir --upgrade \
    pip \
    "setuptools>=78.1.1" \
    "msgpack>=1.2.3" \
    "urllib3>=2.8.0" \
    -r requirements.txt \
    && python -m pip check

# Copy application source code
COPY --chown=sentinel:sentinel app/ ./app/

# Run as the dedicated non-root user
USER sentinel

# Document the application port
EXPOSE 8000

# Check application health from inside the container
HEALTHCHECK --interval=30s \
    --timeout=3s \
    --start-period=10s \
    --retries=3 \
    CMD ["python", "-c", "import urllib.request; urllib.request.urlopen('http://127.0.0.1:8000/health', timeout=3)"]

# Start the FastAPI application
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]

