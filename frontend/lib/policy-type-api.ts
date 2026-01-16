/**
 * API functions for Policy Types.
 */
import api from '@/lib/api';
import {
    PolicyType,
    PolicyTypeCreateRequest,
    PolicyTypeUpdateRequest
} from '@/types/policy-type';

export const policyTypeApi = {
    // Get all policy types
    getPolicyTypes: async (params?: {
        skip?: number;
        limit?: number;
        search?: string;
        is_active?: boolean;
    }) => {
        const response = await api.get<{ policy_types: PolicyType[], total: number }>('/policy-types/', { params });
        return response.data.policy_types;
    },

    // Get single policy type
    getPolicyType: async (id: string) => {
        const response = await api.get<PolicyType>(`/policy-types/${id}`);
        return response.data;
    },

    // Create policy type
    createPolicyType: async (data: PolicyTypeCreateRequest) => {
        const response = await api.post<PolicyType>('/policy-types/', data);
        return response.data;
    },

    // Update policy type
    updatePolicyType: async (id: string, data: PolicyTypeUpdateRequest) => {
        const response = await api.put<PolicyType>(`/policy-types/${id}`, data);
        return response.data;
    },

    // Delete policy type
    deletePolicyType: async (id: string) => {
        await api.delete(`/policy-types/${id}`);
    },
};
