import pytest

def test_calculate_matches_success(client):
    """Test successful matching calculation with sample candidate"""
    candidate_data = {
        "full_name": "Test Candidate",
        "skills": ["Python", "FastAPI", "React", "Docker"],
        "experience_years": 3.0,
        "preferred_locations": ["Bangalore", "Remote"],
        "preferred_roles": ["Backend Developer", "Full Stack Developer"],
        "expected_salary": 1800000,
        "education": {
            "degree": "B.Tech",
            "field": "Computer Science",
            "cgpa": 8.0
        }
    }
    
    response = client.post("/api/matching/calculate", json=candidate_data)
    
    assert response.status_code == 200
    data = response.json()
    
    assert "candidate" in data
    assert data["candidate"] == "Test Candidate"
    assert "field" in data
    assert data["field"] == "Computer Science"
    assert "matches" in data
    assert len(data["matches"]) > 0
    
    # Check first match structure
    first_match = data["matches"][0]
    assert "job_title" in first_match
    assert "match_score" in first_match
    assert "match_tier" in first_match
    assert "breakdown" in first_match
    assert "explanation" in first_match
    
    # Check component scores
    breakdown = first_match["breakdown"]
    assert "skill_match" in breakdown
    assert "location_match" in breakdown
    assert "salary_match" in breakdown
    assert "experience_match" in breakdown
    assert "role_match" in breakdown

def test_calculate_matches_high_score(client):
    """Test that a perfectly matched candidate gets a high score"""
    # Specifically targeting "Senior Python Developer" (id: 1)
    # Required skills: Python, FastAPI, PostgreSQL, Docker, AWS
    # Salary: 15-25L, Experience: 4+ years, Location: Bangalore
    candidate_data = {
        "full_name": "Senior Python Expert",
        "skills": ["Python", "FastAPI", "PostgreSQL", "Docker", "AWS", "Kubernetes"],
        "experience_years": 6.0,
        "preferred_locations": ["Bangalore"],
        "preferred_roles": ["Senior Python Developer"],
        "expected_salary": 2000000,
        "education": {
            "field": "Software Engineering"
        }
    }
    
    response = client.post("/api/matching/calculate", json=candidate_data)
    assert response.status_code == 200
    data = response.json()
    
    # Find the Senior Python Developer match
    job1_match = next((m for m in data["matches"] if m["job_id"] == 1), None)
    assert job1_match is not None
    assert job1_match["match_score"] > 85
    assert "Excellent Match" in job1_match["match_tier"]

def test_missing_skills_explanation(client):
    """Test that missing skills are correctly identified in the response"""
    candidate_data = {
        "skills": ["Python"], # Missing most required skills for Job 1
        "education": {"field": "IT"}
    }
    
    response = client.post("/api/matching/calculate", json=candidate_data)
    data = response.json()
    
    job1_match = next((m for m in data["matches"] if m["job_id"] == 1), None)
    assert job1_match is not None
    assert "FastAPI" in job1_match["missing_skills"]
    assert "AWS" in job1_match["missing_skills"]
