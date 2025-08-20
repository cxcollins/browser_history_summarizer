FROM python:3.12-slim

WORKDIR /app

RUN apt-get update && apt-get install -y \
    build-essential \
    curl \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy all application code (maintains directory structure)
COPY . .

# Create data directory for shared database
RUN mkdir -p /app/data

# Set Python path
ENV PYTHONPATH=/app

CMD ["python", "backend/worker.py"]
