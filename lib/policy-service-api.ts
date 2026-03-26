import { api } from './api';

export interface PolicyService {
    id: string;
    company_id: string;
    name_en: string;
    name_fr?: string;
    description?: string;
    default_price: number;
    category?: string;
    icon_name?: string;
    is_active: boolean;
}

export interface PolicyServiceCreate {
    company_id: string;
    name_en: string;
    name_fr?: string;
    description?: string;
    default_price: number;
    is_active: boolean;
}

export interface PolicyServiceUpdate {
    name_en?: string;
    name_fr?: string;
    description?: string;
    default_price?: number;
    is_active?: boolean;
}

export const policyServiceApi = {
    getAll: async (params?: { company_id: string, search?: string, is_active?: boolean }) => {
        const response = await api.get<PolicyService[]>('/policy-services/', { params });
        return response.data;
    },

    create: async (data: PolicyServiceCreate) => {
        const response = await api.post<PolicyService>('/policy-services/', data);
        return response.data;
    },

    update: async (id: string, data: PolicyServiceUpdate) => {
        const response = await api.put<PolicyService>(`/policy-services/${id}`, data);
        return response.data;
    },

    delete: async (id: string) => {
        const response = await api.delete<PolicyService>(`/policy-services/${id}`);
        return response.data;
    }
};
