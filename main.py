from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from api.endpoints import router
import os

# Get environment variables or use defaults
PORT = int(os.getenv("PORT", 8000))
ENVIRONMENT = os.getenv("ENVIRONMENT", "development")

# Create FastAPI app
app = FastAPI(
    title="DataForge Backend",
    description="API for data processing, code execution, and visualization",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# Configure CORS
allowed_origins = [
    "http://localhost:3000",  # Local development frontend
    "https://dataforge-app.vercel.app",  # Example production frontend URL
    "https://dataforge-app.onrender.com",  # Example render frontend URL
]

# In production, you might want to add your actual deployed frontend URL
if ENVIRONMENT == "production":
    # Allow all origins in production for flexibility
    # You can replace this with specific domains if needed
    allowed_origins = ["*"]

app.add_middleware(
    CORSMiddleware,
    allow_origins=allowed_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include API routes
app.include_router(router)

# Health check endpoint
@app.get("/health")
async def health_check():
    return {"status": "healthy", "environment": ENVIRONMENT}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=PORT) 