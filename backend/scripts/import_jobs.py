import json
import os
import sys

# Add the backend directory to sys.path to allow importing from app
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.database import SessionLocal, init_db
from app.models import Job, Skill, job_skills
from sqlalchemy import insert

def import_jobs_from_json(file_path: str):
    # Initialize database tables
    init_db()
    
    db = SessionLocal()
    
    try:
        with open(file_path, 'r') as f:
            data = json.load(f)
            
        # 1. Import Skills Taxonomy
        print("Importing skills taxonomy...")
        skill_map = {} # Name -> Skill Object
        
        for skill_data in data.get('skills_taxonomy', []):
            existing_skill = db.query(Skill).filter(Skill.name == skill_data['name']).first()
            if not existing_skill:
                skill = Skill(
                    name=skill_data['name'],
                    category=skill_data.get('category'),
                    difficulty_level=skill_data.get('difficulty_level', 1),
                    prerequisites=skill_data.get('prerequisites', [])
                )
                db.add(skill)
                db.flush() # To get the ID
                skill_map[skill.name] = skill
                print(f"  Added skill: {skill.name}")
            else:
                skill_map[existing_skill.name] = existing_skill
                print(f"  Skill already exists: {existing_skill.name}")

        # 2. Import Jobs
        print("\nImporting jobs...")
        for job_data in data.get('jobs', []):
            existing_job = db.query(Job).filter(
                Job.title == job_data['title'], 
                Job.company == job_data['company']
            ).first()
            
            if not existing_job:
                job = Job(
                    title=job_data['title'],
                    company=job_data['company'],
                    description=job_data['description'],
                    location=job_data['location'],
                    is_remote=job_data.get('is_remote', False),
                    salary_min=job_data.get('salary_min'),
                    salary_max=job_data.get('salary_max'),
                    min_experience_years=float(job_data.get('min_experience_years', 0)),
                    max_experience_years=float(job_data.get('max_experience_years', 0))
                )
                db.add(job)
                db.flush() # To get the ID
                
                # Link required skills
                for skill_name in job_data.get('required_skills', []):
                    skill = skill_map.get(skill_name)
                    if not skill:
                        # Create skill if it doesn't exist in taxonomy
                        skill = Skill(name=skill_name, category="Other")
                        db.add(skill)
                        db.flush()
                        skill_map[skill_name] = skill
                    
                    # Associate using the join table
                    db.execute(
                        insert(job_skills).values(
                            job_id=job.id,
                            skill_id=skill.id,
                            is_required=True
                        )
                    )
                
                # Link nice-to-have skills
                for skill_name in job_data.get('nice_to_have_skills', []):
                    skill = skill_map.get(skill_name)
                    if not skill:
                        skill = Skill(name=skill_name, category="Other")
                        db.add(skill)
                        db.flush()
                        skill_map[skill_name] = skill
                    
                    db.execute(
                        insert(job_skills).values(
                            job_id=job.id,
                            skill_id=skill.id,
                            is_required=False
                        )
                    )
                
                print(f"  Added job: {job.title} at {job.company}")
            else:
                print(f"  Job already exists: {job_data['title']} at {job_data['company']}")

        db.commit()
        print("\n✅ Import completed successfully!")

    except Exception as e:
        print(f"❌ Error during import: {e}")
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    json_path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'data', 'jobs.json')
    if os.path.exists(json_path):
        import_jobs_from_json(json_path)
    else:
        print(f"Error: Could not find {json_path}")
