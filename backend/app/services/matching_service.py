"""
Matching Engine Service
Handles job-candidate matching with fuzzy string comparison and explainable scores
"""
from typing import List, Tuple, Optional
from thefuzz import process, fuzz

from ..config import settings


class MatchingEngine:
    """Service for calculating job-candidate match scores using fuzzy matching"""
    
    # City aliases for location matching
    CITY_ALIASES = {
        'bangalore': 'bengaluru', 'bombay': 'mumbai',
        'madras': 'chennai', 'calcutta': 'kolkata', 'gurgaon': 'gurugram'
    }
    
    # Nearby city groups
    NEARBY_GROUPS = [
        {'delhi', 'noida', 'gurgaon', 'gurugram', 'faridabad', 'ghaziabad'},
        {'mumbai', 'navi mumbai', 'thane', 'pune'},
        {'bangalore', 'bengaluru', 'mysore'},
    ]
    
    def __init__(self):
        # We use a threshold of 85 for fuzzy matches as established in job_matching.py
        self.MATCH_THRESHOLD = 85
        self.weights = {
            "skill": 0.4,
            "location": 0.2,
            "salary": 0.15,
            "experience": 0.15,
            "role": 0.1
        }
    
    def calculate_skills_score(
        self, candidate_skills: List[str], required_skills: List[str],
        optional_skills: List[str] = []
    ) -> Tuple[float, List[str], List[str], List[str]]:
        """
        Calculate skills match score using fuzzy matching.
        Returns (score, matching_all, missing_req, missing_opt)
        """
        if not required_skills and not optional_skills:
            return 100.0, [], [], []

        matched_req = []
        missing_req = []
        for req in required_skills:
            match = process.extractOne(req, candidate_skills, scorer=fuzz.token_set_ratio)
            if match and match[1] >= self.MATCH_THRESHOLD:
                matched_req.append(req)
            else:
                missing_req.append(req)
        
        matched_opt = []
        missing_opt = []
        for opt in optional_skills:
            match = process.extractOne(opt, candidate_skills, scorer=fuzz.token_set_ratio)
            if match and match[1] >= self.MATCH_THRESHOLD:
                matched_opt.append(opt)
            else:
                missing_opt.append(opt)
        
        # Calculate scores
        # If no required skills, req_score is 100
        req_score = (len(matched_req) / len(required_skills) * 100) if required_skills else 100.0
        # If no optional skills, opt_score is 100
        opt_score = (len(matched_opt) / len(optional_skills) * 100) if optional_skills else 100.0
        
        # Weighted skill score: 80% required, 20% optional (internal service weight)
        skill_score = (req_score * 0.8) + (opt_score * 0.2)
        
        return skill_score, matched_req + matched_opt, missing_req, missing_opt

    def calculate_location_score(
        self, candidate_locations: List[str], job_location: str
    ) -> float:
        """Calculate location match score. candidate_locations is a list (from schema)"""
        if not candidate_locations or not job_location:
            return 0.0
            
        if any(job_location in loc for loc in candidate_locations):
            return 100.0
            
        # Check aliases and groups
        normalized_job = self.CITY_ALIASES.get(job_location.lower(), job_location.lower())
        
        for loc in candidate_locations:
            normalized_loc = self.CITY_ALIASES.get(loc.lower(), loc.lower())
            if normalized_loc == normalized_job:
                return 100.0
                
            for group in self.NEARBY_GROUPS:
                if normalized_loc in group and normalized_job in group:
                    return 80.0
        
        return 0.0

    def calculate_salary_score(
        self, expected_salary: int, job_min: int, job_max: int
    ) -> float:
        """Calculate salary match score"""
        if job_min <= expected_salary <= job_max:
            return 100.0
        
        if expected_salary < job_min:
            return max(0, 100 - (abs(expected_salary - job_min) / job_min * 100))
        else:
            return max(0, 100 - (abs(expected_salary - job_max) / job_max * 100))

    def calculate_experience_score(
        self, candidate_years: float, min_exp: float
    ) -> float:
        """Calculate experience match score"""
        if candidate_years >= min_exp:
            return 100.0
        return (candidate_years / min_exp * 100) if min_exp > 0 else 100.0

    def calculate_role_score(self, preferred_roles: List[str], job_title: str) -> float:
        """Calculate role match score using fuzzy matching"""
        if not preferred_roles or not job_title:
            return 70.0 # Neutral score
            
        role_match_result = process.extractOne(job_title, preferred_roles, scorer=fuzz.token_set_ratio)
        return role_match_result[1] if role_match_result else 0.0

    def calculate_total_score(self, breakdown: dict) -> float:
        """Calculate weighted total score based on the established 0.4, 0.2, 0.15, 0.15, 0.1 weights"""
        total = (
            breakdown['skill_match'] * self.weights['skill'] +
            breakdown['location_match'] * self.weights['location'] +
            breakdown['salary_match'] * self.weights['salary'] +
            breakdown['experience_match'] * self.weights['experience'] +
            breakdown['role_match'] * self.weights['role']
        )
        return round(total, 1)

    @staticmethod
    def get_match_tier(score: float) -> str:
        """Convert score to tier label"""
        if score >= settings.MATCH_TIERS.get('excellent', 85):
            return "Excellent Match ⭐"
        elif score >= settings.MATCH_TIERS.get('good', 70):
            return "Good Match ✓"
        elif score >= settings.MATCH_TIERS.get('fair', 50):
            return "Fair Match"
        return "Poor Match"

    def generate_explanation(self, result: dict) -> Tuple[str, str, str]:
        """Generate human-readable explanation, top strength, and improvement area"""
        # This mirrors the logic in the router but works on the returned dict
        breakdown = result['breakdown']
        scores = {
            'Skills': breakdown['skill_match'],
            'Location': breakdown['location_match'],
            'Salary': breakdown['salary_match'],
            'Experience': breakdown['experience_match'],
            'Role': breakdown['role_match']
        }
        
        best = max(scores, key=scores.get)
        worst = min(scores, key=scores.get)
        
        parts = []
        if breakdown['skill_match'] >= 80:
            parts.append("Strong skills alignment")
        elif result.get('missing_skills'):
            missing = ', '.join(result['missing_skills'][:3])
            parts.append(f"Missing key skills: {missing}")
        
        if breakdown['location_match'] == 100:
            parts.append("Location is a perfect fit")
        
        if breakdown['salary_match'] >= 90:
            parts.append("Salary expectations align well")
        
        explanation = ". ".join(parts) + "." if parts else "Match score calculated based on profile data."
        top_reason = f"{best} ({int(scores[best])}%)"
        
        if scores[worst] < 70:
            improve = f"Improve your {worst.lower()} match (currently {int(scores[worst])}%)"
        else:
            improve = "All factors are well-matched!"
            
        return explanation, top_reason, improve
