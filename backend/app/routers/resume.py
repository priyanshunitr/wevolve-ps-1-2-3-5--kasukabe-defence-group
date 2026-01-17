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
        'location': parser.extract_location(text),
        'current_role': ExtractedField(value="", confidence=0, source="Not implemented", needs_review=True),
        'years_of_experience': parser.extract_experience_years(text),
        'skills': parser.extract_skills(text),
        'education': parser.extract_education(text),
        'work_experience': [],
    }
    
    # Initialize preference fields (can be updated manually later)
    # If using Python 3.9+, use union operator |, else iterate
    parsed_with_defaults = parsed.copy()
    parsed_with_defaults['preferred_locations'] = []
    parsed_with_defaults['preferred_roles'] = []
    parsed_with_defaults['expected_salary'] = None
    
    overall_confidence = parser.calculate_overall_confidence(parsed)
    
    # --- SAVE TO DB IMMEDIATELY ---
    candidate = Candidate(
        full_name=parsed['full_name'].value,
        email=parsed['email'].value,
        phone=parsed['phone'].value,
        location=parsed['location'].value,
        current_role=parsed['current_role'].value,
        years_of_experience=parsed['years_of_experience'].value,
        raw_resume_text=text,
        education=parsed['education'],
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
    candidate = db.query(Candidate).filter(Candidate.id == candidate_id).first()
    
    if not candidate:
        raise HTTPException(
            status_code=404, 
            detail=f"Candidate with ID {candidate_id} not found"
        )
    
    # Update fields with potentially corrected values
    candidate.full_name = profile.full_name.value
    candidate.email = profile.email.value
    candidate.phone = profile.phone.value
    candidate.location = profile.location.value
    candidate.current_role = profile.current_role.value
    candidate.years_of_experience = profile.years_of_experience.value
    
    # Update Education
    candidate.education = profile.education
    
    # Update Manual Preferences
    candidate.preferred_locations = profile.preferred_locations
    candidate.preferred_roles = profile.preferred_roles
    candidate.expected_salary_min = profile.expected_salary  # Storing single value as min
    
    db.commit()
    db.refresh(candidate)
    
    return {"message": "Profile updated successfully", "candidate_id": candidate.id}
