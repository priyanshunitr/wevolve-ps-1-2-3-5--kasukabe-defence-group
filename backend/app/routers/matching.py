"""
Transparent Matching Router
Multi-Factor Job Matching Engine with Explainable Scores

Scoring Weight Distribution:
- Skills Match: 40%
- Location Match: 20%
- Salary Match: 15%
- Experience Match: 15%
- Role Match: 10%
"""
import json
from typing import List, Dict, Optional
from pathlib import Path
from thefuzz import process, fuzz
from fastapi import APIRouter, HTTPException, Depends, Query
from pydantic import BaseModel
from sqlalchemy.orm import Session

from ..database import get_db
from ..models import Candidate, Job, MatchResult

router = APIRouter(prefix="/api/match", tags=["Transparent Matching"])


# ============================================================
# Pydantic Schemas
# ============================================================

class SkillMatch(BaseModel):
    """Details about skill matching"""
    skill: str
    matched: bool
    is_required: bool


class MatchBreakdown(BaseModel):
    """Detailed breakdown of a single match"""
    job_id: int
    job_title: str
    company: str
    location: str
    salary_range: str
    
    # Overall Score
    total_score: float  # 0-100
    match_tier: str     # "Excellent", "Good", "Fair", "Poor"
    
    # Factor Scores (raw 0-100)
    skills_score: float
    location_score: float
    salary_score: float
    experience_score: float
    role_score: float
    
    # Skill Details
    matching_skills: List[str]
    missing_required_skills: List[str]
    missing_optional_skills: List[str]
    skill_match_percentage: float
    
    # Human-readable explanation
    explanation: str
    top_reason_for_match: str
    top_area_to_improve: str


class MatchRequest(BaseModel):
    """Request to calculate matches"""
    candidate_skills: List[str]
    candidate_location: Optional[str] = None
    candidate_experience_years: Optional[float] = 0
    expected_salary_min: Optional[int] = None
    expected_salary_max: Optional[int] = None
    target_role: Optional[str] = None


# ============================================================
# Scoring Weights (Configurable)
# ============================================================

WEIGHTS = {
    'skills': 0.40,      # 40%
    'location': 0.20,    # 20%
    'salary': 0.15,      # 15%
    'experience': 0.15,  # 15%
    'role': 0.10         # 10%
}


# ============================================================
# Scoring Functions
# ============================================================

def calculate_skills_score(
    candidate_skills: List[str],
    required_skills: List[str],
    optional_skills: List[str] = []
) -> tuple[float, List[str], List[str], List[str]]:
    """
    Calculate skills match score using fuzzy string matching.
    Required skills are weighted more heavily than optional.
    Threshold for a match is 85%.
    
    Returns: (score, matching_skills, missing_required, missing_optional)
    """
    if not candidate_skills:
        return 0.0, [], required_skills, optional_skills

    MATCH_THRESHOLD = 80
    matching_required = []
    missing_required = []
    matching_optional = []
    missing_optional = []
    
    # Check Required Skills
    for req in required_skills:
        # returns (best_match, score)
        match = process.extractOne(req, candidate_skills, scorer=fuzz.token_set_ratio)
        if match and match[1] >= MATCH_THRESHOLD:
            matching_required.append(req)
        else:
            missing_required.append(req)
            
    # Check Optional Skills
    for opt in optional_skills:
        match = process.extractOne(opt, candidate_skills, scorer=fuzz.token_set_ratio)
        if match and match[1] >= MATCH_THRESHOLD:
            matching_optional.append(opt)
        else:
            missing_optional.append(opt)

    all_matching = list(set(matching_required) | set(matching_optional))
    
    # Score calculation: 80% required, 20% optional
    if not required_skills:
        req_score = 100.0
    else:
        req_score = (len(matching_required) / len(required_skills)) * 100
        
    if not optional_skills:
        opt_score = 100.0
    else:
        opt_score = (len(matching_optional) / len(optional_skills)) * 100
        
    score = (req_score * 0.8) + (opt_score * 0.2)
    
    return score, all_matching, missing_required, missing_optional


