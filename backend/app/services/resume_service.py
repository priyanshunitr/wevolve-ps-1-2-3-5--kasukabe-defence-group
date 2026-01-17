"""
Resume Parsing Service
Handles text extraction and data parsing from resumes
"""
import re
import io
from typing import List, Dict, Any

from ..schemas.resume import ExtractedField


class ResumeParser:
    """Service for parsing and extracting data from resumes"""
    
    # Regex patterns
    EMAIL_REGEX = re.compile(r'[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}')
    PHONE_REGEX = re.compile(r'(?:\+91[\-\s]?)?[6-9]\d{9}|(?:\+1[\-\s]?)?\d{3}[\-\s]?\d{3}[\-\s]?\d{4}')
    
    # Known skills taxonomy
    KNOWN_SKILLS = {
        "python", "javascript", "typescript", "java", "c++", "c#", "go", "rust", "ruby", "php",
        "react", "angular", "vue", "nextjs", "django", "flask", "fastapi", "express", "spring",
        "sql", "postgresql", "mysql", "mongodb", "redis", "elasticsearch", "dynamodb",
        "aws", "azure", "gcp", "docker", "kubernetes", "terraform", "jenkins",
        "pandas", "numpy", "scikit-learn", "tensorflow", "pytorch", "spark", "airflow",
        "git", "linux", "rest api", "graphql", "microservices", "agile", "scrum"
    }
    
    # Indian cities for location detection
    INDIAN_CITIES = [
        'bangalore', 'bengaluru', 'mumbai', 'delhi', 'hyderabad', 'chennai',
        'pune', 'kolkata', 'ahmedabad', 'jaipur', 'noida', 'gurgaon', 'gurugram'
    ]
    
    def extract_email(self, text: str) -> ExtractedField:
        """Extract email with validation confidence"""
        matches = self.EMAIL_REGEX.findall(text)
        if matches:
            email = matches[0].lower()
            domain = email.split('@')[1] if '@' in email else ''
            trusted = ['gmail.com', 'yahoo.com', 'outlook.com', 'hotmail.com']
            confidence = 100 if domain in trusted else 85
            return ExtractedField(
                value=email, confidence=confidence,
                source="Pattern matching", needs_review=False
            )
        return ExtractedField(value="", confidence=0, source="Not found", needs_review=True)
    
    def extract_phone(self, text: str) -> ExtractedField:
        """Extract phone number"""
        matches = self.PHONE_REGEX.findall(text)
        if matches:
            phone = re.sub(r'[\s\-]', '', matches[0])
            confidence = 95 if phone.startswith('+91') or (len(phone) == 10 and phone[0] in '6789') else 80
            return ExtractedField(
                value=phone, confidence=confidence,
                source="Pattern matching", needs_review=False
            )
        return ExtractedField(value="", confidence=0, source="Not found", needs_review=True)
    
    def extract_name(self, text: str) -> ExtractedField:
        """Extract name from resume header"""
        lines = text.strip().split('\n')
        skip_words = {'resume', 'curriculum vitae', 'cv', 'profile', 'contact'}
        
        for line in lines[:5]:
            clean_line = line.strip()
            if clean_line and not any(word in clean_line.lower() for word in skip_words):
                words = clean_line.split()
                if 2 <= len(words) <= 4 and not any(char.isdigit() for char in clean_line):
                    return ExtractedField(
                        value=clean_line.title(), confidence=75,
                        source="First non-header line", needs_review=True
                    )
        return ExtractedField(value="Unknown", confidence=0, source="Could not extract", needs_review=True)
    
    def extract_skills(self, text: str) -> List[ExtractedField]:
        """Extract skills by matching against taxonomy"""
        text_lower = text.lower()
        found_skills = []
        
        for skill in self.KNOWN_SKILLS:
            pattern = r'\b' + re.escape(skill) + r'\b'
            if re.search(pattern, text_lower):
                found_skills.append(ExtractedField(
                    value=skill.title(), confidence=90,
                    source="Skill taxonomy match", needs_review=False
                ))
        return found_skills
    
    def extract_experience_years(self, text: str) -> ExtractedField:
        """Extract years of experience"""
        patterns = [
            r'(\d+)\+?\s*(?:years?|yrs?)\s*(?:of)?\s*experience',
            r'experience\s*[:\-]?\s*(\d+)\+?\s*(?:years?|yrs?)',
            r'(\d+)\+?\s*(?:years?|yrs?)\s*in\s*(?:software|development|tech)',
        ]
        
        for pattern in patterns:
            match = re.search(pattern, text.lower())
            if match:
                return ExtractedField(
                    value=float(match.group(1)), confidence=85,
                    source="Pattern matching", needs_review=True
                )
        return ExtractedField(value=0, confidence=0, source="Could not determine", needs_review=True)
    
    
    def extract_education(self, text: str) -> List[Dict[str, Any]]:
        """Extract education details"""
        education = []
        # Pattern for: Degree in Field, Institute (Year) - CGPA: X.X
        # Example: B.Tech in Computer Science, NIT Rourkela (2022-2026) - CGPA: 8.5
        pattern = r'(?P<degree>B\.?Tech|M\.?Tech|B\.?E|M\.?E|B\.?Sc|M\.?Sc|BCA|MCA|MBA)(?:\s+in\s+(?P<field>[^,]+))?,\s+(?P<institute>[^(]+)\s*\((?P<year>[^)]+)\)(?:\s*-\s*CGPA\s*[:]\s*(?P<cgpa>[\d.]+))?'
        
        matches = re.finditer(pattern, text, re.IGNORECASE)
        for match in matches:
            education.append({
                "degree": match.group("degree"),
                "field": match.group("field").strip() if match.group("field") else "Unknown",
                "institute": match.group("institute").strip(),
                "year": match.group("year"),
                "cgpa": float(match.group("cgpa")) if match.group("cgpa") else None
            })
            
        return education

    def extract_location(self, text: str) -> ExtractedField:
        """Extract location from resume"""
        text_lower = text.lower()
        for city in self.INDIAN_CITIES:
            if city in text_lower:
                return ExtractedField(
                    value=city.title(), confidence=80,
                    source="City name match", needs_review=True
                )
        return ExtractedField(value="", confidence=0, source="Not found", needs_review=True)
    
    def calculate_overall_confidence(self, parsed: Dict) -> int:
        """Calculate weighted overall confidence score"""
        weights = {
            'email': 0.20, 'phone': 0.10, 'full_name': 0.15,
            'skills': 0.30, 'experience': 0.15, 'location': 0.10
        }
        
        total = 0
        total += parsed['email'].confidence * weights['email']
        total += parsed['phone'].confidence * weights['phone']
        total += parsed['full_name'].confidence * weights['full_name']
        total += parsed['location'].confidence * weights['location']
        total += parsed['years_of_experience'].confidence * weights['experience']
        
        if parsed['skills']:
            avg_skill_conf = sum(s.confidence for s in parsed['skills']) / len(parsed['skills'])
            total += avg_skill_conf * weights['skills']
        
        return int(total)
    
    @staticmethod
    def extract_text_from_pdf(content: bytes) -> str:
        """Extract text from PDF"""
        try:
            import pdfplumber
            with pdfplumber.open(io.BytesIO(content)) as pdf:
                return '\n'.join(page.extract_text() or '' for page in pdf.pages)
        except ImportError:
            return "[PDF parsing library not available]"
    
    @staticmethod
    def extract_text_from_docx(content: bytes) -> str:
        """Extract text from DOCX"""
        try:
            from docx import Document
            doc = Document(io.BytesIO(content))
            return '\n'.join(p.text for p in doc.paragraphs)
        except ImportError:
            return "[DOCX parsing library not available]"
