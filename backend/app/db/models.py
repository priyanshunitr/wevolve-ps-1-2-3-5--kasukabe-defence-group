"""
SQLAlchemy ORM Models for Wevolve
Defines database schema for Candidates, Jobs, and Skills
"""
from sqlalchemy import Column, Integer, String, Float, Text, JSON, ForeignKey, Table, Boolean, SmallInteger
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


class JobPosting(Base):
    """Job posting storage that mirrors jobs.json structure"""
    __tablename__ = "job_postings"
    
    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(200), nullable=False, index=True)
    company = Column(String(200), nullable=False)
    description = Column(Text)
    location = Column(String(200))
    is_remote = Column(Boolean, default=False)
    salary_min = Column(Integer)
    salary_max = Column(Integer)
    min_experience_years = Column(Float, default=0)
    max_experience_years = Column(Float)
    required_skills = Column(JSON, default=[])
    nice_to_have_skills = Column(JSON, default=[])


# =========
#Auth
#==========

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String)
    email = Column(String, unique=True, index=True)
    hashed_password = Column(String)
    
    # Profile information
    city = Column(String, nullable=True)
    lat = Column(Float, nullable=True)
    lon = Column(Float, nullable=True)
    
    # Photo paths (strings)
    profile_photo = Column(String, nullable=True)
    cover_photo = Column(String, nullable=True)
    
    # Required for your register endpoint
    device_id = Column(String, default="A1:B2:C3:D4:E5:F6")
    
    # Required for your login/delete logic
    # Using SmallInteger (0 or 1) for SQLite compatibility
    is_deleted = Column(SmallInteger, default=0)


# Note: Job model removed to simplify according to user request.
# Note: MatchResult model removed according to user request.
