import json
import os
from thefuzz import process, fuzz

# Load jobs data
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
jobs_path = os.path.normpath(os.path.join(BASE_DIR, "..", "..", "data", "jobs.json"))

with open(jobs_path, "r") as f:
    data = json.load(f)
    jobs = data.get("jobs", [])


# candidate =  {
#     "skills": ["Python3", "FastAPI", "Docker", "ReactJS"], 
#     "experience_years": 1, 
#     "preferred_locations": ["Bangalore", "Hyderabad"], 
#     "preferred_roles": ["Backend Developer", "Full Stack Developer"], 
#     "expected_salary": 800000, 
#     "education": { 
#       "degree": "B.Tech", 
#       "field": "Computer Science", 
#       "cgpa": 8.5 
#     } 
# }


def calculate_match(candidate, job):
    # 1. Skill Match & Missing Skills using Fuzzy Matching
    MATCH_THRESHOLD = 85
    req_skills = job.get('required_skills', [])
    can_skills = candidate.get('skills', [])
    
    matched_skills = []
    missing_skills = []
    
    for req in req_skills:
        match = process.extractOne(req, can_skills, scorer=fuzz.token_set_ratio)
        if match and match[1] >= MATCH_THRESHOLD:
            matched_skills.append(req)
        else:
            missing_skills.append(req)
    
    skill_score = (len(matched_skills) / len(req_skills)) * 100 if req_skills else 100

    # 2. Location Match
    loc_match = 100 if job['location'] in candidate['preferred_locations'] else 0

    # 3. Salary Match
    min_s, max_s = job.get('salary_min', 0), job.get('salary_max', 0)
    if min_s <= candidate['expected_salary'] <= max_s:
        salary_score = 100
    else:
        # Calculate how far off they are (Simplified)
        if candidate['expected_salary'] < min_s:
            salary_score = max(0, 100 - (abs(candidate['expected_salary'] - min_s) / min_s * 100))
        else:
            salary_score = max(0, 100 - (abs(candidate['expected_salary'] - max_s) / max_s * 100))

    # 4. Experience Match
    min_exp = job.get('min_experience_years', 0)
    exp_score = 100 if candidate['experience_years'] >= min_exp else (candidate['experience_years'] / min_exp * 100 if min_exp > 0 else 100)

    # 5. Role Match
    pref_roles = candidate.get('preferred_roles', [])
    job_title = job.get('title', '')
    if pref_roles and job_title:
        # returns (best_match, score)
        role_match_result = process.extractOne(job_title, pref_roles, scorer=fuzz.token_set_ratio)
        role_score = role_match_result[1] if role_match_result else 0
    else:
        role_score = 70.0  # Neutral score if no preference specified

    # 4. Final Weighted Total
    # You can adjust these weights based on priority
    weights = {"skill": 0.4, "location": 0.2, "salary": 0.15, "experience": 0.15, "role": 0.1}
    total_score = (
        (skill_score * weights['skill']) + 
        (loc_match * weights['location']) + 
        (salary_score * weights['salary']) + 
        (exp_score * weights['experience']) +
        (role_score * weights['role'])
    )
    
    return {
        "job_id": job['id'],
        "job_title": job['title'],
        "match_score": round(total_score, 1),
        "breakdown": {
            "skill_match": skill_score,
            "location_match": loc_match,
            "salary_match": salary_score,
            "experience_match": exp_score,
            "role_match": role_score
        },
        "missing_skills": missing_skills
    }

if __name__ == "__main__":
    # Run the matching for all jobs
    print(f"\n--- Match Results for {candidate['education']['field']} Candidate ---")
    print(f"Skills: {', '.join(candidate['skills'])}")
    print("-" * 50)

    for job in jobs:
        result = calculate_match(candidate, job)
        print(f"Job: {result['job_title']} (ID: {result['job_id']})")
        print(f"Score: {result['match_score']}%")
        print(f"Skill Match: {result['breakdown']['skill_match']}%")
        print(f"Location Match: {result['breakdown']['location_match']}%")
        print(f"Salary Match: {result['breakdown']['salary_match']}%")
        print(f"Experience Match: {result['breakdown']['experience_match']}%")
        print(f"Role Match: {result['breakdown']['role_match']}%")
        if result['missing_skills']:
            print(f"Missing Skills: {', '.join(result['missing_skills'])}")
        print("-" * 30)