def calculate_location_score(
    candidate_location: str,
    job_location: str,
    is_remote: bool
) -> float:
    """
    Calculate location match score.
    Remote jobs get 100% for everyone.
    Same city = 100%, Same state = 70%, Different = 30%
    """
    if is_remote:
        return 100.0
    
    if not candidate_location or not job_location:
        return 50.0  # Unknown = neutral
    
    candidate_loc = candidate_location.lower().strip()
    job_loc = job_location.lower().strip()
    
    # Exact match
    if candidate_loc == job_loc:
        return 100.0
    
    # City aliases (Bangalore = Bengaluru)
    aliases = {
        'bangalore': 'bengaluru',
        'bombay': 'mumbai',
        'madras': 'chennai',
        'calcutta': 'kolkata',
        'gurgaon': 'gurugram'
    }
    
    candidate_normalized = aliases.get(candidate_loc, candidate_loc)
    job_normalized = aliases.get(job_loc, job_loc)
    
    if candidate_normalized == job_normalized:
        return 100.0
    
    # Check if either is "remote" keyword
    if 'remote' in job_loc:
        return 100.0
    
    # Nearby cities (simplified - in production, use geo API)
    nearby_groups = [
        {'delhi', 'noida', 'gurgaon', 'gurugram', 'faridabad', 'ghaziabad'},
        {'mumbai', 'navi mumbai', 'thane', 'pune'},
        {'bangalore', 'bengaluru', 'mysore'},
    ]
    
    for group in nearby_groups:
        if candidate_normalized in group and job_normalized in group:
            return 80.0
    
    return 30.0  # Different regions


def calculate_salary_score(
    expected_min: Optional[int],
    expected_max: Optional[int],
    job_min: Optional[int],
    job_max: Optional[int]
) -> float:
    """
    Calculate salary match score.
    Perfect score if job range overlaps or exceeds expectations.
    Partial score based on how close they are.
    """
    # If either is missing, neutral score
    if not job_min and not job_max:
        return 60.0
    if not expected_min and not expected_max:
        return 70.0  # No expectation = slight positive
    
    # Use midpoints for comparison if ranges exist
    expected_mid = ((expected_min or 0) + (expected_max or expected_min or 0)) / 2
    job_mid = ((job_min or 0) + (job_max or job_min or 0)) / 2
    
    if expected_mid == 0:
        return 70.0
    
    # Job pays more than expected = 100%
    if job_mid >= expected_mid:
        return 100.0
    
    # Calculate how close the job salary is to expectation
    ratio = job_mid / expected_mid
    
    if ratio >= 0.9:  # Within 10%
        return 90.0
    elif ratio >= 0.8:  # Within 20%
        return 75.0
    elif ratio >= 0.7:  # Within 30%
        return 60.0
    else:
        return max(30.0, ratio * 100)


def calculate_experience_score(
    candidate_years: float,
    job_min_years: float,
    job_max_years: Optional[float] = None
) -> float:
    """
    Calculate experience match score.
    In range = 100%, slightly over = 80%, under = proportional
    """
    if job_min_years == 0:
        return 100.0  # Entry level - everyone qualifies
    
    # Within range
    if job_max_years:
        if job_min_years <= candidate_years <= job_max_years:
            return 100.0
        if candidate_years > job_max_years:
            # Overqualified - slight penalty
            over_by = candidate_years - job_max_years
            return max(60.0, 100 - (over_by * 5))
    else:
        if candidate_years >= job_min_years:
            return 100.0
    
    # Under-experienced
    if candidate_years < job_min_years:
        ratio = candidate_years / job_min_years
        return max(20.0, ratio * 100)
    
    return 70.0


