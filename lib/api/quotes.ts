import { api } from '@/lib/api';
import {
    Quote,
    QuoteCreate,
    QuoteUpdate,
    QuoteListResponse,
    QuoteCalculationRequest,
    QuoteCalculationResponse,
    PolicyType
} from '@/types/quote';

export const QuoteAPI = {
    // List quotes with filters
    list: async (params?: {
        client_id?: string;
        policy_type_id?: string;
        status?: string;
        page?: number;
        page_size?: number;
    }) => {
        const response = await api.get<QuoteListResponse>('/quotes', { params });
        return response.data;
    },

    // Get quote by ID
    get: async (id: string) => {
        const response = await api.get<Quote>(`/quotes/${id}`);
        return response.data;
    },

    // Calculate premium
    calculate: async (data: QuoteCalculationRequest) => {
        const response = await api.post<QuoteCalculationResponse>('/quotes/calculate', data);
        return response.data;
    },

    // Create new quote
    create: async (data: QuoteCreate) => {
        const response = await api.post<Quote>('/quotes', data);
        return response.data;
    },

    // Update quote
    update: async (id: string, data: QuoteUpdate) => {
        const response = await api.put<Quote>(`/quotes/${id}`, data);
        return response.data;
    },

    // Delete quote
    delete: async (id: string) => {
        await api.delete(`/quotes/${id}`);
    },

    send: async (id: string) => {
        const response = await api.post<Quote>(`/quotes/${id}/send`);
        return response.data;
    },

    matchPolicies: async (clientId?: string, data?: any) => {
        const payload = {
            client_id: clientId,
            ...(data || {})
        };
        const response = await api.post('/premium-policies/match', payload);
        return response.data;
    },

    // Archive quote
    archive: async (id: string) => {
        const response = await api.post<Quote>(`/quotes/${id}/archive`);
        return response.data;
    },

    // Approve quote
    approve: async (id: string) => {
        const response = await api.post<{
            message: string;
            quote_status: string;
            policy_id: string;
            policy_number: string;
        }>(`/quotes/${id}/approve`);
        return response.data;
    },

    // Reject quote
    reject: async (id: string) => {
        const response = await api.post<Quote>(`/quotes/${id}/reject`);
        return response.data;
    },

    // Convert to policy
    convertToPolicy: async (
        id: string,
        data: {
            start_date: string;
            payment_method: string;
            initial_payment_amount?: number;
        }
    ) => {
        const response = await api.post<{
            message: string;
            policy_id: string;
            policy_number: string;
        }>(`/quotes/${id}/convert`, data);
        return response.data;
    },

    // Helper: List Policy Types
    listPolicyTypes: async () => {
        const response = await api.get<{ policy_types: PolicyType[] }>('/policy-types');
        return response.data.policy_types;
    },

    // Create Policy Type
    createPolicyType: async (data: { name: string; code: string; description?: string }) => {
        const response = await api.post<PolicyType>('/policy-types', data);
        return response.data;
    }
};
