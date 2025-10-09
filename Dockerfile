FROM python:3.10-slim

# Install dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential gcc g++ && \
    rm -rf /var/lib/apt/lists/*

# Set working directory
WORKDIR /app

# Copy requirements first
COPY requirements.txt /app/

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy the rest of the project
COPY . /app

# Make start script executable
RUN chmod +x /app/start.sh

# Expose ports
EXPOSE 8000 8501

# Run both backend and frontend
ENTRYPOINT ["/app/start.sh"]
