import os
import json
import pytest
import sys
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

# Ensure the app directory is in the path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.main import app
from app.db.database import Base, get_db
from app.db.models import JobPosting

# SQLite test database (in-memory)
SQLALCHEMY_DATABASE_URL = "sqlite://"

engine = create_engine(
    SQLALCHEMY_DATABASE_URL,
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

@pytest.fixture(scope="session", autouse=True)
def setup_database():
    """Create tables and seed with jobs.json data"""
    Base.metadata.create_all(bind=engine)
    
    db = TestingSessionLocal()
    
    # Load jobs from backend/data/jobs.json
    jobs_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), "data", "jobs.json")
    with open(jobs_path, "r") as f:
        data = json.load(f)
        jobs = data.get("jobs", [])
    
    for job_data in jobs:
        job = JobPosting(
            id=job_data["id"],
            title=job_data["title"],
            company=job_data["company"],
            description=job_data["description"],
            location=job_data["location"],
            is_remote=job_data["is_remote"],
            salary_min=job_data["salary_min"],
            salary_max=job_data["salary_max"],
            min_experience_years=job_data["min_experience_years"],
            max_experience_years=job_data["max_experience_years"],
            required_skills=job_data["required_skills"],
            nice_to_have_skills=job_data["nice_to_have_skills"]
        )
        db.add(job)
    
    db.commit()
    db.close()
    yield
    Base.metadata.drop_all(bind=engine)

def override_get_db():
    try:
        db = TestingSessionLocal()
        yield db
    finally:
        db.close()

app.dependency_overrides[get_db] = override_get_db

@pytest.fixture()
def client():
    return TestClient(app)
