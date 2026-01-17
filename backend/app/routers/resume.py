"""
Resume Intelligence Router
Simplified API endpoints - business logic delegated to services
"""
from fastapi import APIRouter, UploadFile, File, HTTPException, Depends
from sqlalchemy.orm import Session

from ..db import get_db, Candidate
from ..schemas import ParsedResume, ExtractedField
from ..services import ResumeParser

router = APIRouter(prefix="/api/resume", tags=["Resume Intelligence"])

parser = ResumeParser()


@router.post("/parse", response_model=ParsedResume)
async def parse_resume(file: UploadFile = File(...), db: Session = Depends(get_db)):
    """
    Parse an uploaded resume (PDF/DOCX) and extract structured data.
    Saves the initial parse to the database and returns the result.
    """
    allowed_types = {
        "application/pdf": "pdf",
        "application/vnd.openxmlformats-officedocument.wordprocessingml.document": "docx"
    }
    
    if file.content_type not in allowed_types:
        raise HTTPException(
            status_code=400,
            detail=f"Invalid file type: {file.content_type}. Please upload PDF or DOCX."
        )
    
    content = await file.read()
    file_type = allowed_types[file.content_type]
    
    try:
        if file_type == "pdf":
            text = parser.extract_text_from_pdf(content)
        else:
            text = parser.extract_text_from_docx(content)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error parsing file: {str(e)}")
    
    if not text or len(text.strip()) < 50:
        raise HTTPException(
            status_code=400,
            detail="Could not extract sufficient text from the document."
        )
    
    # Extract all fields using service
    parsed = {
        'full_name': parser.extract_name(text),
        'email': parser.extract_email(text),
        'phone': parser.extract_phone(text),
        'years_of_experience': parser.extract_experience_years(text),
        'skills': parser.extract_skills(text),
        'education': parser.extract_education(text),
        'work_experience': parser.extract_work_experience(text),
        'projects': parser.extract_projects(text),
    }
    
    # Initialize preference fields (can be updated manually later)
    # If using Python 3.9+, use union operator |, else iterate
    parsed_with_defaults = parsed.copy()
    parsed_with_defaults['preferred_locations'] = []
    parsed_with_defaults['preferred_roles'] = []
    parsed_with_defaults['expected_salary'] = None
    
    overall_confidence = parser.calculate_overall_confidence(parsed)
    
    # --- SANITIZE DATA BEFORE SAVING ---
    def sanitize_for_json(data):
        """Recursively replace None values with empty strings for JSON serialization."""
        if isinstance(data, dict):
            return {k: sanitize_for_json(v) for k, v in data.items()}
        elif isinstance(data, list):
            return [sanitize_for_json(item) for item in data]
        elif data is None:
            return ""
        return data
    
    sanitized_education = sanitize_for_json(parsed['education'])
    sanitized_work_experience = sanitize_for_json(parsed['work_experience'])
    sanitized_projects = sanitize_for_json(parsed['projects'])
    
    # Update parsed with sanitized projects
    parsed['projects'] = sanitized_projects
    
    # --- SAVE TO DB IMMEDIATELY ---
    try:
        candidate = Candidate(
            full_name=parsed['full_name'].value or "",
            email=parsed['email'].value or "",
            phone=parsed['phone'].value or "",
            years_of_experience=parsed['years_of_experience'].value or 0,
            raw_resume_text=text,
            education=sanitized_education,
            work_experience=sanitized_work_experience,
            projects=sanitized_projects,
            confidence_scores={
                'full_name': parsed['full_name'].confidence,
                'email': parsed['email'].confidence,
                'overall': overall_confidence
            },
            # Initialize preferences as empty
            preferred_locations=[],
            preferred_roles=[]
        )
        db.add(candidate)
        db.commit()
        db.refresh(candidate)
    except Exception as db_error:
        db.rollback()
        raise HTTPException(
            status_code=500,
            detail=f"Database error while saving candidate: {str(db_error)}"
        )
    
   
    response = ParsedResume(
        **parsed_with_defaults,
        overall_confidence=overall_confidence,
        raw_text=text[:2000]
    )
    
    setattr(response, "id", candidate.id)
    
    return response


@router.post("/save/{candidate_id}")
async def save_parsed_profile(
    candidate_id: int,
    profile: ParsedResume,
    db: Session = Depends(get_db)
):
    """
    Update a parsed profile with user corrections.
    """
    """
    Update a parsed profile with user corrections.
    """
    try:
        candidate = db.query(Candidate).filter(Candidate.id == candidate_id).first()
        
        if not candidate:
            raise HTTPException(
                status_code=404, 
                detail=f"Candidate with ID {candidate_id} not found"
            )
        
        # Update fields with potentially corrected values
        # Add basic null safety
        candidate.full_name = profile.full_name.value or ""
        candidate.email = profile.email.value or ""
        candidate.phone = profile.phone.value or ""
        
        try:
            candidate.years_of_experience = float(profile.years_of_experience.value)
        except (ValueError, TypeError):
             candidate.years_of_experience = 0.0
        
        # Update Education - Convert models to dicts
        candidate.education = [e.model_dump() for e in profile.education] if profile.education else []
        
        # Update Manual Preferences
        candidate.preferred_locations = profile.preferred_locations or []
        candidate.preferred_roles = profile.preferred_roles or []
        candidate.expected_salary_min = profile.expected_salary
        
        # We should also update work_experience if it's in the profile
        if profile.work_experience:
             candidate.work_experience = [w.model_dump() for w in profile.work_experience]
             
        # Update Projects
        if hasattr(profile, 'projects') and profile.projects:
            candidate.projects = [p.model_dump() for p in profile.projects]
        
        db.commit()
        db.refresh(candidate)
        
        return {"message": "Profile updated successfully", "candidate_id": candidate.id}
    except HTTPException:
        raise
    except Exception as e:
        import traceback
        traceback.print_exc()
        db.rollback()
        raise HTTPException(
            status_code=500,
            detail=f"Error saving profile: {str(e)}"
        )