def calculate_role_score(
    target_role: Optional[str],
    job_title: str
) -> float:
    """
    Calculate role match score based on title similarity.
    Uses keyword matching and role hierarchy.
    """
    if not target_role:
        return 70.0  # No preference = neutral
    
    target = target_role.lower()
    job = job_title.lower()
    
    # Exact match
    if target in job or job in target:
        return 100.0
    
    # Role family matching
    role_families = {
        'backend': ['python', 'java', 'node', 'api', 'server', 'backend'],
        'frontend': ['react', 'angular', 'vue', 'ui', 'ux', 'frontend', 'web'],
        'fullstack': ['full stack', 'fullstack', 'full-stack'],
        'data': ['data engineer', 'data scientist', 'ml', 'machine learning', 'analytics'],
        'devops': ['devops', 'sre', 'infrastructure', 'platform', 'cloud'],
        'mobile': ['ios', 'android', 'mobile', 'flutter', 'react native'],
    }
    
    # Find candidate's family
    candidate_family = None
    for family, keywords in role_families.items():
        if any(kw in target for kw in keywords):
            candidate_family = family
            break
    
    # Check if job is in the same family
    if candidate_family:
        family_keywords = role_families.get(candidate_family, [])
        if any(kw in job for kw in family_keywords):
            return 85.0
    
    # Check for seniority alignment
    seniority_keywords = ['senior', 'lead', 'principal', 'staff', 'junior', 'associate']
    target_seniority = next((kw for kw in seniority_keywords if kw in target), None)
    job_seniority = next((kw for kw in seniority_keywords if kw in job), None)
    
    if target_seniority and job_seniority:
        if target_seniority == job_seniority:
            return 75.0
    
    return 50.0  # Low match


def calculate_total_score(
    skills: float,
    location: float,
    salary: float,
    experience: float,
    role: float
) -> float:
    """Calculate weighted total score"""
    total = (
        skills * WEIGHTS['skills'] +
        location * WEIGHTS['location'] +
        salary * WEIGHTS['salary'] +
        experience * WEIGHTS['experience'] +
        role * WEIGHTS['role']
    )
    return round(total, 1)


def get_match_tier(score: float) -> str:
    """Convert score to human-readable tier"""
    if score >= 85:
        return "Excellent Match ⭐"
    elif score >= 70:
        return "Good Match ✓"
    elif score >= 50:
        return "Fair Match"
    else:
        return "Poor Match"


def generate_explanation(breakdown: dict) -> tuple[str, str, str]:
    """
    Generate human-readable explanation, top strength, and improvement area.
    """
    scores = {
        'Skills': breakdown['skills_score'],
        'Location': breakdown['location_score'],
        'Salary': breakdown['salary_score'],
        'Experience': breakdown['experience_score'],
        'Role': breakdown['role_score']
    }
    
    # Find best and worst
    best_factor = max(scores, key=scores.get)
    worst_factor = min(scores, key=scores.get)
    
    # Generate explanation
    parts = []
    
    if breakdown['skills_score'] >= 80:
        parts.append(f"Strong skills alignment ({int(breakdown['skill_match_percentage'])}% match)")
    elif breakdown['missing_required_skills']:
        missing = ', '.join(breakdown['missing_required_skills'][:3])
        parts.append(f"Missing key skills: {missing}")
    
    if breakdown['location_score'] == 100:
        parts.append("Location is a perfect fit")
    elif breakdown['location_score'] < 50:
        parts.append("Location may require relocation")
    
    if breakdown['salary_score'] >= 90:
        parts.append("Salary expectations align well")
    
    if breakdown['experience_score'] >= 90:
        parts.append("Experience level matches requirements")
    elif breakdown['experience_score'] < 60:
        parts.append("May need more experience for this role")
    
    explanation = ". ".join(parts) + "." if parts else "Match score calculated based on profile data."
    
    top_reason = f"{best_factor} ({int(scores[best_factor])}%)"
    
    if scores[worst_factor] < 70:
        improve = f"Improve your {worst_factor.lower()} match (currently {int(scores[worst_factor])}%)"
    else:
        improve = "All factors are well-matched!"
    
    return explanation, top_reason, improve


