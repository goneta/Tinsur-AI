import api from './api';

export interface Referral {
    id: string;
    referral_code: string;
    status: 'pending' | 'converted' | 'expired' | 'rewarded';
    reward_amount: number;
    reward_paid: boolean;
    converted_at: string | null;
    created_at: string;
    // Relations if needed, but for listing mostly IDs or expanded?
    // Backend schemas model usually returns IDs unless configured otherwise.
}

export interface ReferralStats {
    total_rewards: number;
    pending_conversions: number;
    converted_count: number;
}

export const referralApi = {
    createReferral: async (data: { referrer_client_id: string }) => {
        const response = await api.post<Referral>('/referrals/', data);
        return response.data;
    },

    getReferrals: async (params?: { skip?: number; limit?: number }) => {
        const response = await api.get<Referral[]>('/referrals/', { params });
        return response.data;
    },

    getStats: async () => {
        const response = await api.get<ReferralStats>('/referrals/stats');
        return response.data;
    }
};
