"""
SQLAlchemy ORM Models for Wevolve
Defines database schema for Candidates, Jobs, Skills, and Matches
"""
from sqlalchemy import Column, Integer, String, Float, Text, JSON, ForeignKey, Table, Boolean
from sqlalchemy.orm import relationship

from .database import Base

# ============================================================
# Association Tables (Many-to-Many relationships)
# ============================================================

candidate_skills = Table(
    'candidate_skills',
    Base.metadata,
    Column('candidate_id', Integer, ForeignKey('candidates.id'), primary_key=True),
    Column('skill_id', Integer, ForeignKey('skills.id'), primary_key=True),
    Column('proficiency_level', Integer, default=1)  # 1-5 scale
)

job_skills = Table(
    'job_skills',
    Base.metadata,
    Column('job_id', Integer, ForeignKey('jobs.id'), primary_key=True),
    Column('skill_id', Integer, ForeignKey('skills.id'), primary_key=True),
    Column('is_required', Boolean, default=True)
)


# ============================================================
# ORM Models
# ============================================================

class Skill(Base):
    """Centralized skill taxonomy for matching and gap analysis"""
    __tablename__ = "skills"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), unique=True, nullable=False, index=True)
    category = Column(String(50))  # e.g., "Programming", "Database"
    difficulty_level = Column(Integer, default=1)  # 1-5 scale
    prerequisites = Column(JSON, default=[])


class Candidate(Base):
    """Candidate profile parsed from resume"""
    __tablename__ = "candidates"
    
    id = Column(Integer, primary_key=True, index=True)
    
    # Basic Info
    full_name = Column(String(200))
    email = Column(String(200), index=True)
    phone = Column(String(50))
    location = Column(String(200))
    
    # Professional Info
    current_role = Column(String(200))
    years_of_experience = Column(Float, default=0)
    expected_salary_min = Column(Integer)
    expected_salary_max = Column(Integer)
    
    # Preferences (JSON lists)
    preferred_locations = Column(JSON, default=[])
    preferred_roles = Column(JSON, default=[])
    
    # Parsed Content (JSON)
    education = Column(JSON, default=[])
    work_experience = Column(JSON, default=[])
    projects = Column(JSON, default=[])
    certifications = Column(JSON, default=[])
    confidence_scores = Column(JSON, default={})
    
    # Raw Data
    raw_resume_text = Column(Text)
    resume_file_path = Column(String(500))
    
    # Relationships
    skills = relationship("Skill", secondary=candidate_skills, backref="candidates")


class Job(Base):
    """Job posting for candidate matching"""
    __tablename__ = "jobs"
    
    id = Column(Integer, primary_key=True, index=True)
    
    # Basic Info
    title = Column(String(200), nullable=False, index=True)
    company = Column(String(200), nullable=False)
    description = Column(Text)
    
    # Location
    location = Column(String(200))
    is_remote = Column(Boolean, default=False)
    
    # Compensation
    salary_min = Column(Integer)
    salary_max = Column(Integer)
    
    # Requirements
    min_experience_years = Column(Float, default=0)
    max_experience_years = Column(Float)
    
    # Relationships
    required_skills = relationship("Skill", secondary=job_skills, backref="jobs")


class MatchResult(Base):
    """Stored match results between candidates and jobs"""
    __tablename__ = "match_results"
    
    id = Column(Integer, primary_key=True, index=True)
    candidate_id = Column(Integer, ForeignKey('candidates.id'), nullable=False)
    job_id = Column(Integer, ForeignKey('jobs.id'), nullable=False)
    
    # Scores
    total_score = Column(Float, nullable=False)
    skills_score = Column(Float)
    location_score = Column(Float)
    salary_score = Column(Float)
    experience_score = Column(Float)
    role_score = Column(Float)
    
    # Details
    matching_skills = Column(JSON, default=[])
    missing_skills = Column(JSON, default=[])
    match_explanation = Column(Text)
    
    # Relationships
    candidate = relationship("Candidate", backref="matches")
    job = relationship("Job", backref="matches")
