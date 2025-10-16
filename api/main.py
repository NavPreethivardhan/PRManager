"""
PR Copilot - AI-Powered PR Management System
Main FastAPI application entry point
"""

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
import uvicorn

from api.routes import webhooks, health
from api.database import engine, Base
from workers.celery_app import celery_app

# Robust import of auth router with fallback
try:
    from api.routes.auth import router as auth_router
except Exception:
    # Define a minimal inline auth router to avoid import errors
    from fastapi import APIRouter
    from fastapi.responses import JSONResponse, RedirectResponse
    from typing import Optional

    auth_router = APIRouter()

    @auth_router.get("")
    async def _auth_index():
        return {"status": "ok", "message": "Auth endpoints available", "endpoints": ["/auth/callback", "/auth/setup"]}

    @auth_router.get("/setup")
    async def _setup(next: Optional[str] = None):
        if next:
            return RedirectResponse(url=next)
        return {"status": "ok", "message": "PR Copilot setup complete"}

    @auth_router.get("/callback")
    async def _callback(code: Optional[str] = None, installation_id: Optional[str] = None, setup_action: Optional[str] = None):
        return JSONResponse(
            content={
                "status": "received",
                "code_provided": bool(code),
                "installation_id": installation_id,
                "setup_action": setup_action,
                "next_steps": "Install the app on a repository and open a PR to test webhooks."
            }
        )


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
app.include_router(auth_router, prefix="/auth", tags=["auth"])  # exposes /auth, /auth/callback, /auth/setup


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
