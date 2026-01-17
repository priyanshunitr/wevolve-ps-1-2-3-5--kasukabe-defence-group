"""Matching-related schemas"""
from typing import List, Optional
from pydantic import BaseModel


class SkillMatch(BaseModel):
    """Details about a skill match"""
    skill: str
    matched: bool
    is_required: bool


class MatchRequest(BaseModel):
    """Request to calculate job matches"""
    candidate_skills: List[str]
    candidate_location: Optional[str] = None
    candidate_experience_years: Optional[float] = 0
    expected_salary_min: Optional[int] = None
    expected_salary_max: Optional[int] = None
    target_role: Optional[str] = None


class MatchBreakdown(BaseModel):
    """Detailed match breakdown for a job"""
    job_id: int
    job_title: str
    company: str
    location: str
    salary_range: str
    
    # Scores
    total_score: float
    match_tier: str
    skills_score: float
    location_score: float
    salary_score: float
    experience_score: float
    role_score: float
    
    # Skill details
    matching_skills: List[str]
    missing_required_skills: List[str]
    missing_optional_skills: List[str]
    skill_match_percentage: float
    
    # Explanations
    explanation: str
    top_reason_for_match: str
    top_area_to_improve: str
