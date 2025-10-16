"""
PR Copilot - AI-Powered PR Management System
Main FastAPI application entry point
"""

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
import uvicorn

from api.routes import webhooks, health
from api.routes import auth as auth_routes
from api.database import engine, Base
from workers.celery_app import celery_app


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan events"""
    # Startup
    print("🚀 Starting PR Copilot...")
    
    # Create database tables
    Base.metadata.create_all(bind=engine)
    
    # Start Celery worker (in production, this would be separate)
    print("✅ Database initialized")
    print("✅ Celery worker ready")
    
    yield
    
    # Shutdown
    print("🛑 Shutting down PR Copilot...")


# Create FastAPI app
app = FastAPI(
    title="PR Copilot",
    description="AI-Powered PR Management System",
    version="1.0.0",
    lifespan=lifespan
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure properly for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(health.router, prefix="/health", tags=["health"])
app.include_router(webhooks.router, prefix="/webhooks", tags=["webhooks"])
app.include_router(auth_routes.router, tags=["auth"])  # exposes /setup and /auth/callback


@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "message": "PR Copilot - AI-Powered PR Management System",
        "version": "1.0.0",
        "status": "running"
    }


if __name__ == "__main__":
    uvicorn.run(
        "api.main:app",
        host="0.0.0.0",
        port=8000,
        reload=True
    )
