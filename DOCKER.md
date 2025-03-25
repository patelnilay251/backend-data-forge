# DataForge Backend - Docker Guide

This guide explains how to build and run the DataForge backend API using Docker.

## Prerequisites

- Docker installed on your system
- Docker Compose (optional, for local development)

## Building the Docker Image

To build the Docker image:

```bash
docker build -t dataforge-backend .
```

## Running the Container

### Using Docker directly

```bash
docker run -p 8000:8000 dataforge-backend
```

### Using Docker Compose (local development)

```bash
docker-compose up
```

## Deployment on Render

To deploy on Render:

1. Push your Docker image to a container registry (Docker Hub, GitHub Container Registry, etc.)
2. In Render, create a new Web Service and select "Docker" as your runtime
3. Link to your container registry
4. Set the following environment variables if needed:
   - `PORT`: Port for the application (Render will automatically set this)

## Environment Variables

The application supports the following environment variables:

- `PORT`: The port the application will listen on (default: 8000)

## Image Structure

The Docker image includes:

- Python 3.10 as the base image
- FastAPI application code
- All dependencies specified in requirements.txt
- A startup script (start.sh)

## Volumes

If running locally with Docker Compose, the `./tmp` directory is mounted into the container for data persistence.

## API Documentation

Once the container is running, API documentation is available at:

- Swagger UI: `http://localhost:8000/docs`
- ReDoc: `http://localhost:8000/redoc` 