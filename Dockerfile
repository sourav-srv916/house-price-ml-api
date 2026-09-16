# Use a lightweight Python image
FROM python:3.13-slim

# Set the working directory inside the container
WORKDIR /app

# Copy dependency file first
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy the application code and ML model
COPY . .

# Tell Docker that the API uses port 8000
EXPOSE 8000

# Create a shared directory for Prometheus metrics from multiple workers
RUN mkdir -p /tmp/prometheus_multiproc

# Configure Prometheus to use multiprocess metrics mode
ENV PROMETHEUS_MULTIPROC_DIR=/tmp/prometheus_multiproc

# Start the FastAPI application
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000", "--workers", "2"]

# 0.0.0.0 is required so the API listens on all container network
# interfaces and can receive requests forwarded from the host machine.