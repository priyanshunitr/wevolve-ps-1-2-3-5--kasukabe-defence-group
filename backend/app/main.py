"""
Wevolve API - Main Entry Point
The AI-Powered Career Acceleration Ecosystem

Three Core Modules:
1. Resume Intelligence - Parse and score resumes
2. Transparent Matching - Multi-factor job matching with explanations
3. Actionable Growth - Personalized learning roadmaps
"""
from typing import Optional, List
import json

from fastapi import FastAPI, HTTPException, UploadFile, File, Depends
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from sqlalchemy.orm import Session
from . import models

from .database import init_db, get_db

# Import routers
from .routers import resume, matching, roadmap

# Initialize FastAPI app
app = FastAPI(
    title="Wevolve API",
    description="AI-Powered Career Acceleration Ecosystem",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# CORS Configuration for React frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://localhost:3000"],  # Vite & CRA defaults
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include Routers
app.include_router(resume.router)
app.include_router(matching.router)
app.include_router(roadmap.router)


# ============================================================
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
# ============================================================

@app.on_event("startup")
async def startup_event():
    """Initialize the database on application startup."""
    print("🚀 Wevolve API Starting...")
    init_db()
    print("✅ Database initialized successfully!")


# ============================================================
# API Endpoints
# ============================================================

@app.get("/", response_model=HealthResponse)
async def root():
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

@app.post("/api/resume/parse", response_model=CandidateProfile)
async def parse_resume(file: UploadFile = File(...)):
    """
    Parse an uploaded resume (PDF/DOCX) and extract structured data.
    Returns confidence scores for each extracted field.
    
    This is a placeholder - actual parsing logic will be implemented in routers/resume.py
    """
    # Validate file type
    allowed_types = ["application/pdf", "application/vnd.openxmlformats-officedocument.wordprocessingml.document"]
    if file.content_type not in allowed_types:
        raise HTTPException(
            status_code=400,
            detail="Invalid file type. Please upload a PDF or DOCX file."
        )
    
    # Placeholder response - actual implementation will use pdfplumber/python-docx
    return CandidateProfile(
        full_name="Demo Candidate",
        email="demo@example.com",
        phone="+91 9876543210",
        location="Bangalore, India",
        current_role="Software Developer",
        years_of_experience=3.5,
        skills=["Python", "FastAPI", "React", "SQL"],
        confidence_scores={
            "full_name": 95,
            "email": 100,
            "phone": 85,
            "location": 80,
            "skills": 90
        }
    )


# ============================================================
# Module 2: Transparent Matching
# ============================================================

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
    
    Scoring Weights:
    - Skills: 40%
    - Location: 20%
    - Salary: 15%
    - Experience: 15%
    - Role: 10%
    """
    # Placeholder response - actual matching engine will be implemented
    return [
        MatchScore(
            job_id=1,
            job_title="Senior Python Developer",
            company="TechCorp India",
            total_score=78.5,
            skills_score=85.0,
            location_score=100.0,
            salary_score=70.0,
            experience_score=60.0,
            role_score=75.0,
            matching_skills=["Python", "FastAPI"],
            missing_skills=["PostgreSQL", "Docker", "AWS"],
            explanation="Strong skills match (85%). You have 2/5 required skills. Consider learning PostgreSQL and Docker to improve your match."
        )
    ]


# ============================================================
# Module 3: Actionable Growth (Roadmap Generation)
# ============================================================

@app.get("/api/roadmap/{candidate_id}/{job_id}", response_model=RoadmapResponse)
async def generate_roadmap(candidate_id: int, job_id: int):
    """
    Generate a personalized learning roadmap based on skill gaps.
    Uses skill dependency topology to order learning phases.
    """
    # Placeholder response - actual roadmap generation will be implemented
    return RoadmapResponse(
        target_role="Senior Python Developer",
        missing_skills=["PostgreSQL", "Docker", "AWS"],
        phases=[
            LearningPhase(
                phase=1,
                title="Database Fundamentals",
                skills=["PostgreSQL"],
                estimated_weeks=3,
                resources=["PostgreSQL Official Tutorial", "SQLZoo Exercises"]
            ),
            LearningPhase(
                phase=2,
                title="Containerization",
                skills=["Docker"],
                estimated_weeks=2,
                resources=["Docker Getting Started", "Docker for Developers course"]
            ),
            LearningPhase(
                phase=3,
                title="Cloud Infrastructure",
                skills=["AWS"],
                estimated_weeks=4,
                resources=["AWS Free Tier Labs", "AWS Certified Developer Guide"]
            )
        ],
        total_estimated_weeks=9
    )


# ============================================================
# Run with: uvicorn app.main:app --reload
# ============================================================
