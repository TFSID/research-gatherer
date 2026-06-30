# ===================================================================
# Research Gatherer — Multi-stage Dockerfile
# ===================================================================
# Build:  docker build -t research-gatherer .
# Run:    docker run -p 8000:8000 --env-file .env research-gatherer
# ===================================================================

# ---------- Stage 1: Builder ----------
FROM python:3.12-slim AS builder

WORKDIR /build

# Install build dependencies for lxml, Pillow, etc.
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    g++ \
    libxml2-dev \
    libxslt1-dev \
    zlib1g-dev \
    libjpeg-dev \
    libpng-dev \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --no-cache-dir --prefix=/install -r requirements.txt


# ---------- Stage 2: Runtime ----------
FROM python:3.12-slim AS runtime

LABEL maintainer="Infradyne Research"
LABEL description="Research Gatherer — OpenAI-compatible API server with multi-engine search"
LABEL version="2.0.0"

# Install runtime dependencies
# - libxml2/libxslt for lxml (used by BeautifulSoup)
# - curl for healthcheck
# - chromium + chromedriver for Selenium-based engines (optional)
RUN apt-get update && apt-get install -y --no-install-recommends \
    libxml2 \
    libxslt1.1 \
    libjpeg62-turbo \
    libpng16-16 \
    curl \
    chromium \
    chromium-driver \
    fonts-liberation \
    libnss3 \
    libatk-bridge2.0-0 \
    libgtk-3-0 \
    libgbm1 \
    && rm -rf /var/lib/apt/lists/*

# Copy installed Python packages from builder
COPY --from=builder /install /usr/local

# Create non-root user
RUN groupadd -r research && useradd -r -g research -d /app -s /sbin/nologin research

WORKDIR /app

# Copy application code
COPY ai_api.py .
COPY research_gatherer.py .
COPY image_gatherer.py .
COPY app_logger.py .

# Copy modules
COPY utils/ ./utils/
COPY engines/ ./engines/
COPY engines_image/ ./engines_image/
COPY libs/ ./libs/
COPY cookie/ ./cookie/

# Create output directory and set ownership
RUN mkdir -p /app/research_output \
    && chown -R research:research /app

# Switch to non-root user
USER research

# Environment defaults (override via .env or -e flags)
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    RESEARCH_HOST=0.0.0.0 \
    RESEARCH_PORT=8000 \
    RESEARCH_OUTPUT_DIR=/app/research_output \
    RESEARCH_PARSE_WORKERS=4 \
    RESEARCH_JINA_TIMEOUT=30 \
    RESEARCH_RATE_LIMIT=0.5 \
    # Selenium/Chromium settings for headless mode
    CHROME_BIN=/usr/bin/chromium \
    CHROMEDRIVER_PATH=/usr/bin/chromedriver \
    DISPLAY=""

EXPOSE 8000

HEALTHCHECK --interval=30s --timeout=5s --start-period=10s --retries=3 \
    CMD curl -f http://localhost:8000/health || exit 1

ENTRYPOINT ["python", "ai_api.py"]
CMD ["--host", "0.0.0.0", "--port", "8000"]
