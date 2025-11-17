# Dockerfile for Lohnkonto Data Extraction Backend
FROM python:3.11-slim

# Install Java Runtime Environment (required for JAR execution)
RUN apt-get update && \
    apt-get install -y --no-install-recommends \
    default-jre-headless \
    && rm -rf /var/lib/apt/lists/*

# Set working directory
WORKDIR /app

# Copy requirements and install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

# Copy application files
COPY api.py .
COPY jar_processor.py .
COPY Lohnkonten-1.0.0.jar .
COPY template.xlsx .

# Create output directory
RUN mkdir -p output

# Set environment variables
ENV PYTHONUNBUFFERED=1 \
    PORT=8000 \
    HOST=0.0.0.0 \
    TEMPLATE_PATH=/app/template.xlsx

# Expose port
EXPOSE 8000

# Run the application
CMD ["sh", "-c", "uvicorn api:app --host 0.0.0.0 --port ${PORT}"]
