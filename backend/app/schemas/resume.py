"""Resume-related schemas"""
from typing import List, Dict, Any, Optional
from pydantic import BaseModel


class ExtractedField(BaseModel):
    """A single extracted field with confidence score"""
    value: Any
    confidence: int  # 0-100



class EducationEntry(BaseModel):
    degree: Optional[str] = None
    field: Optional[str] = None
    institute: Optional[str] = None
    year: Optional[str] = None
    cgpa: Optional[float] = None
    confidence: int = 0

class WorkExperienceEntry(BaseModel):
    title: str
    company: str
    duration: str
    description: List[str] = []

class ProjectEntry(BaseModel):
    title: str
    tech_stack: List[str] = []
    description: List[str] = []
    confidence: int = 0

class ParsedResume(BaseModel):
    """Complete parsed resume with all fields"""
    id: Optional[int] = None
    full_name: ExtractedField
    email: ExtractedField
    phone: ExtractedField
    years_of_experience: ExtractedField
    skills: List[ExtractedField]
    education: List[EducationEntry]
    work_experience: List[WorkExperienceEntry]
    projects: List[ProjectEntry] = []
    
    # New manual/inferred fields
    preferred_locations: List[str] = []
    preferred_roles: List[str] = []
    expected_salary: Optional[int] = None
    
    overall_confidence: int
    raw_text: str


class ProfileUpdate(BaseModel):
    """User correction for a parsed field"""
    field_name: str
    corrected_value: Any


class CandidateProfile(BaseModel):
    """Simplified candidate profile response"""
    full_name: str
    email: str
    phone: Optional[str] = None
    years_of_experience: Optional[float] = 0
    skills: List[str] = []
    confidence_scores: dict = {}

    class Config:
        from_attributes = True
