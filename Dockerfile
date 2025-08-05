# Use Python 3.11 slim image
FROM python:3.11-slim

# Set proxy environment variables for build (configurable via GitLab CI/CD variables)
ARG HTTP_PROXY
ARG HTTPS_PROXY
ARG NO_PROXY
ARG http_proxy
ARG https_proxy
ENV HTTP_PROXY=$HTTP_PROXY
ENV HTTPS_PROXY=$HTTPS_PROXY
ENV NO_PROXY=$NO_PROXY
ENV http_proxy=$http_proxy
ENV https_proxy=$https_proxy

# Set working directory
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Install uv package manager
RUN pip install uv

# Copy dependency files
COPY pyproject.toml uv.lock ./

# Install dependencies with retry and longer timeout
RUN uv sync --frozen --timeout 300 || \
    (echo "First attempt failed, retrying..." && sleep 10 && uv sync --frozen --timeout 300) || \
    (echo "Second attempt failed, retrying..." && sleep 30 && uv sync --frozen --timeout 300)

}

# Copy application code
COPY . .

# Install the client module in development mode
RUN uv pip install -e ./mcp_client_tools

# Create data directory for persistent storage
RUN mkdir -p /app/data

# Create non-root user
RUN useradd --create-home --shell /bin/bash app && \
    chown -R app:app /app
USER app

# Expose ports
EXPOSE 9000 9001 9090 8080

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=60s --retries=3 \
    CMD curl -f http://localhost:9000/health || exit 1

# Start all services using the main startup script
CMD ["uv", "run", "python", "start_services.py"] 