# Base image
FROM python:3.10-slim

# Set workdir
WORKDIR /app

# Copy all project files
COPY . .

# Install dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Make start.sh executable
RUN chmod +x start.sh

# Expose Render's port
EXPOSE 8000

# Run both backend and frontend
CMD ["./start.sh"]
