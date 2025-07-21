# SharePoint Tool Foundry - Dockerfile
# Multi-stage build for optimized container size

FROM python:3.11-slim as builder

# Set working directory
WORKDIR /app

# Install system dependencies for building
RUN apt-get update && apt-get install -y \
    gcc \
    g++ \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements and install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir --user -r requirements.txt

# Production stage
FROM python:3.11-slim

# Set working directory
WORKDIR /app

# Create non-root user for security
RUN groupadd -r appuser && useradd -r -g appuser appuser

# Copy installed packages from builder stage
COPY --from=builder /root/.local /home/appuser/.local

# Copy application code
COPY . .

# Set ownership and permissions
RUN chown -R appuser:appuser /app
USER appuser

# Add local packages to PATH
ENV PATH=/home/appuser/.local/bin:$PATH

# Set Python path
ENV PYTHONPATH=/app

# Create logs directory
RUN mkdir -p logs

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD python -c "import config; config.Config()" || exit 1

# Default command
CMD ["python", "sharepoint_agent.py"]

# Labels
LABEL name="sharepoint-tool-foundry"
LABEL version="1.0.0"
LABEL description="Azure AI Foundry agent with SharePoint integration"
LABEL maintainer="SharePoint Tool Foundry Team"
