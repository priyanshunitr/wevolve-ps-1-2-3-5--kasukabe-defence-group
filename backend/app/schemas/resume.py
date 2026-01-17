"""Resume-related schemas"""
from typing import List, Dict, Any, Optional
from pydantic import BaseModel


class ExtractedField(BaseModel):
    """A single extracted field with confidence score"""
    value: Any
    confidence: int  # 0-100
    source: str
    needs_review: bool


class ParsedResume(BaseModel):
    """Complete parsed resume with all fields"""
    id: Optional[int] = None
    full_name: ExtractedField
    email: ExtractedField
    phone: ExtractedField
    location: ExtractedField
    current_role: ExtractedField
    years_of_experience: ExtractedField
    skills: List[ExtractedField]
    education: List[Dict]
    work_experience: List[Dict]
    
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
    location: Optional[str] = None
    current_role: Optional[str] = None
    years_of_experience: Optional[float] = 0
    skills: List[str] = []
    confidence_scores: dict = {}

    class Config:
        from_attributes = True
