"""
Matching Engine Service
Handles job-candidate matching with explainable scores
"""
from typing import List, Tuple, Optional

from ..config import settings


class MatchingEngine:
    """Service for calculating job-candidate match scores"""
    
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
    
    # Role families for matching
    ROLE_FAMILIES = {
        'backend': ['python', 'java', 'node', 'api', 'server', 'backend'],
        'frontend': ['react', 'angular', 'vue', 'ui', 'ux', 'frontend', 'web'],
        'fullstack': ['full stack', 'fullstack', 'full-stack'],
        'data': ['data engineer', 'data scientist', 'ml', 'machine learning', 'analytics'],
        'devops': ['devops', 'sre', 'infrastructure', 'platform', 'cloud'],
        'mobile': ['ios', 'android', 'mobile', 'flutter', 'react native'],
    }
    
    def __init__(self):
        self.weights = settings.MATCHING_WEIGHTS
    
    def calculate_skills_score(
        self, candidate_skills: List[str], required_skills: List[str],
        optional_skills: List[str] = []
    ) -> Tuple[float, List[str], List[str], List[str]]:
        """Calculate skills match score. Returns (score, matching, missing_req, missing_opt)"""
        candidate_lower = {s.lower() for s in candidate_skills}
        required_lower = {s.lower() for s in required_skills}
        optional_lower = {s.lower() for s in optional_skills}
        
        matching_required = candidate_lower & required_lower
        matching_optional = candidate_lower & optional_lower
        missing_required = list(required_lower - candidate_lower)
        missing_optional = list(optional_lower - candidate_lower)
        matching = list(matching_required | matching_optional)
        
        if not required_skills:
            return 100.0, [s.title() for s in matching], missing_required, missing_optional
        
        req_score = (len(matching_required) / len(required_skills)) * 100
        opt_score = (len(matching_optional) / len(optional_skills)) * 100 if optional_skills else 0
        
        score = (req_score * 0.8) + (opt_score * 0.2)
        return score, [s.title() for s in matching], missing_required, missing_optional
    
    def calculate_location_score(
        self, candidate_location: str, job_location: str, is_remote: bool
    ) -> float:
        """Calculate location match score"""
        if is_remote or 'remote' in job_location.lower():
            return 100.0
        
        if not candidate_location or not job_location:
            return 50.0
        
        cand = self.CITY_ALIASES.get(candidate_location.lower(), candidate_location.lower())
        job = self.CITY_ALIASES.get(job_location.lower(), job_location.lower())
        
        if cand == job:
            return 100.0
        
        for group in self.NEARBY_GROUPS:
            if cand in group and job in group:
                return 80.0
        
        return 30.0
    
    def calculate_salary_score(
        self, expected_min: Optional[int], expected_max: Optional[int],
        job_min: Optional[int], job_max: Optional[int]
    ) -> float:
        """Calculate salary match score"""
        if not job_min and not job_max:
            return 60.0
        if not expected_min and not expected_max:
            return 70.0
        
        expected_mid = ((expected_min or 0) + (expected_max or expected_min or 0)) / 2
        job_mid = ((job_min or 0) + (job_max or job_min or 0)) / 2
        
        if expected_mid == 0:
            return 70.0
        if job_mid >= expected_mid:
            return 100.0
        
        ratio = job_mid / expected_mid
        if ratio >= 0.9:
            return 90.0
        elif ratio >= 0.8:
            return 75.0
        elif ratio >= 0.7:
            return 60.0
        return max(30.0, ratio * 100)
    
    def calculate_experience_score(
        self, candidate_years: float, job_min_years: float,
        job_max_years: Optional[float] = None
    ) -> float:
        """Calculate experience match score"""
        if job_min_years == 0:
            return 100.0
        
        if job_max_years:
            if job_min_years <= candidate_years <= job_max_years:
                return 100.0
            if candidate_years > job_max_years:
                return max(60.0, 100 - (candidate_years - job_max_years) * 5)
        elif candidate_years >= job_min_years:
            return 100.0
        
        if candidate_years < job_min_years:
            return max(20.0, (candidate_years / job_min_years) * 100)
        
        return 70.0
    
    def calculate_role_score(self, target_role: Optional[str], job_title: str) -> float:
        """Calculate role match score"""
        if not target_role:
            return 70.0
        
        target = target_role.lower()
        job = job_title.lower()
        
        if target in job or job in target:
            return 100.0
        
        for family, keywords in self.ROLE_FAMILIES.items():
            if any(kw in target for kw in keywords):
                if any(kw in job for kw in keywords):
                    return 85.0
        
        seniority = ['senior', 'lead', 'principal', 'staff', 'junior', 'associate']
        target_sen = next((kw for kw in seniority if kw in target), None)
        job_sen = next((kw for kw in seniority if kw in job), None)
        
        if target_sen and job_sen and target_sen == job_sen:
            return 75.0
        
        return 50.0
    
    def calculate_total_score(
        self, skills: float, location: float, salary: float,
        experience: float, role: float
    ) -> float:
        """Calculate weighted total score"""
        return round(
            skills * self.weights['skills'] +
            location * self.weights['location'] +
            salary * self.weights['salary'] +
            experience * self.weights['experience'] +
            role * self.weights['role'],
            1
        )
    
    @staticmethod
    def get_match_tier(score: float) -> str:
        """Convert score to tier label"""
        if score >= settings.MATCH_TIERS['excellent']:
            return "Excellent Match ⭐"
        elif score >= settings.MATCH_TIERS['good']:
            return "Good Match ✓"
        elif score >= settings.MATCH_TIERS['fair']:
            return "Fair Match"
        return "Poor Match"
    
    def generate_explanation(self, breakdown: dict) -> Tuple[str, str, str]:
        """Generate human-readable explanation, top strength, and improvement area"""
        scores = {
            'Skills': breakdown['skills_score'],
            'Location': breakdown['location_score'],
            'Salary': breakdown['salary_score'],
            'Experience': breakdown['experience_score'],
            'Role': breakdown['role_score']
        }
        
        best = max(scores, key=scores.get)
        worst = min(scores, key=scores.get)
        
        parts = []
        if breakdown['skills_score'] >= 80:
            parts.append(f"Strong skills alignment ({int(breakdown['skill_match_percentage'])}% match)")
        elif breakdown.get('missing_required_skills'):
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
        top_reason = f"{best} ({int(scores[best])}%)"
        
        if scores[worst] < 70:
            improve = f"Improve your {worst.lower()} match (currently {int(scores[worst])}%)"
        else:
            improve = "All factors are well-matched!"
        
        return explanation, top_reason, improve
