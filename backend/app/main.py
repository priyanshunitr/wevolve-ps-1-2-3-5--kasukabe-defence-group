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
from .routers.job_matching import calculate_match, jobs

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
# Run with: uvicorn app.main:app --reload
# ============================================================

@app.post("/match")
async def match_candidate(candidate_data: dict):
    """
    Match a candidate against all available jobs.
    Expects candidate JSON in the request body.
    """
    # 1. Print visual report to terminal (like loaclly)
    field = candidate_data.get('education', {}).get('field', 'Unknown')
    print(f"\n--- Match Results for {field} Candidate ---")
    print(f"Skills: {', '.join(candidate_data.get('skills', []))}")
    print("-" * 50)

    results = []
    for job in jobs:
        # 2. Call your logic from job_matching.py
        result = calculate_match(candidate_data, job)
        
        # 3. Print details to console
        print(f"Job: {result['job_title']} (ID: {result['job_id']})")
        print(f"Score: {result['match_score']}%")
        print(f"Skill Match: {result['breakdown']['skill_match']}%")
        print(f"Location Match: {result['breakdown']['location_match']}%")
        print(f"Salary Match: {result['breakdown']['salary_match']}%")
        print(f"Experience Match: {result['breakdown']['experience_match']}%")
        print(f"Role Match: {result['breakdown']['role_match']}%")
        if result['missing_skills']:
            print(f"Missing Skills: {', '.join(result['missing_skills'])}")
        print("-" * 30)
        
        results.append(result)
    
    # 4. Sort results by match_score descending for the API response
    results.sort(key=lambda x: x['match_score'], reverse=True)
    
    # 5. Return the JSON result
    return {
        "candidate": candidate_data.get("full_name", "Candidate"),
        "field": field,
        "matches": results
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