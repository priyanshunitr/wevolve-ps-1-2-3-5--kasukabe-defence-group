import React, { createContext, useContext, useState, ReactNode } from 'react';
import { ParsedResumeAPI } from '@/types/api';

// Frontend-friendly resume format (used for display/editing)
export interface ParsedResumeFrontend {
  id?: number;
  name: string;
  email: string;
  phone: string;
  skills: { name: string; confidence: number }[];
  experience: {
    title: string;
    company: string;
    duration: string;
    description: string;
    confidence: number;
  }[];
  education: {
    degree: string;
    institution: string;
    year: string;
    confidence: number;
  }[];
  projects: {
    name: string;
    description: string;
    technologies: string[];
    confidence: number;
  }[];
  preferredLocations: string[];
  preferredRoles: string[];
  expectedSalary: number | null;
  nameConfidence: number;
  emailConfidence: number;
  phoneConfidence: number;
  yearsOfExperience: number;
}

// Transform API response to frontend format
export function transformApiToFrontend(api: ParsedResumeAPI): ParsedResumeFrontend {
  return {
    id: api.id,
    name: String(api.full_name.value || ''),
    email: String(api.email.value || ''),
    phone: String(api.phone.value || ''),
    skills: api.skills.map((s) => ({
      name: String(s.value || ''),
      confidence: s.confidence,
    })),
    experience: api.work_experience.map((w) => ({
      title: w.title,
      company: w.company,
      duration: w.duration,
      description: w.description.join('. '),
      confidence: 80, // Default confidence
    })),
    education: api.education.map((e) => ({
      degree: e.degree || '',
      institution: e.institute || '',
      year: e.year || '',
      confidence: e.confidence,
    })),
    projects: api.projects.map((p) => ({
      name: p.title,
      description: p.description.join('. '),
      technologies: p.tech_stack,
      confidence: p.confidence,
    })),
    preferredLocations: api.preferred_locations,
    preferredRoles: api.preferred_roles,
    expectedSalary: api.expected_salary,
    nameConfidence: api.full_name.confidence,
    emailConfidence: api.email.confidence,
    phoneConfidence: api.phone.confidence,
    yearsOfExperience: Number(api.years_of_experience.value) || 0,
  };
}

// Transform frontend format back to API format
export function transformFrontendToApi(frontend: ParsedResumeFrontend): ParsedResumeAPI {
  return {
    id: frontend.id,
    full_name: { value: frontend.name, confidence: frontend.nameConfidence },
    email: { value: frontend.email, confidence: frontend.emailConfidence },
    phone: { value: frontend.phone, confidence: frontend.phoneConfidence },
    years_of_experience: { value: frontend.yearsOfExperience, confidence: 80 },
    skills: frontend.skills.map((s) => ({ value: s.name, confidence: s.confidence })),
    education: frontend.education.map((e) => ({
      degree: e.degree,
      field: '',
      institute: e.institution,
      year: e.year,
      cgpa: undefined,
      confidence: e.confidence,
    })),
    work_experience: frontend.experience.map((w) => ({
      title: w.title,
      company: w.company,
      duration: w.duration,
      description: w.description ? [w.description] : [],
    })),
    projects: frontend.projects.map((p) => ({
      title: p.name,
      tech_stack: p.technologies,
      description: p.description ? [p.description] : [],
      confidence: p.confidence,
    })),
    preferred_locations: frontend.preferredLocations,
    preferred_roles: frontend.preferredRoles,
    expected_salary: frontend.expectedSalary,
    overall_confidence: Math.round(
      (frontend.nameConfidence + frontend.emailConfidence + frontend.phoneConfidence) / 3
    ),
    raw_text: '',
  };
}

interface ResumeContextType {
  resumeFile: File | null;
  setResumeFile: (file: File | null) => void;
  parsedResume: ParsedResumeFrontend | null;
  setParsedResume: (resume: ParsedResumeFrontend | null) => void;
  candidateId: number | null;
  setCandidateId: (id: number | null) => void;
  isVerified: boolean;
  setIsVerified: (verified: boolean) => void;
  isLoading: boolean;
  setIsLoading: (loading: boolean) => void;
  error: string | null;
  setError: (error: string | null) => void;
}

const ResumeContext = createContext<ResumeContextType | undefined>(undefined);

export const ResumeProvider: React.FC<{ children: ReactNode }> = ({ children }) => {
  const [resumeFile, setResumeFile] = useState<File | null>(null);
  const [parsedResume, setParsedResume] = useState<ParsedResumeFrontend | null>(null);
  const [candidateId, setCandidateId] = useState<number | null>(null);
  const [isVerified, setIsVerified] = useState(false);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  return (
    <ResumeContext.Provider
      value={{
        resumeFile,
        setResumeFile,
        parsedResume,
        setParsedResume,
        candidateId,
        setCandidateId,
        isVerified,
        setIsVerified,
        isLoading,
        setIsLoading,
        error,
        setError,
      }}
    >
      {children}
    </ResumeContext.Provider>
  );
};

export const useResume = () => {
  const context = useContext(ResumeContext);
  if (!context) {
    throw new Error('useResume must be used within a ResumeProvider');
  }
  return context;
};
