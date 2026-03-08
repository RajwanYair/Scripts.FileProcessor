# File Processing Suite - Production Docker Image
# Multi-stage build for optimal image size

# Stage 1: Builder
FROM python:3.11-slim as builder

# Set working directory
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    g++ \
    libmagic1 \
    libmagic-dev \
    && rm -rf /var/lib/apt/lists/*

# Copy project definition and install dependencies
COPY pyproject.toml README.md ./
COPY src/ src/

# Install the package and its dependencies
RUN pip install --no-cache-dir --user .

# Stage 2: Runtime
FROM python:3.11-slim

LABEL maintainer="File Processing Suite Team"
LABEL version="7.0.0"
LABEL description="Enterprise-grade file processing platform with AI/ML capabilities"

# Set environment variables
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PATH=/root/.local/bin:$PATH \
    APP_ENV=production

# Install runtime dependencies
RUN apt-get update && apt-get install -y \
    libmagic1 \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Create app user (security best practice)
RUN useradd -m -u 1000 appuser && \
    mkdir -p /app /app/uploads /app/plugins /app/logs /app/cache && \
    chown -R appuser:appuser /app

# Set working directory
WORKDIR /app

# Copy Python dependencies from builder
COPY --from=builder /root/.local /root/.local

# Copy application code
COPY --chown=appuser:appuser . .

# Switch to non-root user
USER appuser

# Expose ports
EXPOSE 8000 8080

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:8000/health || exit 1

# Default command
CMD ["uvicorn", "file_processor.api.server:app", "--host", "0.0.0.0", "--port", "8000", "--workers", "4"]
