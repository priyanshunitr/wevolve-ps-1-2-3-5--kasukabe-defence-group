"""
Actionable Growth Router
Simplified API endpoints - business logic delegated to services
"""
import json
from pathlib import Path
from fastapi import APIRouter, HTTPException

from ..schemas.roadmap import RoadmapRequest, RoadmapResponse
from ..services import RoadmapGenerator

router = APIRouter(prefix="/api/roadmap", tags=["Actionable Growth"])

# Service instance
generator = RoadmapGenerator()


@router.post("/generate", response_model=RoadmapResponse)
async def generate_roadmap(request: RoadmapRequest):
    """
    Generate a personalized learning roadmap based on skill gaps.
    Uses topological sorting to order skills by dependencies.
    """
    # Load jobs data
    jobs_file = Path(__file__).parent.parent.parent / "data" / "jobs.json"
    
    try:
        with open(jobs_file, 'r') as f:
            data = json.load(f)
            jobs = {j['id']: j for j in data.get('jobs', [])}
    except FileNotFoundError:
        raise HTTPException(status_code=404, detail="Jobs data not found")
    
    # Get target job
    job = jobs.get(request.target_job_id)
    if not job:
        raise HTTPException(status_code=404, detail=f"Job with ID {request.target_job_id} not found")
    
    # Identify missing skills
    current_skills_lower = {s.lower() for s in request.current_skills}
    required_skills = job.get('required_skills', [])
    optional_skills = job.get('nice_to_have_skills', [])
    all_job_skills = required_skills + optional_skills
    missing_skills = [s for s in all_job_skills if s.lower() not in current_skills_lower]
    
    # Handle perfect match case
    if not missing_skills:
        return RoadmapResponse(
            target_job=job['title'],
            target_company=job['company'],
            current_match_score=100.0,
            projected_match_score=100.0,
            missing_skills_count=0,
            phases=[],
            total_estimated_weeks=0,
            total_estimated_hours=0,
            summary="Congratulations! You already have all the skills for this role.",
            motivation_message="🎉 You're ready to apply! Your skills are a perfect match."
        )
    
    # Sort skills by dependencies and build phases
    skill_phases = generator.topological_sort_skills(missing_skills)
    phases, total_weeks, total_hours = generator.build_phases(
        skill_phases, required_skills, request.learning_pace
    )
    
    # Calculate scores
    matching_count = len(request.current_skills)
    total_count = len(all_job_skills)
    current_score = (matching_count / total_count * 100) if total_count > 0 else 0
    
    # Generate summary
    weeks_text = f"{int(total_weeks)} weeks" if total_weeks >= 1 else f"{int(total_weeks * 4)} days"
    summary = (
        f"To become a strong candidate for {job['title']} at {job['company']}, "
        f"you need to learn {len(missing_skills)} skills across {len(phases)} phases. "
        f"Estimated timeline: {weeks_text} at a {request.learning_pace} pace."
    )
    
    return RoadmapResponse(
        target_job=job['title'],
        target_company=job['company'],
        current_match_score=round(current_score, 1),
        projected_match_score=100.0,
        missing_skills_count=len(missing_skills),
        phases=phases,
        total_estimated_weeks=total_weeks,
        total_estimated_hours=total_hours,
        summary=summary,
        motivation_message=generator.get_motivation_message(len(missing_skills), total_weeks)
    )


@router.get("/skills")
async def get_available_skills():
    """Get all skills in the taxonomy with their metadata"""
    return {
        skill: {
            "category": data.get("category"),
            "difficulty": data.get("difficulty"),
            "prerequisites": data.get("prerequisites", []),
            "estimated_weeks": data.get("estimated_weeks")
        }
        for skill, data in generator.SKILL_RESOURCES.items()
    }
