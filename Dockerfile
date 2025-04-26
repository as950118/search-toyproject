# syntax=docker/dockerfile:1

FROM python:3.9-slim

WORKDIR /app

# (Optional) Install system dependencies
# RUN apt-get update && apt-get install -y build-essential

# Copy requirements if you have them
COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

# Copy the rest of your application code
COPY . .

# Default command (can be overridden by docker-compose)
CMD ["uvicorn", "backend.main:app", "--host", "0.0.0.0", "--port", "8080"]