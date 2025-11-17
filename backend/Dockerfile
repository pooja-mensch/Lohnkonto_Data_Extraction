# Dockerfile for Lohnkonto Data Extraction Backend
# Multi-stage build for optimized image size

# Stage 1: Base image with Python and Java
FROM python:3.11-slim as base

# Install Java Runtime (required for JAR execution)
RUN apt-get update && \
    apt-get install -y --no-install-recommends \
    default-jre-headless \
    && rm -rf /var/lib/apt/lists/*

# Set working directory
WORKDIR /app

# Stage 2: Dependencies
FROM base as dependencies

# Copy requirements first for better caching
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Stage 3: Final image
FROM base

# Copy Python dependencies from previous stage
COPY --from=dependencies /usr/local/lib/python3.11/site-packages /usr/local/lib/python3.11/site-packages
COPY --from=dependencies /usr/local/bin /usr/local/bin

# Set working directory
WORKDIR /app

# Copy application files
COPY api.py .
COPY jar_processor.py .
COPY Lohnkonten-1.0.0.jar .
COPY template.xlsx .
COPY requirements.txt .

# Create output directory
RUN mkdir -p output

# Set environment variables
ENV PYTHONUNBUFFERED=1
ENV PORT=8000
ENV HOST=0.0.0.0
ENV TEMPLATE_PATH=/app/template.xlsx

# Expose port
EXPOSE 8000

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
  CMD python -c "import requests; requests.get('http://localhost:8000/health')" || exit 1

# Run the application
CMD uvicorn api:app --host 0.0.0.0 --port ${PORT}
