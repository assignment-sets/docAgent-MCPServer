FROM python:3.11-slim

# Set working directory
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    g++ \
    libglib2.0-0 \
    && rm -rf /var/lib/apt/lists/*

# Install Python packages
RUN pip install --no-cache-dir \
    numpy \
    pandas \
    matplotlib \
    seaborn \
    scipy \
    sympy \
    scikit-learn \
    watchdog \
    boto3 \
    python-dotenv \
    requests

COPY watcher.py /app/watcher.py
COPY entrypoint.sh /app/entrypoint.sh
RUN chmod +x /app/entrypoint.sh

RUN useradd -m -u 1000 sandboxuser && \
    chown -R sandboxuser:sandboxuser /app

USER sandboxuser

ENTRYPOINT ["/bin/bash", "/app/entrypoint.sh"]