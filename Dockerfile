FROM python:3.13-slim

# Prevent Python from writing .pyc files and enable unbuffered logging
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PYTHONPATH=/app/src

WORKDIR /app

# Install system dependencies (curl for healthchecks, etc.)
RUN apt-get update && apt-get install -y --no-install-recommends \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Install Python dependencies first for caching
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application files and migrations
COPY pyproject.toml README.md alembic.ini ./
COPY src/ ./src/
COPY migrations/ ./migrations/
COPY entrypoint.sh ./

# Install local package in editable mode (ensuring all pyproject.toml dependencies are met)
RUN pip install --no-cache-dir -e .

# Create uploads directory
RUN mkdir -p /app/uploads

# Ensure entrypoint script has LF line endings and is executable
RUN sed -i 's/\r$//' /app/entrypoint.sh && chmod +x /app/entrypoint.sh

# Default port (Render overrides this with $PORT)
EXPOSE 8000

ENTRYPOINT ["/bin/sh", "/app/entrypoint.sh"]
