# Dockerfile for GPX Art Generator API
#
# This multi-stage build creates an optimized Docker image for the FastAPI backend
# that integrates with the GPX Art Generator CLI tool.

# Stage 1: Builder - Install dependencies and prepare application
FROM python:3.11-slim AS builder

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1

# Set working directory
WORKDIR /app

# Install system dependencies needed for building Python packages
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    gcc \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

# Install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

# Stage 2: Final image
FROM python:3.11-slim

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    APP_HOME=/app \
    PATH="/app/cli:${PATH}" \
    TZ=UTC

# Set working directory
WORKDIR ${APP_HOME}

# Create a non-root user to run the application
RUN addgroup --system app && \
    adduser --system --ingroup app app && \
    mkdir -p ${APP_HOME}/uploads ${APP_HOME}/output ${APP_HOME}/logs && \
    chown -R app:app ${APP_HOME}

# Install system dependencies needed for runtime
RUN apt-get update && apt-get install -y --no-install-recommends \
    libcairo2 \
    libpango-1.0-0 \
    libpangocairo-1.0-0 \
    libgdk-pixbuf2.0-0 \
    libffi-dev \
    shared-mime-info \
    curl \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

# Copy Python dependencies from builder stage
COPY --from=builder /usr/local/lib/python3.11/site-packages /usr/local/lib/python3.11/site-packages
COPY --from=builder /usr/local/bin /usr/local/bin

# Copy application code
COPY . ${APP_HOME}/

# Install the GPX Art CLI tool from the project
RUN pip install -e ../cli/

# Set proper permissions
RUN chown -R app:app ${APP_HOME}

# Switch to non-root user
USER app

# Health check
HEALTHCHECK --interval=30s --timeout=30s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:8000/ || exit 1

# Expose the application port
EXPOSE 8000

# Start the application with uvicorn
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]

