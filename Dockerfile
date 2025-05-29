# Use official Python base image
FROM python:3.11

# Set working directory
WORKDIR /app

# Copy all project files into the container
COPY . /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    build-essential \
    curl \
    git \
    && rm -rf /var/lib/apt/lists/*

# Install Python dependencies
RUN pip install --upgrade pip
RUN pip install --no-cache-dir -r requirements.txt

# Ensure strategies directory exists and is accessible
RUN mkdir -p /app/strategies/symbol_specific /app/strategies/experimental

# Default command
CMD ["python", "main.py"]