# 121AI Production Docker Image
# Universal AI Orchestration Platform

FROM python:3.11-slim as builder

WORKDIR /build

# Install build dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    g++ \
    make \
    libssl-dev \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements
COPY requirements.txt .

# Build Python dependencies
RUN pip install --user --no-cache-dir -r requirements.txt


# Production image
FROM python:3.11-slim

LABEL maintainer="121 Group <support@121.us>"
LABEL version="1.0.0"
LABEL description="121AI - Universal AI Orchestration Platform"

# Set environment variables
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    121AI_ENV=production \
    121AI_PORT=8000 \
    121AI_WORKERS=4

# Create non-root user
RUN groupadd -r 121ai && useradd -r -g 121ai 121ai

WORKDIR /app

# Install runtime dependencies
RUN apt-get update && apt-get install -y \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Copy Python dependencies from builder
COPY --from=builder /root/.local /home/121ai/.local

# Copy application
COPY --chown=121ai:121ai . .

# Add to PATH
ENV PATH=/home/121ai/.local/bin:$PATH

# Switch to non-root user
USER 121ai

# Health check
HEALTHCHECK --interval=30s --timeout=3s --start-period=40s --retries=3 \
    CMD curl -f http://localhost:${121AI_PORT}/health || exit 1

# Expose port
EXPOSE 8000

# Run application
CMD ["python", "-m", "121ai.main", "--port", "8000", "--workers", "4"]
