/**
 * API Type Definitions
 * TypeScript interfaces matching backend Pydantic schemas
 */

// ============================================================
// Resume Types
// ============================================================

export interface ExtractedField {
  value: string | number | null;
  confidence: number;
}

export interface EducationEntry {
  degree?: string;
  field?: string;
  institute?: string;
  year?: string;
  cgpa?: number;
  confidence: number;
}

export interface WorkExperienceEntry {
  title: string;
  company: string;
  duration: string;
  description: string[];
}

export interface ProjectEntry {
  title: string;
  tech_stack: string[];
  description: string[];
  confidence: number;
}

export interface ParsedResumeAPI {
  id?: number;
  full_name: ExtractedField;
  email: ExtractedField;
  phone: ExtractedField;
  years_of_experience: ExtractedField;
  skills: ExtractedField[];
  education: EducationEntry[];
  work_experience: WorkExperienceEntry[];
  projects: ProjectEntry[];
  preferred_locations: string[];
  preferred_roles: string[];
  expected_salary: number | null;
  overall_confidence: number;
  raw_text: string;
}

// ============================================================
// Matching Types
// ============================================================

export interface MatchRequest {
  full_name?: string;
  skills: string[];
  experience_years: number;
  preferred_locations?: string[];
  preferred_roles?: string[];
  expected_salary?: number;
  education?: {
    degree: string;
    field: string;
    cgpa: number;
  };
}

export interface ScoreBreakdown {
  skill_match: number;
  location_match: number;
  salary_match: number;
  experience_match: number;
  role_match: number;
}

export interface JobMatchAPI {
  job_id: number;
  job_title: string;
  match_score: number;
  match_tier: string;
  breakdown: ScoreBreakdown;
  missing_skills: string[];
  explanation: string;
  top_reason_for_match: string;
  top_area_to_improve: string;
}

export interface MatchResponseAPI {
  candidate: string;
  field: string;
  matches: JobMatchAPI[];
}

// ============================================================
// Roadmap Types
// ============================================================

export interface LearningResource {
  title: string;
  type: string;
  url?: string;
  provider: string;
  estimated_hours: number;
  is_free: boolean;
}

export interface SkillNode {
  name: string;
  category: string;
  difficulty: number;
  estimated_weeks: number;
  prerequisites: string[];
  resources: LearningResource[];
  why_needed: string;
}

export interface LearningPhase {
  phase_number: number;
  title: string;
  description: string;
  skills: SkillNode[];
  total_weeks: number;
  milestone: string;
}

export interface RoadmapRequest {
  current_skills: string[];
  target_job_id: number;
  learning_pace: "intensive" | "moderate" | "relaxed";
}

export interface RoadmapResponse {
  target_job: string;
  target_company: string;
  current_match_score: number;
  projected_match_score: number;
  missing_skills_count: number;
  phases: LearningPhase[];
  total_estimated_weeks: number;
  total_estimated_hours: number;
  summary: string;
  motivation_message: string;
}

// ============================================================
// Job Types
// ============================================================

export interface JobAPI {
  id: number;
  title: string;
  company: string;
  description: string;
  location: string;
  is_remote: boolean;
  salary_min: number;
  salary_max: number;
  min_experience_years: number;
  max_experience_years?: number;
  required_skills: string[];
  nice_to_have_skills: string[];
}

export interface JobsResponse {
  jobs: JobAPI[];
}