# ============================================================
# API Endpoints
# ============================================================

@router.post("/calculate", response_model=List[MatchBreakdown])
async def calculate_matches(request: MatchRequest):
    """
    Calculate match scores between a candidate and all available jobs.
    Returns detailed breakdown with explanations for each job.
    """
    # Load jobs from JSON (in production, this would be a DB query)
    jobs_file = Path(__file__).parent.parent.parent / "data" / "jobs.json"
    
    try:
        with open(jobs_file, 'r') as f:
            data = json.load(f)
            jobs = data.get('jobs', [])
    except FileNotFoundError:
        # Return mock data if file doesn't exist
        jobs = [
            {
                "id": 1,
                "title": "Senior Python Developer",
                "company": "TechCorp India",
                "location": "Bangalore",
                "is_remote": False,
                "salary_min": 1500000,
                "salary_max": 2500000,
                "min_experience_years": 4,
                "max_experience_years": 8,
                "required_skills": ["Python", "FastAPI", "PostgreSQL", "Docker", "AWS"],
                "nice_to_have_skills": ["Kubernetes", "Redis"]
            }
        ]
    
    results = []
    
    for job in jobs:
        # Calculate each factor score
        skills_score, matching, missing_req, missing_opt = calculate_skills_score(
            request.candidate_skills,
            job.get('required_skills', []),
            job.get('nice_to_have_skills', [])
        )
        
        location_score = calculate_location_score(
            request.candidate_location or "",
            job.get('location', ''),
            job.get('is_remote', False)
        )
        
        salary_score = calculate_salary_score(
            request.expected_salary_min,
            request.expected_salary_max,
            job.get('salary_min'),
            job.get('salary_max')
        )
        
        experience_score = calculate_experience_score(
            request.candidate_experience_years or 0,
            job.get('min_experience_years', 0),
            job.get('max_experience_years')
        )
        
        role_score = calculate_role_score(
            request.target_role,
            job.get('title', '')
        )
        
        # Calculate total
        total = calculate_total_score(
            skills_score, location_score, salary_score,
            experience_score, role_score
        )
        
        # Calculate skill match percentage
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
        
        # Generate explanations
        explanation, top_reason, improve = generate_explanation(breakdown)
        
        # Format salary range
        sal_min = job.get('salary_min', 0)
        sal_max = job.get('salary_max', 0)
        if sal_min and sal_max:
            salary_range = f"₹{sal_min // 100000}L - ₹{sal_max // 100000}L"
        else:
            salary_range = "Not disclosed"
        
        results.append(MatchBreakdown(
            **breakdown,
            salary_range=salary_range,
            total_score=total,
            match_tier=get_match_tier(total),
            explanation=explanation,
            top_reason_for_match=top_reason,
            top_area_to_improve=improve
        ))
    
    # Sort by total score descending
    results.sort(key=lambda x: x.total_score, reverse=True)
    
    return results


@router.get("/weights")
async def get_scoring_weights():
    """Get the current scoring weights used for matching"""
    return {
        "weights": {
            "skills": {"percentage": 40, "description": "Technical skill alignment"},
            "location": {"percentage": 20, "description": "Geographic fit or remote compatibility"},
            "salary": {"percentage": 15, "description": "Compensation expectations alignment"},
            "experience": {"percentage": 15, "description": "Years of experience match"},
            "role": {"percentage": 10, "description": "Job title and role type match"}
        },
        "tiers": {
            "excellent": {"min_score": 85, "emoji": "⭐"},
            "good": {"min_score": 70, "emoji": "✓"},
            "fair": {"min_score": 50, "emoji": ""},
            "poor": {"min_score": 0, "emoji": ""}
        }
    }
