import { api } from './api';

export interface PremiumPolicyCriteria {
    id: string;
    company_id: string;
    name: string;
    description?: string;
    field_name: string;
    operator: string;
    value: string;
    created_at: string;
    updated_at: string;
}

import { PolicyService } from './policy-service-api';

export interface PremiumPolicyType {
    id: string;
    company_id: string;
    name: string;
    description?: string;
    price: number;
    excess: number;
    tagline?: string;
    is_featured?: boolean;
    code?: string;
    is_active: boolean;
    criteria: PremiumPolicyCriteria[];
    services: PolicyService[];
    created_at: string;
    updated_at: string;
}

export interface PremiumPolicyTypeCreate {
    name: string;
    description?: string;
    price: number;
    excess?: number;
    is_active?: boolean;
    criteria_ids: string[];
    service_ids?: string[];
}

export const premiumPolicyApi = {
    // Criteria
    getCriteria: async () => {
        const response = await api.get<PremiumPolicyCriteria[]>('/premium-policies/criteria');
        return response.data;
    },
    createCriteria: async (data: Partial<PremiumPolicyCriteria>) => {
        const response = await api.post<PremiumPolicyCriteria>('/premium-policies/criteria', data);
        return response.data;
    },
    updateCriteria: async (id: string, data: Partial<PremiumPolicyCriteria>) => {
        const response = await api.put<PremiumPolicyCriteria>(`/premium-policies/criteria/${id}`, data);
        return response.data;
    },
    deleteCriteria: async (id: string) => {
        await api.delete(`/premium-policies/criteria/${id}`);
    },

    // Policy Types
    getPolicyTypes: async (page = 1, pageSize = 50) => {
        const response = await api.get<{ premium_policy_types: PremiumPolicyType[], total: number }>(
            `/premium-policies/types?page=${page}&page_size=${pageSize}`
        );
        return response.data;
    },
    getPolicyType: async (id: string) => {
        const response = await api.get<PremiumPolicyType>(`/premium-policies/types/${id}`);
        return response.data;
    },
    createPolicyType: async (data: PremiumPolicyTypeCreate) => {
        const response = await api.post<PremiumPolicyType>('/premium-policies/types', data);
        return response.data;
    },
    updatePolicyType: async (id: string, data: Partial<PremiumPolicyTypeCreate>) => {
        const response = await api.put<PremiumPolicyType>(`/premium-policies/types/${id}`, data);
        return response.data;
    },
    deletePolicyType: async (id: string) => {
        await api.delete(`/premium-policies/types/${id}`);
    }
};
