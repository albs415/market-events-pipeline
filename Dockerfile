# Use a slim Python base image
FROM python:3.11-slim

# Set working directory inside container
WORKDIR /app

# Copy requirements first (for efficient caching)
COPY requirements.txt ./

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy your source code
COPY etl ./etl
COPY README.md ./README.md

# Ensure output appears instantly (no buffering)
ENV PYTHONUNBUFFERED=1

# Default command (can be overridden in Railway settings)
CMD ["python", "-m", "etl.main"]