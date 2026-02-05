"""
Main FastAPI application for SamIT Global educational center management system.
Provides REST API for Telegram Mini App with role-based access control.
"""
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import logging

from app.database import init_database
from routers.auth import router as auth_router
from routers.admin import router as admin_router
from routers.teacher import router as teacher_router
from routers.parent import router as parent_router

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Create FastAPI application
app = FastAPI(
    title="SamIT Global API",
    description="Educational center management system API",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# Configure CORS for Telegram Mini App
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, specify exact domains
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Global exception handler
@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    logger.error(f"Global exception: {exc}")
    return JSONResponse(
        status_code=500,
        content={"detail": "Internal server error"}
    )

# Health check endpoint
@app.get("/health")
async def health_check():
    """Health check endpoint for monitoring"""
    return {"status": "healthy", "service": "SamIT Global API"}

# Include routers
app.include_router(
    auth_router,
    prefix="/api/auth",
    tags=["Authentication"]
)

app.include_router(
    admin_router,
    prefix="/api/admin",
    tags=["Admin Operations"]
)

app.include_router(
    teacher_router,
    prefix="/api/teacher",
    tags=["Teacher Operations"]
)

app.include_router(
    parent_router,
    prefix="/api/parent",
    tags=["Parent Operations"]
)

@app.on_event("startup")
async def startup_event():
    """Initialize database on startup"""
    logger.info("Starting SamIT Global API...")
    init_database()
    logger.info("API startup completed")

@app.on_event("shutdown")
async def shutdown_event():
    """Cleanup on shutdown"""
    logger.info("Shutting down SamIT Global API...")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    )
