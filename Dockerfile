FROM python:3.10-slim

WORKDIR /app

# System dependencies for pandas and other numeric libraries
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements first for better layer caching
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy the rest of the application
COPY . .

# Create tmp directory if it doesn't exist
RUN mkdir -p tmp

# Make the start script executable
RUN chmod +x start.sh

# Expose the port the app runs on
EXPOSE 8000

# Use the start script as entrypoint
ENTRYPOINT ["/app/start.sh"] 