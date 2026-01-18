"""Matching-related schemas"""
from typing import List, Optional, Dict, Any
from pydantic import BaseModel


class CandidateEducation(BaseModel):
    degree: Optional[str] = "B.Tech"
    field: Optional[str] = "Computer Science"
    cgpa: Optional[float] = 8.5


class MatchRequest(BaseModel):
    """Request to calculate job matches with full candidate info"""
    full_name: Optional[str] = "Candidate"
    skills: List[str]
    experience_years: float = 0.0
    preferred_locations: List[str] = []
    preferred_roles: List[str] = []
    expected_salary: int = 0
    education: Optional[CandidateEducation] = None


class ScoreBreakdown(BaseModel):
    """Raw component scores (0-100)"""
    skill_match: float
    location_match: float
    salary_match: float
    experience_match: float
    role_match: float


class JobMatch(BaseModel):
    """Result for a single job match"""
    job_id: int
    job_title: str
    match_score: float
    match_tier: str
    breakdown: ScoreBreakdown
    missing_skills: List[str]
    explanation: str
    top_reason_for_match: str
    top_area_to_improve: str


class MatchResponse(BaseModel):
    """Final response from the matching endpoint"""
    candidate: str
    field: str
    matches: List[JobMatch]
