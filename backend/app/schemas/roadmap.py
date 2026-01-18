"""Roadmap-related schemas"""
from typing import List, Optional
from pydantic import BaseModel


class LearningResource(BaseModel):
    """A single learning resource"""
    title: str
    type: str  # "course", "tutorial", "documentation", "project"
    url: Optional[str] = None
    provider: str
    estimated_hours: int
    is_free: bool


class SkillNode(BaseModel):
    """A skill in the learning roadmap"""
    name: str
    category: str
    difficulty: int  # 1-5
    estimated_weeks: float
    prerequisites: List[str]
    resources: List[LearningResource]
    why_needed: str


class LearningPhase(BaseModel):
    """A phase in the learning roadmap"""
    phase_number: int
    title: str
    description: str
    skills: List[SkillNode]
    total_weeks: float
    milestone: str


class RoadmapRequest(BaseModel):
    """Request for generating a roadmap"""
    current_skills: List[str]
    target_job_id: int
    learning_pace: str = "moderate"  # "intensive", "moderate", "relaxed"
# check how learning pace will be decided

class RoadmapResponse(BaseModel):
    """Complete learning roadmap"""
    target_job: str
    target_company: str
    current_match_score: float
    projected_match_score: float
    missing_skills_count: int
    phases: List[LearningPhase]
    total_estimated_weeks: float
    total_estimated_hours: int
    summary: str
    motivation_message: str
