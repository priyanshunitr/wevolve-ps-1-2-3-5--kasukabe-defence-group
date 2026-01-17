/**
 * API Service Layer
 * Centralized API calls to FastAPI backend
 */

import axios, { AxiosError } from 'axios';
import {
    ParsedResumeAPI,
    MatchRequest,
    MatchBreakdown,
    RoadmapRequest,
    RoadmapResponse,
    JobsResponse,
} from '@/types/api';

// ============================================================
// Configuration
// ============================================================

const API_BASE_URL = process.env.NEXT_PUBLIC_API_BASE_URL || 'http://localhost:8000';

const api = axios.create({
    baseURL: API_BASE_URL,
    headers: {
        'Content-Type': 'application/json',
    },
});

// ============================================================
// Error Handling
// ============================================================

export class APIError extends Error {
    constructor(
        message: string,
        public statusCode?: number,
        public details?: unknown
    ) {
        super(message);
        this.name = 'APIError';
    }
}

function handleError(error: unknown): never {
    if (error instanceof AxiosError) {
        const message = error.response?.data?.detail || error.message;
        throw new APIError(message, error.response?.status, error.response?.data);
    }
    throw error;
}

// ============================================================
// Resume API
// ============================================================

export async function parseResume(file: File): Promise<ParsedResumeAPI> {
    try {
        const formData = new FormData();
        formData.append('file', file);

        const response = await api.post<ParsedResumeAPI>('/api/resume/parse', formData, {
            headers: {
                'Content-Type': 'multipart/form-data',
            },
        });
        return response.data;
    } catch (error) {
        handleError(error);
    }
}

export async function saveResume(
    candidateId: number,
    profile: ParsedResumeAPI
): Promise<{ message: string; candidate_id: number }> {
    try {
        const response = await api.post(`/api/resume/save/${candidateId}`, profile);
        return response.data;
    } catch (error) {
        handleError(error);
    }
}

// ============================================================
// Matching API
// ============================================================

export async function calculateMatches(request: MatchRequest): Promise<MatchBreakdown[]> {
    try {
        const response = await api.post<MatchBreakdown[]>('/api/match/calculate', request);
        return response.data;
    } catch (error) {
        handleError(error);
    }
}

export async function getMatchingWeights(): Promise<{
    weights: Record<string, { percentage: number; description: string }>;
    tiers: Record<string, number>;
}> {
    try {
        const response = await api.get('/api/match/weights');
        return response.data;
    } catch (error) {
        handleError(error);
    }
}

// ============================================================
// Roadmap API
// ============================================================

export async function generateRoadmap(request: RoadmapRequest): Promise<RoadmapResponse> {
    try {
        const response = await api.post<RoadmapResponse>('/api/roadmap/generate', request);
        return response.data;
    } catch (error) {
        handleError(error);
    }
}

export async function getAvailableSkills(): Promise<
    Record<string, { category: string; difficulty: number; prerequisites: string[]; estimated_weeks: number }>
> {
    try {
        const response = await api.get('/api/roadmap/skills');
        return response.data;
    } catch (error) {
        handleError(error);
    }
}

// ============================================================
// Jobs API
// ============================================================

export async function getJobs(): Promise<JobsResponse> {
    try {
        const response = await api.get<JobsResponse>('/api/jobs');
        return response.data;
    } catch (error) {
        handleError(error);
    }
}
