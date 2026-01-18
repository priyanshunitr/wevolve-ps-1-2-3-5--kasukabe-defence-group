
import pytest
from fastapi.testclient import TestClient
import sys
import os

# Add backend directory to sys.path to allow importing app
backend_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
if backend_path not in sys.path:
    sys.path.insert(0, backend_path)

from app.main import app

client = TestClient(app)

def test_get_available_skills():
    """Test retrieving the list of available skills."""
    response = client.get("/api/roadmap/skills")
    assert response.status_code == 200
    data = response.json()
    
    # Check for basic skills we know exist in the system (lowercase keys)
    assert "python" in data
    assert "fastapi" in data
    
    # Check structure
    python_data = data["python"]
    assert "category" in python_data
    assert "difficulty" in python_data
    assert "prerequisites" in python_data

def test_generate_roadmap_with_significant_gaps():
    """Test generating a roadmap where the user has few matching skills."""
    # Job 1 (Senior Python Developer) requires Python, FastAPI, PostgreSQL, Docker, AWS
    # User only has "Python".
    payload = {
        "target_job_id": 1,
        "current_skills": ["Python"],
        "learning_pace": "moderate"
    }
    response = client.post("/api/roadmap/generate", json=payload)
    assert response.status_code == 200
    data = response.json()
    
    assert data["target_job"] == "Senior Python Developer"
    assert data["missing_skills_count"] > 0
    
    # Since we are missing FastAPI, PostgreSQL, Docker, and AWS, count should be at least 4
    # (plus nice-to-haves if included, which they are in missing_skills calculation)
    assert data["missing_skills_count"] >= 4
    
    # Check that phases were generated
    assert len(data["phases"]) > 0
    
    # Check first phase structure (LearningPhase schema has 'title', not 'phase_name')
    first_phase = data["phases"][0]
    assert "title" in first_phase
    assert "skills" in first_phase
    assert len(first_phase["skills"]) > 0

def test_generate_roadmap_perfect_match():
    """Test generating a roadmap where the user has ALL required and optional skills."""
    # Job 1 Skills
    all_job_skills = [
        "Python", "FastAPI", "PostgreSQL", "Docker", "AWS",  # Required
        "Kubernetes", "Redis", "GraphQL"                     # Nice to have
    ]
    
    payload = {
        "target_job_id": 1,
        "current_skills": all_job_skills,
        "learning_pace": "intense"
    }
    response = client.post("/api/roadmap/generate", json=payload)
    assert response.status_code == 200
    data = response.json()
    
    assert data["missing_skills_count"] == 0
    assert data["current_match_score"] == 100.0
    assert len(data["phases"]) == 0
    # Check for appropriate success message (API says "already have all" or "ready to apply")
    assert "already have all" in data["summary"].lower() or "ready to apply" in data["motivation_message"].lower()

def test_generate_roadmap_partial_match():
    """Test generating a roadmap with some gaps."""
    # User has Python, FastAPI, SQL. Missing Docker, AWS, PostgreSQL specific, etc.
    payload = {
        "target_job_id": 1,
        "current_skills": ["Python", "FastAPI", "SQL"],
        "learning_pace": "casual"
    }
    response = client.post("/api/roadmap/generate", json=payload)
    assert response.status_code == 200
    data = response.json()
    
    assert data["missing_skills_count"] > 0
    assert data["missing_skills_count"] < 8 # Total skills for job is 8. Should have fewer missing than total.
    
    # Check estimated weeks exists and is positive
    assert data["total_estimated_weeks"] > 0

def test_generate_roadmap_invalid_job_id():
    """Test error handling for non-existent job ID."""
    payload = {
        "target_job_id": 999999,
        "current_skills": ["Python"],
        "learning_pace": "moderate"
    }
    response = client.post("/api/roadmap/generate", json=payload)
    assert response.status_code == 404
    assert "not found" in response.json()["detail"].lower()
