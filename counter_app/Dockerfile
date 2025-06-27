# Use Python 3.11 slim image
FROM python:3.11-slim

# Set working directory
WORKDIR /app

# Install minimal system dependencies
RUN apt-get update && apt-get install -y \
    libglib2.0-0 \
    libgomp1 \
    python3-opencv \
    && rm -rf /var/lib/apt/lists/*

# Install uv for faster Python package management
RUN pip install --no-cache-dir uv

# Copy requirements and install Python dependencies with uv
COPY requirements.txt .
RUN uv pip install --system --no-cache -r requirements.txt

# Copy application files
COPY app.py .
COPY centroid_tracker.py .
COPY config.py .
COPY helper.py .
COPY zone_setup.py .
COPY config.yaml .
COPY model_data/ ./model_data/

# Create directories for input/output
RUN mkdir -p /app/input /app/output /app/logs

# Set environment variables
ENV PYTHONUNBUFFERED=1
ENV OPENCV_LOG_LEVEL=ERROR

# Create a non-root user
RUN useradd -m -u 1000 appuser && chown -R appuser:appuser /app
USER appuser

# Default command
CMD ["python", "app.py", "--help"]
