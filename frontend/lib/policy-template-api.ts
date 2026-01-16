/**
 * API functions for Policy Templates.
 */
import api from '@/lib/api';
import {
    PolicyTemplate,
    PolicyTemplateCreateRequest,
    PolicyTemplateUpdateRequest
} from '@/types/policy-template';

export const policyTemplateApi = {
    // Get all policy templates
    getPolicyTemplates: async (params?: {
        skip?: number;
        limit?: number;
        policy_type_id?: string;
        search?: string;
        is_active?: boolean;
    }) => {
        const response = await api.get<PolicyTemplate[]>('/policy-templates/', { params });
        return response.data;
    },

    // Get single policy template
    getPolicyTemplate: async (id: string) => {
        const response = await api.get<PolicyTemplate>(`/policy-templates/${id}`);
        return response.data;
    },

    // Create policy template
    createPolicyTemplate: async (data: PolicyTemplateCreateRequest) => {
        const response = await api.post<PolicyTemplate>('/policy-templates/', data);
        return response.data;
    },

    // Update policy template
    updatePolicyTemplate: async (id: string, data: PolicyTemplateUpdateRequest) => {
        const response = await api.put<PolicyTemplate>(`/policy-templates/${id}`, data);
        return response.data;
    },

    // Delete policy template
    deletePolicyTemplate: async (id: string) => {
        await api.delete(`/policy-templates/${id}`);
    },

    // Duplicate template
    duplicatePolicyTemplate: async (id: string) => {
        const response = await api.post<PolicyTemplate>(`/policy-templates/${id}/duplicate`);
        return response.data;
    }
};
