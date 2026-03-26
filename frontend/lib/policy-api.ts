/**
 * API functions for policy management.
 */
import api from '@/lib/api';
import {
    Policy,
    PolicyCreateRequest,
    PolicyUpdateRequest,
    PolicyRenewalRequest,
    PolicyCancellationRequest,
    EndorsementCreateRequest
} from '@/types/policy';

export const policyApi = {
    // Get all policies with filters
    getPolicies: async (params?: {
        skip?: number;
        limit?: number;
        client_id?: string;
        policy_type_id?: string;
        status?: string;
    }) => {
        // Backend returns: { policies: Policy[], total: number, page: number, page_size: number }
        const response = await api.get<{ policies: Policy[]; total: number }>('/policies/', { params });
        return response.data;
    },

    // Get expiring policies
    getExpiringPolicies: async (days: number = 30) => {
        const response = await api.get<Policy[]>('/policies/expiring', {
            params: { days }
        });
        return response.data;
    },

    // Get single policy
    getPolicy: async (id: string) => {
        const response = await api.get<Policy>(`/policies/${id}`);
        return response.data;
    },

    // Create policy
    createPolicy: async (data: PolicyCreateRequest) => {
        const response = await api.post<Policy>('/policies/', data);
        return response.data;
    },

    // Update policy
    updatePolicy: async (id: string, data: PolicyUpdateRequest) => {
        const response = await api.put<Policy>(`/policies/${id}`, data);
        return response.data;
    },

    // Renew policy
    renewPolicy: async (id: string, data: PolicyRenewalRequest) => {
        const response = await api.post<Policy>(`/policies/${id}/renew`, data);
        return response.data;
    },

    // Cancel policy
    cancelPolicy: async (id: string, data: PolicyCancellationRequest) => {
        const response = await api.post<Policy>(`/policies/${id}/cancel`, data);
        return response.data;
    },

    // Reinstate policy
    reinstatePolicy: async (id: string) => {
        const response = await api.post<Policy>(`/policies/${id}/reinstate`);
        return response.data;
    },

    // Get payment schedule
    getPolicySchedule: async (id: string) => {
        const response = await api.get<any>(`/policies/${id}/schedule`);
        return response.data;
    },

    // Delete policy (soft delete)
    deletePolicy: async (id: string) => {
        await api.delete(`/policies/${id}`);
    },

    createEndorsement: async (id: string, data: EndorsementCreateRequest) => {
        const response = await api.post<any>(`/policies/${id}/endorsements`, data);
        return response.data;
    },


    // Generate Payment Schedule Document
    generatePaymentSchedule: async (id: string) => {
        const response = await api.post<any>(`/policies/${id}/generate-schedule`);
        return response.data;
    },

    // Generate Policy Agreement Document
    generatePolicyAgreement: async (id: string) => {
        const response = await api.post<any>(`/policies/${id}/generate-agreement`);
        return response.data;
    },

    // Get generated policy documents
    getPolicyDocuments: async (id: string) => {
        const response = await api.get<string[]>(`/documents/policy/${id}`);
        return response.data;
    },
};
