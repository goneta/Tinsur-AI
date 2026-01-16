import api from './api';

export type AiPlan = 'BASIC' | 'BYOK' | 'CREDIT';

export interface SubscriptionStatus {
    plan: AiPlan;
    credits: number;
    has_custom_key: boolean;
    company_id: string;
}

export interface UsageStat {
    date: string;
    credits: number;
    count: number;
}

export interface TopupResponse {
    payment_id: string;
    status: string;
    gateway_response: any;
}

export const subscriptionApi = {
    getStatus: async () => {
        const response = await api.get<SubscriptionStatus>('/subscription/status');
        return response.data;
    },

    updatePlan: async (plan: AiPlan) => {
        const response = await api.post('/subscription/plan', { ai_plan: plan });
        return response.data;
    },

    updateCompanyKey: async (apiKey: string) => {
        const response = await api.post('/subscription/keys', { api_key: apiKey });
        return response.data;
    },

    updateSystemKey: async (provider: string, apiKey: string) => {
        const response = await api.post('/subscription/system/keys', {
            provider,
            api_key: apiKey
        });
        return response.data;
    },

    topupDev: async (companyId: string, amount: number) => {
        const response = await api.post('/dev/topup-dev', null, {
            params: {
                amount,
                company_id: companyId
            }
        });
        return response.data;
    },

    getUsageStats: async () => {
        const response = await api.get<UsageStat[]>('/subscription/usage/stats');
        return response.data;
    },

    initiateTopup: async (data: {
        amount: number,
        payment_method: string,
        payment_gateway?: string,
        phone_number?: string,
        success_url?: string,
        cancel_url?: string
    }) => {
        const response = await api.post<TopupResponse>('/subscription/topup', data);
        return response.data;
    }
};
