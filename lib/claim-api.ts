/**
 * API client for claim operations.
 */
import { api } from './api';

export interface Claim {
    id: string;
    claim_number: string;
    policy_id: string;
    client_id: string;
    company_id: string;
    adjuster_id?: string;
    incident_date: string;
    incident_description: string;
    incident_location?: string;
    status: 'submitted' | 'under_review' | 'approved' | 'rejected' | 'paid' | 'closed';
    claim_amount: number;
    approved_amount?: number;
    evidence_files: string[];
    ai_assessment?: {
        severity: 'Low' | 'Medium' | 'High';
        damage_description: string;
        suggested_estimate: number;
        confidence_score: number;
        analyzed_at: string;
    };
    created_at: string;
    updated_at: string;
    fraud_score?: number;
    fraud_details?: {
        risk_factors: Array<{
            type: string;
            severity: 'Low' | 'Medium' | 'High';
            message: string;
        }>;
        last_analyzed?: string;
    };
}

export interface CreateClaimData {
    policy_id: string;
    incident_date: string;
    incident_description: string;
    incident_location?: string;
    claim_amount: number;
    evidence_files?: string[];
}

export interface UpdateClaimData {
    status?: string;
    approved_amount?: number;
    adjuster_id?: string;
    incident_description?: string;
    evidence_files?: string[];
    notes?: string;
}

export const claimApi = {
    /**
     * Get all claims with optional filters.
     */
    getClaims: async (params?: {
        skip?: number;
        limit?: number;
        status?: string;
        client_id?: string;
    }) => {
        const response = await api.get<Claim[]>('/claims', { params });
        return response.data;
    },

    /**
     * Get a specific claim by ID.
     */
    getClaim: async (id: string) => {
        const response = await api.get<Claim>(`/claims/${id}`);
        return response.data;
    },

    /**
     * Create a new claim.
     */
    createClaim: async (data: CreateClaimData) => {
        const response = await api.post<Claim>('/claims', data);
        return response.data;
    },

    /**
     * Update a claim.
     */
    updateClaim: async (id: string, data: UpdateClaimData) => {
        const response = await api.put<Claim>(`/claims/${id}`, data);
        return response.data;
    },

    /**
     * Analyze damage using AI (includes auto-fraud check).
     */
    analyzeClaimDamage: async (id: string) => {
        const response = await api.post<any>(`/claims/${id}/analyze`);
        return response.data;
    },

    /**
     * Manually trigger AI fraud review.
     */
    analyzeClaimFraud: async (id: string) => {
        const response = await api.post<any>(`/claims/${id}/analyze-fraud`);
        return response.data;
    },
};
