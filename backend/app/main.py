"""
Wevolve API - Main Entry Point
The AI-Powered Career Acceleration Ecosystem

Three Core Modules:
1. Resume Intelligence - Parse and score resumes
2. Transparent Matching - Multi-factor job matching with explanations
3. Actionable Growth - Personalized learning roadmaps
"""
import json
from pathlib import Path
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from .config import settings
from .db import init_db
from .routers import resume, matching, roadmap

# ============================================================
# Application Setup
# ============================================================

app = FastAPI(
    title=settings.APP_NAME,
    description=settings.APP_DESCRIPTION,
    version=settings.APP_VERSION,
    docs_url="/docs",
    redoc_url="/redoc"
)

# CORS Configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include Routers
app.include_router(resume.router)
app.include_router(matching.router)
app.include_router(roadmap.router)


# ============================================================
# Lifecycle Events
# ============================================================

@app.on_event("startup")
async def startup_event():
    """Initialize database on application startup."""
    print("🚀 Wevolve API Starting...")
    init_db()
    print("✅ Database initialized successfully!")


# ============================================================
# Health Check Endpoints
# ============================================================

@app.get("/")
async def root():
    """Root endpoint - health check."""
    try:
        return {
            "status": "ok",
            "message": "Wevolve API is running",
            "version": settings.APP_VERSION
        }
    except Exception as e:
        return {
            "status": "error",
            "message": f"Health check failed: {str(e)}"
        }


@app.get("/health")
async def health_check():
    """Detailed health check with database connectivity test."""
    try:
        from .db import SessionLocal
        db = SessionLocal()
        db.execute("SELECT 1")
        db.close()
        
        return {
            "status": "ok",
            "message": "All systems operational",
            "database": "connected"
        }
    except Exception as e:
        return {
            "status": "error",
            "message": "Health check failed",
            "error": str(e),
            "database": "disconnected"
        }


# ============================================================
# Jobs API
# ============================================================

@app.get("/api/jobs")
async def get_jobs():
    """
    Return all available jobs from the jobs.json file.
    """
    jobs_file = Path(__file__).parent.parent / "data" / "jobs.json"
    
    try:
        with open(jobs_file, 'r') as f:
            data = json.load(f)
            return {"jobs": data.get('jobs', [])}
    except FileNotFoundError:
        return {"jobs": []}