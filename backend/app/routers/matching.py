"""
Transparent Matching Router
Simplified API endpoints - business logic delegated to services
"""
import json
from typing import List
from pathlib import Path
from fastapi import APIRouter

from ..config import settings
from ..schemas.matching import MatchRequest, MatchBreakdown
from ..services import MatchingEngine

router = APIRouter(prefix="/api/match", tags=["Transparent Matching"])

# Service instance
engine = MatchingEngine()


@router.post("/calculate", response_model=List[MatchBreakdown])
async def calculate_matches(request: MatchRequest):
    """
    Calculate match scores between a candidate and all available jobs.
    Returns detailed breakdown with explanations for each job.
    """
    # Load jobs data
    jobs_file = Path(__file__).parent.parent.parent / "data" / "jobs.json"
    
    try:
        with open(jobs_file, 'r') as f:
            data = json.load(f)
            jobs = data.get('jobs', [])
    except FileNotFoundError:
        jobs = [_get_fallback_job()]
    
    results = []
    
    for job in jobs:
        # Calculate scores using service
        skills_score, matching, missing_req, missing_opt = engine.calculate_skills_score(
            request.candidate_skills,
            job.get('required_skills', []),
            job.get('nice_to_have_skills', [])
        )
        
        location_score = engine.calculate_location_score(
            request.candidate_location or "",
            job.get('location', ''),
            job.get('is_remote', False)
        )
        
        salary_score = engine.calculate_salary_score(
            request.expected_salary_min,
            request.expected_salary_max,
            job.get('salary_min'),
            job.get('salary_max')
        )
        
        experience_score = engine.calculate_experience_score(
            request.candidate_experience_years or 0,
            job.get('min_experience_years', 0),
            job.get('max_experience_years')
        )
        
        role_score = engine.calculate_role_score(request.target_role, job.get('title', ''))
        
        total = engine.calculate_total_score(
            skills_score, location_score, salary_score, experience_score, role_score
        )
        
        # Build breakdown
        all_required = job.get('required_skills', [])
        skill_pct = (len(matching) / len(all_required) * 100) if all_required else 100
        
        breakdown = {
            'job_id': job.get('id'),
            'job_title': job.get('title'),
            'company': job.get('company'),
            'location': job.get('location', 'Not specified'),
            'skills_score': round(skills_score, 1),
            'location_score': round(location_score, 1),
            'salary_score': round(salary_score, 1),
            'experience_score': round(experience_score, 1),
            'role_score': round(role_score, 1),
            'matching_skills': matching,
            'missing_required_skills': missing_req,
            'missing_optional_skills': missing_opt,
            'skill_match_percentage': round(skill_pct, 1)
        }
        
        explanation, top_reason, improve = engine.generate_explanation(breakdown)
        
        # Format salary range
        sal_min, sal_max = job.get('salary_min', 0), job.get('salary_max', 0)
        salary_range = f"₹{sal_min // 100000}L - ₹{sal_max // 100000}L" if sal_min and sal_max else "Not disclosed"
        
        results.append(MatchBreakdown(
            **breakdown,
            salary_range=salary_range,
            total_score=total,
            match_tier=engine.get_match_tier(total),
            explanation=explanation,
            top_reason_for_match=top_reason,
            top_area_to_improve=improve
        ))
    
    results.sort(key=lambda x: x.total_score, reverse=True)
    return results


@router.get("/weights")
async def get_scoring_weights():
    """Get the current scoring weights used for matching"""
    return {
        "weights": {
            "skills": {"percentage": 40, "description": "Technical skill alignment"},
            "location": {"percentage": 20, "description": "Geographic fit"},
            "salary": {"percentage": 15, "description": "Compensation alignment"},
            "experience": {"percentage": 15, "description": "Experience match"},
            "role": {"percentage": 10, "description": "Role type match"}
        },
        "tiers": settings.MATCH_TIERS
    }


def _get_fallback_job() -> dict:
    """Return fallback job if data file not found"""
    return {
        "id": 1,
        "title": "Senior Python Developer",
        "company": "TechCorp India",
        "location": "Bangalore",
        "is_remote": False,
        "salary_min": 1500000,
        "salary_max": 2500000,
        "min_experience_years": 4,
        "required_skills": ["Python", "FastAPI", "PostgreSQL", "Docker", "AWS"]
    }
