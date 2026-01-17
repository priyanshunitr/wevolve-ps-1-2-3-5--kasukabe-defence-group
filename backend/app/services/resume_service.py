"""
Resume Parsing Service - Master Rule Implementation
Implements the complete "Master Rule List" for robust resume parsing:
1. Sectionizer - Zone-based text splitting
2. Contact Information - Strict Regex + Validation
3. Name Extraction - Heuristic Filtering
4. Education - Fuzzy Clustering with Proximity Rule
5. Experience - Date Math Calculation
6. Skills - Contextual Density
7. Location - City + Pincode
8. Projects - Title vs Description Detection + Tech Stack Extraction
"""
import re
import io
from typing import List, Dict, Any, Optional, Tuple
from datetime import datetime
from dateutil import parser as date_parser
from dateutil.relativedelta import relativedelta

from ..schemas.resume import ExtractedField


class ResumeParser:
    """
    Advanced Resume Parser with Master Rule Implementation
    Handles messy internet resumes with zone-based parsing
    """
    
    # ============================================================
    # SECTION HEADERS for Zone Detection (Rule 1)
    # ============================================================
    SECTION_KEYWORDS = {
        'education': ['education', 'academic', 'qualification', 'academics', 'scholastic'],
        'experience': ['experience', 'employment', 'work history', 'career', 'professional background'],
        'skills': ['skills', 'technical skills', 'technologies', 'tools', 'competencies', 'expertise'],
        'projects': ['projects', 'academic projects', 'personal projects', 'key projects'],
        'contact': ['contact', 'personal info', 'personal details', 'reach me'],
        'summary': ['summary', 'objective', 'about me', 'profile', 'career objective'],
        'certifications': ['certifications', 'certificates', 'courses', 'training'],
        'achievements': ['achievements', 'awards', 'honors', 'accomplishments']
    }
    
    # ============================================================
    # REGEX PATTERNS (Rule 2)
    # ============================================================
    EMAIL_REGEX = re.compile(r'[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}')
    
    # Comprehensive phone regex (supports international formats)
    PHONE_REGEX = re.compile(
        r'(?:(?:\+|00)([1-9]\d{0,2})[\s.\-]?)?'  # Country code
        r'(?:\(?\d{2,5}\)?[\s.\-]?)?'             # Area code
        r'\d{3,5}[\s.\-]?\d{3,5}'                 # Main number
    )
    
    # Date range patterns for experience calculation
    DATE_RANGE_REGEX = re.compile(
        r'((?:Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)[a-z]*[\s,]*\d{4}|'
        r'\d{1,2}/\d{4}|\d{4})'
        r'\s*[-–—to]+\s*'
        r'((?:Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)[a-z]*[\s,]*\d{4}|'
        r'\d{1,2}/\d{4}|\d{4}|Present|Current|Till Date|Ongoing)',
        re.IGNORECASE
    )
    
    # Pincode regex (Indian 6-digit, not starting with 0)
    PINCODE_REGEX = re.compile(r'\b[1-9]\d{5}\b')
    
    # CGPA/GPA extraction
    CGPA_REGEX = re.compile(r'(?:CGPA|GPA|Grade)[:\s]*(\d+\.?\d*)\s*(?:/\s*10)?', re.IGNORECASE)
    PERCENTAGE_REGEX = re.compile(r'(\d{2,3}(?:\.\d+)?)\s*%')
    
    # ============================================================
    # TRUSTED DOMAINS for Email Validation (Rule 2)
    # ============================================================
    TRUSTED_DOMAINS = {
        'gmail.com', 'yahoo.com', 'outlook.com', 'hotmail.com',
        'icloud.com', 'protonmail.com', 'mail.com',
        # Indian educational domains
        'edu.in', 'ac.in', 'iitb.ac.in', 'iitd.ac.in', 'iitk.ac.in',
        'iitkgp.ac.in', 'bits-pilani.ac.in', 'nitrkl.ac.in'
    }
    
    # ============================================================
    # NAME STOPWORDS (Rule 3)
    # ============================================================
    NAME_STOPWORDS = {
        'resume', 'cv', 'curriculum vitae', 'mobile', 'email', 'address',
        'page', 'contact', 'phone', 'tel', 'linkedin', 'github', 'portfolio',
        'http', 'www', '@', 'objective', 'summary'
    }
    
    # ============================================================
    # DEGREE KEYWORDS for Education (Rule 4)
    # ============================================================
    DEGREE_KEYWORDS = {
        'b.tech', 'btech', 'b tech', 'm.tech', 'mtech', 'm tech',
        'b.e', 'be', 'b e', 'm.e', 'me', 'm e',
        'b.sc', 'bsc', 'b sc', 'm.sc', 'msc', 'm sc',
        'bca', 'mca', 'bba', 'mba', 'b.com', 'bcom', 'm.com', 'mcom',
        'phd', 'ph.d', 'doctorate', 'bachelor', 'master', 'diploma',
        'hsc', 'ssc', 'cbse', 'icse', '10th', '12th', 'intermediate',
        'b.a', 'ba', 'm.a', 'ma', 'b.ed', 'bed', 'm.ed', 'med'
    }
    
    INSTITUTE_KEYWORDS = {
        'university', 'institute', 'college', 'school', 'academy',
        'iit', 'nit', 'iiit', 'bits', 'vit', 'srm', 'manipal',
        'engineering', 'technology', 'polytechnic', 'vidyalaya'
    }
    
    # ============================================================
    # JOB TITLE KEYWORDS for Experience (Rule 5)
    # ============================================================
    JOB_TITLE_KEYWORDS = {
        'intern', 'internship', 'trainee', 'associate', 'assistant',
        'developer', 'engineer', 'analyst', 'designer', 'architect',
        'manager', 'lead', 'senior', 'junior', 'principal', 'staff',
        'consultant', 'specialist', 'administrator', 'coordinator',
        'executive', 'officer', 'head', 'director', 'vp', 'cto', 'ceo'
    }
    
    # ============================================================
    # SKILLS TAXONOMY (Rule 6)
    # ============================================================
    # Short/ambiguous skills that need context
    AMBIGUOUS_SKILLS = {'c', 'r', 'go', 'vue', 'dart', 'rust', 'swift', 'perl'}
    
    KNOWN_SKILLS = {
        # Programming Languages
        "python", "javascript", "typescript", "java", "c++", "c#", "go", "rust",
        "ruby", "php", "swift", "kotlin", "scala", "perl", "r", "matlab", "dart",
        "c", "objective-c", "groovy", "lua", "haskell", "elixir", "clojure",
        
        # Frontend Frameworks
        "react", "angular", "vue", "nextjs", "nuxt", "svelte", "gatsby", "remix",
        "jquery", "bootstrap", "tailwind", "tailwindcss", "material-ui", "chakra",
        "html", "css", "sass", "scss", "less", "webpack", "vite", "parcel",
        
        # Backend Frameworks
        "django", "flask", "fastapi", "express", "nestjs", "spring", "spring boot",
        "rails", "laravel", "asp.net", "gin", "fiber", "actix", "rocket",
        
        # Databases
        "sql", "postgresql", "postgres", "mysql", "mongodb", "redis", "elasticsearch",
        "dynamodb", "cassandra", "neo4j", "sqlite", "oracle", "mariadb", "couchdb",
        "firebase", "supabase", "prisma", "sqlalchemy", "sequelize", "mongoose",
        
        # Cloud & DevOps
        "aws", "azure", "gcp", "google cloud", "heroku", "vercel", "netlify",
        "docker", "kubernetes", "k8s", "terraform", "ansible", "jenkins", "gitlab",
        "github actions", "circleci", "travis", "nginx", "apache", "linux", "unix",
        
        # Data & ML
        "pandas", "numpy", "scikit-learn", "tensorflow", "pytorch", "keras",
        "spark", "hadoop", "airflow", "kafka", "flink", "dbt", "snowflake",
        "tableau", "power bi", "matplotlib", "seaborn", "plotly", "opencv",
        "nlp", "machine learning", "deep learning", "data science", "ai",
        
        # Tools & Others
        "git", "github", "gitlab", "bitbucket", "jira", "confluence", "slack",
        "rest api", "graphql", "grpc", "websocket", "oauth", "jwt", "api",
        "microservices", "agile", "scrum", "kanban", "ci/cd", "devops",
        "testing", "jest", "pytest", "selenium", "cypress", "postman",
        "figma", "sketch", "adobe xd", "photoshop", "illustrator"
    }
    
    # ============================================================
    # INDIAN CITIES & STATES (Rule 7)
    # ============================================================
    INDIAN_CITIES = {
        'bangalore', 'bengaluru', 'mumbai', 'delhi', 'new delhi', 'hyderabad',
        'chennai', 'pune', 'kolkata', 'ahmedabad', 'jaipur', 'noida', 'gurgaon',
        'gurugram', 'ghaziabad', 'faridabad', 'lucknow', 'kanpur', 'nagpur',
        'indore', 'bhopal', 'patna', 'vadodara', 'surat', 'kochi', 'thiruvananthapuram',
        'coimbatore', 'visakhapatnam', 'chandigarh', 'mysore', 'mangalore',
        'rourkela', 'bhubaneswar', 'cuttack'
    }
    
    INDIAN_STATES = {
        'andhra pradesh', 'arunachal pradesh', 'assam', 'bihar', 'chhattisgarh',
        'goa', 'gujarat', 'haryana', 'himachal pradesh', 'jharkhand', 'karnataka',
        'kerala', 'madhya pradesh', 'maharashtra', 'manipur', 'meghalaya', 'mizoram',
        'nagaland', 'odisha', 'punjab', 'rajasthan', 'sikkim', 'tamil nadu',
        'telangana', 'tripura', 'uttar pradesh', 'uttarakhand', 'west bengal',
        'delhi', 'jammu and kashmir', 'ladakh'
    }
    
    # Pincode to City mapping (sample - can be extended)
    PINCODE_CITY_MAP = {
        '560': 'Bangalore', '400': 'Mumbai', '110': 'Delhi', '500': 'Hyderabad',
        '600': 'Chennai', '411': 'Pune', '700': 'Kolkata', '380': 'Ahmedabad',
        '302': 'Jaipur', '201': 'Noida', '122': 'Gurgaon', '769': 'Rourkela',
        '751': 'Bhubaneswar'
    }
    
    # ============================================================
    # PROJECT DETECTION RULES (Rule 8)
    # ============================================================
    
    # Rule B: Action Verbs that indicate DESCRIPTION (not title)
    ACTION_VERBS = {
        'developed', 'created', 'built', 'implemented', 'designed', 'fixed',
        'established', 'launched', 'deployed', 'integrated', 'optimized',
        'maintained', 'managed', 'led', 'coordinated', 'improved', 'enhanced',
        'refactored', 'migrated', 'configured', 'automated', 'analyzed',
        'tested', 'debugged', 'resolved', 'achieved', 'reduced', 'increased',
        'streamlined', 'collaborated', 'contributed', 'utilized', 'leveraged'
    }
    
    # Rule C: Noun Signals that indicate PROJECT TITLE
    PROJECT_NOUN_SIGNALS = {
        'system', 'app', 'application', 'clone', 'portal', 'dashboard',
        'engine', 'api', 'model', 'detector', 'bot', 'platform', 'website',
        'tool', 'framework', 'library', 'service', 'manager', 'analyzer',
        'generator', 'tracker', 'monitor', 'classifier', 'predictor',
        'scraper', 'crawler', 'simulator', 'calculator', 'converter',
        'chatbot', 'assistant', 'interface', 'pipeline', 'network'
    }
    
    # Tech Stack Keywords (Rule A for tech detection)
    TECH_STACK_LABELS = {
        'tech stack:', 'technology:', 'technologies:', 'key skills:',
        'environment:', 'tools:', 'stack:', 'tech:'
    }
    
    # Rule C: Connectors that separate title from tech stack
    TECH_STACK_CONNECTORS = {'using', 'built with', 'with', 'powered by', 'made with'}

    # ============================================================
    # RULE 1: SECTIONIZER - Zone-based Text Splitting
    # ============================================================
    def sectionize(self, text: str) -> Dict[str, str]:
        """
        Split resume into zones based on section headers.
        Returns a dict with section names as keys and their content as values.
        """
        lines = text.split('\n')
        sections = {'header': '', 'unknown': ''}
        current_section = 'header'
        
        for i, line in enumerate(lines):
            line_lower = line.lower().strip()
            words = line_lower.split()
            
            # Check if this line is a section header (< 5 words + contains keyword)
            if len(words) < 5 and line.strip():
                detected_section = None
                for section_name, keywords in self.SECTION_KEYWORDS.items():
                    if any(kw in line_lower for kw in keywords):
                        detected_section = section_name
                        break
                
                if detected_section:
                    current_section = detected_section
                    if current_section not in sections:
                        sections[current_section] = ''
                    continue  # Don't add the header line itself
            
            # Add line to current section
            if current_section in sections:
                sections[current_section] += line + '\n'
            else:
                sections[current_section] = line + '\n'
        
        return sections

    # ============================================================
    # RULE 2: EMAIL EXTRACTION with Domain Validation
    # ============================================================
    def extract_email(self, text: str) -> ExtractedField:
        """Extract email with domain-based confidence scoring."""
        matches = self.EMAIL_REGEX.findall(text)
        
        if matches:
            email = matches[0].lower()
            domain = email.split('@')[1] if '@' in email else ''
            
            # Check if domain is trusted
            is_trusted = domain in self.TRUSTED_DOMAINS
            # Also check for .edu.in, .ac.in patterns
            is_educational = domain.endswith('.edu.in') or domain.endswith('.ac.in')
            
            if is_trusted or is_educational:
                confidence = 100
            else:
                confidence = 80  # Reduce by 20% for unknown domains
            
            return ExtractedField(
                value=email,
                confidence=confidence
            )
        
        return ExtractedField(value="", confidence=0)

    # ============================================================
    # RULE 2: PHONE EXTRACTION with Length Validation
    # ============================================================
    def extract_phone(self, text: str) -> ExtractedField:
        """Extract phone with length validation."""
        matches = self.PHONE_REGEX.findall(text)
        
        # Also try simpler patterns for Indian numbers
        simple_patterns = [
            r'\+91[\s\-]?[6-9]\d{9}',
            r'[6-9]\d{9}',
            r'\d{5}[\s\-]?\d{5}'
        ]
        
        all_matches = []
        for pattern in simple_patterns:
            found = re.findall(pattern, text)
            all_matches.extend(found)
        
        for match in all_matches:
            # Strip non-digits for length check
            digits_only = re.sub(r'\D', '', match)
            
            # Length validation: 10-15 digits
            if 10 <= len(digits_only) <= 15:
                # Format nicely
                if len(digits_only) == 10:
                    formatted = f"+91-{digits_only}"
                    confidence = 95
                elif digits_only.startswith('91') and len(digits_only) == 12:
                    formatted = f"+{digits_only[:2]}-{digits_only[2:]}"
                    confidence = 95
                else:
                    formatted = match
                    confidence = 80
                
                return ExtractedField(
                    value=formatted,
                    confidence=confidence
                )
        
        return ExtractedField(value="", confidence=0)

    # ============================================================
    # RULE 3: NAME EXTRACTION with Heuristic Filtering
    # ============================================================
    def extract_name(self, text: str) -> ExtractedField:
        """
        Extract name using:
        - Top 20 Lines Rule
        - Stopword Filter
        - Shape Filter (Title/Upper case, 2-4 words, no digits/special chars)
        """
        lines = text.strip().split('\n')
        
        # Only search first 20 lines (Top 20 Lines Rule)
        for line in lines[:20]:
            clean_line = line.strip()
            if not clean_line:
                continue
            
            line_lower = clean_line.lower()
            
            # Stopword Filter
            if any(stop in line_lower for stop in self.NAME_STOPWORDS):
                continue
            
            # Shape Filter
            words = clean_line.split()
            
            # Must be 2-4 words
            if not (2 <= len(words) <= 4):
                continue
            
            # Must contain Zero Digits
            if any(char.isdigit() for char in clean_line):
                continue
            
            # Must contain Zero Special Characters (except spaces and dots for initials)
            special_chars = set(clean_line) - set('abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ .')
            if special_chars:
                continue
            
            # Check for Title Case or UPPER CASE
            is_title_case = all(w[0].isupper() for w in words if w)
            is_upper_case = clean_line.isupper()
            
            if is_title_case or is_upper_case:
                # High confidence name found
                name = clean_line.title()  # Normalize to Title Case
                return ExtractedField(
                    value=name,
                    confidence=85
                )
        
        return ExtractedField(
            value="Unknown",
            confidence=0
        )

    # ============================================================
    # RULE 4: EDUCATION EXTRACTION with Fuzzy Clustering
    # ============================================================
    def extract_education(self, text: str) -> List[Dict[str, Any]]:
        """
        Extract education using Proximity Rule:
        - Find Degree keyword lines
        - Find Institute keyword lines
        - Cluster if within 3 lines of each other
        - Extract CGPA from clustered lines
        """
        sections = self.sectionize(text)
        edu_text = sections.get('education', text)  # Fallback to full text
        
        lines = edu_text.split('\n')
        education_entries = []
        
        # Find all degree and institute line indices
        degree_lines = []
        institute_lines = []
        
        for i, line in enumerate(lines):
            line_lower = line.lower()
            
            # Check for degree keywords
            if any(deg in line_lower for deg in self.DEGREE_KEYWORDS):
                degree_lines.append((i, line.strip()))
            
            # Check for institute keywords
            if any(inst in line_lower for inst in self.INSTITUTE_KEYWORDS):
                institute_lines.append((i, line.strip()))
        
        # Cluster degrees with nearest institutes (within 3 lines)
        used_institutes = set()
        
        for deg_idx, degree_line in degree_lines:
            best_institute = None
            best_distance = float('inf')
            
            for inst_idx, inst_line in institute_lines:
                if inst_idx in used_institutes:
                    continue
                distance = abs(deg_idx - inst_idx)
                if distance <= 3 and distance < best_distance:
                    best_distance = distance
                    best_institute = (inst_idx, inst_line)
            
            if best_institute:
                used_institutes.add(best_institute[0])
                
                # Extract CGPA from nearby lines (within cluster)
                cluster_start = min(deg_idx, best_institute[0])
                cluster_end = max(deg_idx, best_institute[0]) + 1
                cluster_text = '\n'.join(lines[cluster_start:cluster_end + 1])
                
                cgpa = None
                cgpa_match = self.CGPA_REGEX.search(cluster_text)
                if cgpa_match:
                    cgpa = float(cgpa_match.group(1))
                else:
                    # Try percentage
                    pct_match = self.PERCENTAGE_REGEX.search(cluster_text)
                    if pct_match:
                        cgpa = float(pct_match.group(1))
                
                # Extract year
                year_match = re.search(r'20\d{2}(?:\s*[-–]\s*20\d{2})?', cluster_text)
                year = year_match.group(0) if year_match else None
                
                # Parse degree type
                degree_type = self._extract_degree_type(degree_line)
                
                education_entries.append({
                    'degree': degree_type,
                    'field': self._extract_field(degree_line),
                    'institute': best_institute[1],
                    'year': year,
                    'cgpa': cgpa,
                    'confidence': 85
                })
            else:
                # No institute found, add degree alone
                education_entries.append({
                    'degree': self._extract_degree_type(degree_line),
                    'field': self._extract_field(degree_line),
                    'institute': '',
                    'year': None,
                    'cgpa': None,
                    'confidence': 60
                })
        
        return education_entries
    
    def _extract_degree_type(self, line: str) -> str:
        """Extract the degree type from a line."""
        line_lower = line.lower()
        for deg in sorted(self.DEGREE_KEYWORDS, key=len, reverse=True):
            if deg in line_lower:
                return deg.upper().replace('.', '')
        return 'Unknown'
    
    def _extract_field(self, line: str) -> str:
        """Extract field of study from a line."""
        # Common patterns: "in Computer Science", "- Electronics"
        patterns = [
            r'in\s+([A-Za-z\s]+?)(?:\s*,|\s*\(|$)',
            r'-\s*([A-Za-z\s]+?)(?:\s*,|\s*\(|$)',
            r'(?:Computer Science|Electronics|Mechanical|Civil|Chemical|IT|Information Technology)'
        ]
        for pattern in patterns:
            match = re.search(pattern, line, re.IGNORECASE)
            if match:
                return match.group(1).strip() if match.lastindex else match.group(0).strip()
        return 'Not specified'

    # ============================================================
    # RULE 5: EXPERIENCE EXTRACTION with Date Math
    # ============================================================
    def extract_experience_years(self, text: str) -> ExtractedField:
        """
        Calculate total years of experience using Date Math:
        - Extract all date ranges
        - Calculate duration for each
        - Sum up total experience
        """
        sections = self.sectionize(text)
        exp_text = sections.get('experience', text)
        
        # Find all date ranges
        date_matches = self.DATE_RANGE_REGEX.findall(exp_text)
        
        total_months = 0
        roles_found = []
        
        for start_str, end_str in date_matches:
            try:
                # Parse start date
                start_date = self._parse_date(start_str)
                
                # Parse end date (handle "Present")
                if end_str.lower() in ['present', 'current', 'till date', 'ongoing']:
                    end_date = datetime.now()
                else:
                    end_date = self._parse_date(end_str)
                
                if start_date and end_date:
                    # Calculate duration
                    diff = relativedelta(end_date, start_date)
                    months = diff.years * 12 + diff.months
                    if months > 0:
                        total_months += months
                        roles_found.append(f"{start_str} - {end_str}")
            except Exception:
                continue
        
        if total_months > 0:
            years = round(total_months / 12, 1)
            return ExtractedField(
                value=years,
                confidence=90
            )
        
        # Fallback: Try explicit "X years experience" pattern
        explicit_patterns = [
            r'(\d+)\+?\s*(?:years?|yrs?)(?:\s+of)?\s*experience',
            r'experience[:\s]+(\d+)\+?\s*(?:years?|yrs?)',
            r'(\d+)\+?\s*(?:years?|yrs?)\s+in\s+(?:software|development|tech|IT)',
        ]
        
        for pattern in explicit_patterns:
            match = re.search(pattern, text.lower())
            if match:
                return ExtractedField(
                    value=float(match.group(1)),
                    confidence=75
                )
        
        return ExtractedField(
            value=0,
            confidence=0
        )
    
    def _parse_date(self, date_str: str) -> Optional[datetime]:
        """Parse various date formats."""
        try:
            return date_parser.parse(date_str, fuzzy=True)
        except Exception:
            # Try MM/YYYY format
            match = re.match(r'(\d{1,2})/(\d{4})', date_str)
            if match:
                return datetime(int(match.group(2)), int(match.group(1)), 1)
            # Try just year
            match = re.match(r'(\d{4})', date_str)
            if match:
                return datetime(int(match.group(1)), 1, 1)
        return None

    # ============================================================
    # RULE 5: WORK EXPERIENCE EXTRACTION
    # ============================================================
    # ============================================================
    # RULE 5: WORK EXPERIENCE EXTRACTION
    # ============================================================
    def extract_work_experience(self, text: str) -> List[Dict[str, Any]]:
        """Extract structured work experience entries."""
        sections = self.sectionize(text)
        exp_text = sections.get('experience', '')
        
        if not exp_text:
            return []
        
        experiences = []
        lines = exp_text.split('\n')
        
        current_exp = None
        
        for line in lines:
            line = line.strip()
            if not line:
                continue
            
            line_lower = line.lower()
            
            # 1. Check if line is a Date Range
            date_match = self.DATE_RANGE_REGEX.search(line)
            
            # 2. Check if line is a Job Title (with safeguards)
            is_title = self._is_job_title_line(line)
            
            if is_title:
                # Try to extract company from title line
                title_part, company_part = self._split_title_company(line)
                
                # Start new entry
                if current_exp:
                    experiences.append(current_exp)
                
                current_exp = {
                    'title': title_part,
                    'company': company_part,
                    'duration': date_match.group(0) if date_match else '',
                    'description': []
                }
            elif date_match:
                # If we have a current entry without a duration, assign it
                if current_exp and not current_exp['duration']:
                    current_exp['duration'] = date_match.group(0)
                elif current_exp:
                     # Already has duration? Maybe this is a project date or just a stray date. 
                     # For now, treat as description or ignore?
                     # Better: if it's ONLY a date line, maybe it belongs to the current one anyway.
                     pass
                else:
                    # Date without title? Start a placeholder entry
                    current_exp = {
                        'title': '',
                        'company': '',
                        'duration': date_match.group(0),
                        'description': []
                    }
            elif current_exp:
                # Description processing
                # Clean bullet points
                clean_line = line.lstrip('-•*→▪▸ ').strip()
                
                if not current_exp['company'] and len(line.split()) <= 6 and not clean_line.startswith(('I ', 'We ')):
                     # Heuristic: Short line after title might be Company Name
                     # But safeguard against short sentences "I built this."
                     current_exp['company'] = line
                else:
                    current_exp['description'].append(clean_line)
        
        if current_exp:
            experiences.append(current_exp)
        
        return experiences

    def _is_job_title_line(self, line: str) -> bool:
        """Check if a line looks like a job title."""
        line_lower = line.lower()
        words = line_lower.split()
        
        if not words:
            return False
            
        # Guard 1: Action Verbs (Descriptions often start with these)
        first_word = words[0].rstrip(',.:;')
        if first_word in self.ACTION_VERBS:
            return False
            
        # Guard 2: Sentences (End with period?)
        if line.endswith('.'):
            return False
            
        # Guard 3: Bullet points
        if line.startswith(('-', '•', '*', '→')):
            return False
            
        # Check for keywords with boundaries
        for keyword in self.JOB_TITLE_KEYWORDS:
            # Use regex to avoid "architect" matching "architecture"
            if re.search(r'\b' + re.escape(keyword) + r'\b', line_lower):
                return True
                
        return False
    
    def _split_title_company(self, line: str) -> Tuple[str, str]:
        """Split a line into Title and Company if possible."""
        # Common separators: |, -, at, for
        separators = [
            r'\s+\|\s+',           # " | "
            r'\s+-\s+',            # " - " (but careful with hyphens in names)
            r'\s+–\s+',            # En dash
            r'\s+—\s+',            # Em dash
            r'\s+at\s+',           # " at "
            r'\s+for\s+',          # " for "
            r',\s+'                # ", " with space
        ]
        
        for sep in separators:
            parts = re.split(sep, line, maxsplit=1, flags=re.IGNORECASE)
            if len(parts) == 2:
                # Heuristic: Check if parts look reasonable
                # Title part should probably contain a job keyword
                return parts[0].strip(), parts[1].strip()
                
        return line, ""

    # ============================================================
    # RULE 8: PROJECT EXTRACTION with Title vs Description Detection
    # ============================================================
    def extract_projects(self, text: str) -> List[Dict[str, Any]]:
        """
        Extract projects using advanced title vs description detection:
        - Rule A: Period Check (titles don't end with periods)
        - Rule B: Action Verb Guard (descriptions start with action verbs)
        - Rule C: Noun Signal (project nouns boost title confidence)
        - Rule D: Casing Heuristic (ALL CAPS / Title Case = likely title)
        - Rule E: Length Limit (max 10 words / 60 chars for title)
        
        Tech Stack Detection:
        - Rule A: Explicit labels (Tech Stack:, Technology:)
        - Rule B: Parenthetical pattern: "Project Name (React, Node)"
        - Rule C: Connector words: "using", "built with"
        """
        sections = self.sectionize(text)
        projects_text = sections.get('projects', '')
        
        if not projects_text:
            return []
        
        lines = projects_text.split('\n')
        projects = []
        current_project = None
        
        for line in lines:
            line = line.strip()
            if not line:
                continue
            
            # Check if this line is a project title
            is_title, title_confidence, extracted_title, extracted_tech = self._analyze_project_line(line)
            
            if is_title and title_confidence >= 60:
                # Save previous project if exists
                if current_project:
                    # Before saving, scan descriptions for any missed tech
                    self._extract_tech_from_descriptions(current_project)
                    projects.append(current_project)
                
                # Start new project
                current_project = {
                    'title': extracted_title,
                    'tech_stack': extracted_tech if extracted_tech else [],
                    'description': [],
                    'confidence': title_confidence
                }
            elif current_project:
                # This is a description line, add to current project
                # Check for tech stack labels in description
                tech_from_line = self._extract_tech_from_label(line)
                if tech_from_line:
                    current_project['tech_stack'].extend(tech_from_line)
                else:
                    # Clean bullet points and add to description
                    desc_line = line.lstrip('-•*→▪▸ ').strip()
                    if desc_line:
                        current_project['description'].append(desc_line)
                        # Also extract any tech mentions from the description
                        tech_from_desc = self._extract_tech_from_text(desc_line)
                        if tech_from_desc:
                            current_project['tech_stack'].extend(tech_from_desc)
        
        # Don't forget the last project
        if current_project:
            # Before saving, scan descriptions for any missed tech
            self._extract_tech_from_descriptions(current_project)
            projects.append(current_project)
        
        return projects
    
    def _analyze_project_line(self, line: str) -> Tuple[bool, int, str, List[str]]:
        """
        Analyze a line to determine if it's a project title.
        Returns: (is_title, confidence, extracted_title, extracted_tech_stack)
        """
        confidence = 50  # Start neutral
        extracted_title = line
        extracted_tech = []
        
        line_lower = line.lower().strip()
        words = line.split()
        
        # ========== RULE A: Period Check ==========
        # Titles almost never end with a period
        if line.endswith('.'):
            confidence -= 30  # Strong negative signal
        
        # ========== RULE B: Action Verb Guard ==========
        # If line STARTS with an action verb, it's likely a description
        if words:
            first_word = words[0].lower().rstrip(',.:;')
            if first_word in self.ACTION_VERBS:
                # Exception: check if followed by a noun (e.g., "Automated Testing Framework")
                if len(words) > 1:
                    second_word = words[1].lower()
                    if any(noun in second_word for noun in self.PROJECT_NOUN_SIGNALS):
                        confidence += 10  # It's an adjective usage
                    else:
                        confidence -= 40  # Definitely a description
                else:
                    confidence -= 40
        
        # ========== RULE C: Noun Signal ==========
        # Check for project-indicating nouns
        has_noun_signal = any(noun in line_lower for noun in self.PROJECT_NOUN_SIGNALS)
        if has_noun_signal:
            confidence += 25  # Strong positive signal
        
        # ========== RULE D: Casing Heuristic ==========
        if line.isupper():
            # ALL CAPS = likely title
            confidence += 20
        elif self._is_title_case(line):
            # Title Case = likely title
            confidence += 15
        elif line[0].islower() if line else False:
            # Starts lowercase = likely description
            confidence -= 15
        
        # ========== RULE E: Length Limit ==========
        # Titles are typically short
        word_count = len(words)
        char_count = len(line)
        
        if word_count > 10 or char_count > 60:
            confidence -= 25  # Too long for a title
        elif word_count <= 5:
            confidence += 10  # Short = likely title
        
        # ========== TECH STACK EXTRACTION ==========
        
        # Rule B: Parenthetical Pattern - "Project Name (React, Node, Mongo)"
        paren_match = re.search(r'([^(]+)\s*\(([^)]+)\)\s*$', line)
        if paren_match:
            extracted_title = paren_match.group(1).strip()
            paren_content = paren_match.group(2)
            # Check if parenthetical content looks like tech stack
            potential_tech = [t.strip() for t in re.split(r'[,|/]', paren_content)]
            if self._looks_like_tech_stack(potential_tech):
                extracted_tech = potential_tech
                confidence += 15  # This is a common title format
        
        # Rule C: Connector Pattern - "Library System using Java and SQL"
        for connector in self.TECH_STACK_CONNECTORS:
            connector_pattern = rf'\s+{re.escape(connector)}\s+'
            if re.search(connector_pattern, line_lower):
                parts = re.split(connector_pattern, line, maxsplit=1, flags=re.IGNORECASE)
                if len(parts) == 2:
                    extracted_title = parts[0].strip()
                    tech_part = parts[1].strip().rstrip('.')
                    # Parse tech stack (comma or "and" separated)
                    tech_items = re.split(r',\s*|\s+and\s+', tech_part)
                    extracted_tech = [t.strip() for t in tech_items if t.strip()]
                    confidence += 10
                break
        
        # Final determination
        is_title = confidence >= 60
        
        # Normalize confidence to 0-100
        confidence = max(0, min(100, confidence))
        
        return (is_title, confidence, extracted_title, extracted_tech)
    
    def _is_title_case(self, text: str) -> bool:
        """Check if text is in Title Case."""
        words = text.split()
        if not words:
            return False
        
        # Allow small words to be lowercase (a, an, the, of, etc.)
        small_words = {'a', 'an', 'the', 'of', 'in', 'on', 'at', 'to', 'for', 'and', 'or', 'but'}
        
        for i, word in enumerate(words):
            # Skip if it's all special chars or numbers
            if not any(c.isalpha() for c in word):
                continue
            
            # First word must be capitalized
            if i == 0:
                if not word[0].isupper():
                    return False
            else:
                # Small words can be lowercase
                word_clean = word.lower().strip('(),.-:')
                if word_clean in small_words:
                    continue
                # Other words should be capitalized
                if word[0].isalpha() and not word[0].isupper():
                    return False
        
        return True
    
    def _extract_tech_from_label(self, line: str) -> List[str]:
        """Extract tech stack from explicit labels like 'Tech Stack: React, Node'."""
        line_lower = line.lower()
        
        for label in self.TECH_STACK_LABELS:
            if label in line_lower:
                # Extract everything after the label
                idx = line_lower.find(label)
                tech_part = line[idx + len(label):].strip()
                # Parse comma-separated or other separators
                tech_items = re.split(r'[,|/•]', tech_part)
                return [t.strip() for t in tech_items if t.strip()]
        
        return []
    
    def _looks_like_tech_stack(self, items: List[str]) -> bool:
        """Check if a list of items looks like technology names."""
        if not items:
            return False
        
        # If only 1-2 items, be more lenient
        if len(items) <= 2:
            # Check if any item is a known skill or looks like tech
            for item in items:
                item_lower = item.lower().strip()
                if item_lower in self.KNOWN_SKILLS:
                    return True
                # Check if it's short and looks like tech (no spaces, alphanumeric)
                if len(item) <= 20 and re.match(r'^[A-Za-z0-9.#+-]+$', item.strip()):
                    return True
            return False
        
        # For 3+ items, check if at least one is a known skill
        known_count = sum(1 for item in items if item.lower().strip() in self.KNOWN_SKILLS)
        
        # Also check for common patterns (short, no spaces)
        tech_pattern_count = sum(1 for item in items 
                                  if len(item.strip()) <= 20 and ' ' not in item.strip())
        
        # At least one known skill OR most items look like tech names
        return known_count >= 1 or tech_pattern_count >= len(items) * 0.5
    
    def _extract_tech_from_text(self, text: str) -> List[str]:
        """Extract known technologies from a line of text."""
        found_tech = []
        text_lower = text.lower()
        
        # Scan for known skills in the text
        for skill in self.KNOWN_SKILLS:
            skill_lower = skill.lower()
            # Skip ambiguous single-letter skills in general text
            if skill_lower in self.AMBIGUOUS_SKILLS:
                continue
            
            # Use word boundary matching
            pattern = r'\b' + re.escape(skill_lower) + r'\b'
            if re.search(pattern, text_lower):
                # Normalize the skill name
                formatted = skill.title() if len(skill) > 3 else skill.upper()
                found_tech.append(formatted)
        
        return found_tech
    
    def _extract_tech_from_descriptions(self, project: Dict) -> None:
        """Deduplicate and clean up tech stack in a project."""
        if not project.get('tech_stack'):
            return
        
        # Normalize and deduplicate
        seen = set()
        unique_tech = []
        
        for tech in project['tech_stack']:
            tech_normalized = tech.strip().lower()
            if tech_normalized and tech_normalized not in seen:
                seen.add(tech_normalized)
                # Preserve the original casing or format nicely
                formatted = tech.strip()
                if formatted.lower() in self.KNOWN_SKILLS:
                    formatted = formatted.title() if len(formatted) > 3 else formatted.upper()
                unique_tech.append(formatted)
        
        project['tech_stack'] = unique_tech

    # ============================================================
    # RULE 6: SKILLS EXTRACTION with Contextual Density
    # ============================================================
    def extract_skills(self, text: str) -> List[ExtractedField]:
        """
        Extract skills using:
        - Block First Rule: Prioritize Skills Zone
        - Ambiguity Guard: Handle short skills carefully
        """
        sections = self.sectionize(text)
        skills_zone = sections.get('skills', '')
        
        found_skills = []
        found_skill_names = set()  # Track to avoid duplicates
        
        # Priority 1: Search in Skills Zone (90% confidence)
        if skills_zone:
            zone_skills = self._extract_skills_from_text(skills_zone, is_skills_zone=True)
            for skill in zone_skills:
                if skill.value.lower() not in found_skill_names:
                    found_skill_names.add(skill.value.lower())
                    found_skills.append(skill)
        
        # Priority 2: Search whole text if skills zone is sparse (70% confidence)
        if len(found_skills) < 3:
            all_skills = self._extract_skills_from_text(text, is_skills_zone=False)
            for skill in all_skills:
                if skill.value.lower() not in found_skill_names:
                    found_skill_names.add(skill.value.lower())
                    found_skills.append(skill)
        
        return found_skills
    
    def _extract_skills_from_text(self, text: str, is_skills_zone: bool) -> List[ExtractedField]:
        """Extract skills from given text with confidence based on zone."""
        skills = []
        text_lower = text.lower()
        confidence = 90 if is_skills_zone else 70
        
        for skill in self.KNOWN_SKILLS:
            skill_lower = skill.lower()
            
            # Ambiguity Guard for short/ambiguous skills (C, R, Go, Vue, etc.)
            if skill_lower in self.AMBIGUOUS_SKILLS:
                # For ambiguous skills, require comma-separation to avoid false positives
                # Pattern: skill must be preceded by start/comma and followed by comma/end
                comma_pattern = rf'(?:^|,\s*){re.escape(skill_lower)}(?:\s*,|\s*$)'
                
                # Must ACTUALLY match the comma pattern in the text
                if re.search(comma_pattern, text_lower):
                    skills.append(ExtractedField(
                        value=skill.upper(),  # Short skills like C, R should be uppercase
                        confidence=confidence - 5  # Slightly lower for ambiguous
                    ))
            else:
                # Normal skill matching with word boundaries
                pattern = r'\b' + re.escape(skill_lower) + r'\b'
                if re.search(pattern, text_lower):
                    skills.append(ExtractedField(
                        value=skill.title() if len(skill) > 3 else skill.upper(),
                        confidence=confidence
                    ))
        
        return skills

    # ============================================================
    # RULE 7: LOCATION EXTRACTION with City + Pincode
    # ============================================================
    def extract_location(self, text: str) -> ExtractedField:
        """
        Extract location using:
        - Pincode Heuristic: 6-digit Indian pincode
        - City Matching
        - State Fallback
        """
        text_lower = text.lower()
        
        # Try Pincode first
        pincode_matches = self.PINCODE_REGEX.findall(text)
        for pincode in pincode_matches:
            # Map pincode prefix to city
            prefix = pincode[:3]
            if prefix in self.PINCODE_CITY_MAP:
                city = self.PINCODE_CITY_MAP[prefix]
                return ExtractedField(
                    value=f"{city} ({pincode})",
                    confidence=90
                )
        
        # Try City matching
        for city in self.INDIAN_CITIES:
            if city in text_lower:
                return ExtractedField(
                    value=city.title(),
                    confidence=85
                )
        
        # Fallback: State matching
        for state in self.INDIAN_STATES:
            if state in text_lower:
                return ExtractedField(
                    value=state.title(),
                    confidence=70
                )
        
        return ExtractedField(value="", confidence=0)

    # ============================================================
    # OVERALL CONFIDENCE CALCULATION
    # ============================================================
    def calculate_overall_confidence(self, parsed: Dict) -> int:
        """Calculate weighted overall confidence score."""
        weights = {
            'email': 0.20,
            'phone': 0.15,
            'full_name': 0.20,
            'skills': 0.30,
            'experience': 0.10,
            'education': 0.05
        }
        
        total = 0
        total += parsed['email'].confidence * weights['email']
        total += parsed['phone'].confidence * weights['phone']
        total += parsed['full_name'].confidence * weights['full_name']
        total += parsed['years_of_experience'].confidence * weights['experience']
        
        # Skills confidence is average of all found skills
        if parsed['skills']:
            avg_skill_conf = sum(s.confidence for s in parsed['skills']) / len(parsed['skills'])
            total += avg_skill_conf * weights['skills']
        
        # Education confidence
        if parsed.get('education'):
            avg_edu_conf = sum(e.get('confidence', 50) for e in parsed['education']) / len(parsed['education'])
            total += avg_edu_conf * weights['education']
        
        return min(100, int(total))

    # ============================================================
    # FILE EXTRACTION UTILITIES
    # ============================================================
    @staticmethod
    def extract_text_from_pdf(content: bytes) -> str:
        """Extract text from PDF using pdfplumber."""
        try:
            import pdfplumber
            with pdfplumber.open(io.BytesIO(content)) as pdf:
                text_parts = []
                for page in pdf.pages:
                    page_text = page.extract_text()
                    if page_text:
                        text_parts.append(page_text)
                return '\n'.join(text_parts)
        except ImportError:
            return "[PDF parsing library not available]"
        except Exception as e:
            return f"[PDF parsing error: {str(e)}]"
    
    @staticmethod
    def extract_text_from_docx(content: bytes) -> str:
        """Extract text from DOCX using python-docx."""
        try:
            from docx import Document
            doc = Document(io.BytesIO(content))
            paragraphs = [p.text for p in doc.paragraphs if p.text.strip()]
            return '\n'.join(paragraphs)
        except ImportError:
            return "[DOCX parsing library not available]"
        except Exception as e:
            return f"[DOCX parsing error: {str(e)}]"
