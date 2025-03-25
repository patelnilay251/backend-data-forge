# DataForge Backend Deployment Guide

This guide provides instructions for deploying the DataForge backend to Render using Docker.

## Docker Setup

We've containerized the application with the following files:

- `Dockerfile` - Defines how to build the Docker image
- `docker-compose.yml` - For local development and testing
- `start.sh` - Entrypoint script for the container
- `.dockerignore` - Excludes unnecessary files from the build
- `.env.example` - Example environment variables

## Deployment to Render

### Option 1: Using Render Dashboard (UI)

1. **Push to a Git Repository**
   - Push your code to GitHub, GitLab, or another Git provider

2. **Create a New Web Service on Render**
   - Log in to your Render account
   - Click "New +" and select "Web Service"
   - Connect your Git repository
   - Choose the repository and branch

3. **Configure the Service**
   - Select "Docker" as the runtime
   - Set the following configuration:
     - Name: dataforge-backend (or your preferred name)
     - Environment: Docker
     - Region: Choose the one closest to your users
     - Branch: main (or your deployment branch)
     - Health Check Path: /health

4. **Set Environment Variables**
   - Add the following environment variables:
     - `ENVIRONMENT`: production
     - `PORT`: 8000 (Render may set this automatically)

5. **Deploy**
   - Click "Create Web Service"
   - Render will build and deploy your Docker image

### Option 2: Using Infrastructure as Code (render.yaml)

1. **Use the provided render.yaml file**
   The repository includes a `render.yaml` file that defines the service configuration.

2. **Deploy via Render Blueprint**
   - Push your code to a Git repository
   - In Render, click "New +" and select "Blueprint"
   - Connect your Git repository
   - Render will detect the render.yaml file and propose the defined services
   - Review and deploy

## Updating Your Deployment

To update your deployment:

1. Push changes to your Git repository
2. Render will automatically detect changes and rebuild/redeploy

## Monitoring and Logs

- Access logs and metrics from the Render dashboard
- Use the `/health` endpoint to check service status

## Connecting Your Frontend

Update your frontend to use the Render deployment URL:

```javascript
// In your frontend code
const API_BASE_URL = "https://your-app-name.onrender.com";
```

Ensure CORS is properly configured in the backend to allow requests from your frontend domain. 