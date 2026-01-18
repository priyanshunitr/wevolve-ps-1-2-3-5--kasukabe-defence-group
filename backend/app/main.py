"""
Wevolve API - Main Entry Point
The AI-Powered Career Acceleration Ecosystem

Three Core Modules:
1. Resume Intelligence - Parse and score resumes
2. Transparent Matching - Multi-factor job matching with explanations
3. Actionable Growth - Personalized learning roadmaps
"""
<<<<<<< HEAD
from typing import Optional, List
=======
>>>>>>> main
import json
from pathlib import Path
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

<<<<<<< HEAD
from fastapi import FastAPI, HTTPException, UploadFile, File, Depends, Body
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from sqlalchemy.orm import Session
from . import models

from .database import init_db, get_db

# Import routers
from .routers import resume, matching, roadmap
from .skill_score import calculate_match
=======
from .config import settings
from .db import init_db
from .routers import resume, matching, roadmap, auth

# ============================================================
# Application Setup
# ============================================================
>>>>>>> main

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
app.include_router(auth.router, prefix="/auth", tags=["Authentication"])


# ============================================================
<<<<<<< HEAD
# Pydantic Schemas for API Request/Response
# ============================================================

class HealthResponse(BaseModel):
    status: str
    message: str
    version: str


class SkillBase(BaseModel):
    name: str
    category: Optional[str] = None
    difficulty_level: Optional[int] = 1


class CandidateProfile(BaseModel):
    full_name: str
    email: str
    phone: Optional[str] = None
    location: Optional[str] = None
    current_role: Optional[str] = None
    years_of_experience: Optional[float] = 0
    skills: List[str] = []
    confidence_scores: dict = {}

    class Config:
        from_attributes = True


class JobPosting(BaseModel):
    id: int
    title: str
    company: str
    location: Optional[str] = None
    salary_min: Optional[int] = None
    salary_max: Optional[int] = None
    required_skills: List[str] = []

    class Config:
        from_attributes = True


class MatchScore(BaseModel):
    job_id: int
    job_title: str
    company: str
    total_score: float
    skills_score: float
    location_score: float
    salary_score: float
    experience_score: float
    role_score: float
    matching_skills: List[str]
    missing_skills: List[str]
    explanation: str

class SkillScoreResponse(BaseModel):
    overall_score: float
    matched_skills: List[str]
    missing_skills: List[str]
    matching_explanation: str
    job_id: int
    job_title: str


class LearningPhase(BaseModel):
    phase: int
    title: str
    skills: List[str]
    estimated_weeks: int
    resources: List[str] = []


class RoadmapResponse(BaseModel):
    target_role: str
    missing_skills: List[str]
    phases: List[LearningPhase]
    total_estimated_weeks: int


# ============================================================
# Startup Event - Initialize Database
=======
# Lifecycle Events
>>>>>>> main
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
<<<<<<< HEAD
    """Health check endpoint."""
    return HealthResponse(
        status="healthy",
        message="Welcome to Wevolve API - The AI-Powered Career Acceleration Ecosystem",
        version="1.0.0"
    )


@app.get("/health", response_model=HealthResponse)
async def health_check():
    """Detailed health check."""
    return HealthResponse(
        status="healthy",
        message="All systems operational",
        version="1.0.0"
    )


# ============================================================
# Module 1: Resume Intelligence
# ============================================================

@app.post("/api/resume/score", response_model=SkillScoreResponse)
async def calculate_skill_score(
    job_id: int, 
    candidate: CandidateProfile, 
    db: Session = Depends(get_db)
):
    """
    Calculate the match score between a resume and a job requirement.
    The candidate info is provided as JSON in the request body.
    """
    # Fetch job from database
    job_model = db.query(models.Job).filter(models.Job.id == job_id).first()
    if not job_model:
        raise HTTPException(status_code=404, detail="Job not found")

    # Map CandidateProfile to dictionary expected by skill_score.py
    candidate_dict = {
        "skills": candidate.skills,
        "experience_years": candidate.years_of_experience,
        "preferred_locations": [candidate.location] if candidate.location else [],
        "expected_salary": (candidate.confidence_scores.get("expected_salary") or 0),
        "preferred_roles": [candidate.current_role] if candidate.current_role else []
    }

    # Map Job model to dictionary expected by skill_score.py
    job_dict = {
        "id": job_model.id,
        "title": job_model.title,
        "location": job_model.location,
        "salary_min": job_model.salary_min or 0,
        "salary_max": job_model.salary_max or 0,
        "min_experience_years": job_model.min_experience_years or 0,
        "required_skills": [s.name for s in job_model.required_skills]
    }

    # Call the scoring logic from skill_score.py
    result = calculate_match(candidate_dict, job_dict)

    return SkillScoreResponse(
        overall_score=result["match_score"],
        matched_skills=[s for s in job_dict["required_skills"] if s not in result["missing_skills"]],
        missing_skills=result["missing_skills"],
        matching_explanation=f"Match score: {result['match_score']}%. " + 
                            (f"Missing skills: {', '.join(result['missing_skills'])}" if result['missing_skills'] else "All skills matched!"),
        job_id=result["job_id"],
        job_title=result["job_title"]
    )
=======
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
        from sqlalchemy import text
        db = SessionLocal()
        db.execute(text("SELECT 1"))
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
>>>>>>> main


# ============================================================
# Jobs API
# ============================================================

<<<<<<< HEAD
@app.get("/api/jobs", response_model=List[JobPosting])
async def get_all_jobs(db: Session = Depends(get_db)):
    """
    Get all available job postings from the database.
    """
    jobs = db.query(models.Job).all()
    
    # Map SQLAlchemy objects to Pydantic models with skill names
    result = []
    for job in jobs:
        job_data = JobPosting(
            id=job.id,
            title=job.title,
            company=job.company,
            location=job.location,
            salary_min=job.salary_min,
            salary_max=job.salary_max,
            required_skills=[s.name for s in job.required_skills]
        )
        result.append(job_data)
        
    return result


@app.post("/api/match/{candidate_id}", response_model=List[MatchScore])
async def calculate_matches(candidate_id: int):
    """
    Calculate match scores between a candidate and all available jobs.
    Returns detailed breakdown with explanations.
=======
@app.get("/api/jobs")
async def get_jobs():
    """
    Return all available jobs from the jobs.json file.
    """
    jobs_file = Path(__file__).parent.parent / "data" / "jobs.json"
>>>>>>> main
    
    try:
        with open(jobs_file, 'r') as f:
            data = json.load(f)
            return {"jobs": data.get('jobs', [])}
    except FileNotFoundError:
        return {"jobs": []}