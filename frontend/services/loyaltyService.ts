import api from '@/lib/api';

export interface LoyaltyPoint {
    id: string;
    client_id: string;
    points_balance: number;
    tier: 'bronze' | 'silver' | 'gold' | 'platinum';
    total_points_earned: number;
    last_updated: string;
}

export const loyaltyService = {
    async getLoyaltyPoints(clientId: string) {
        const response = await api.get<LoyaltyPoint>(`/loyalty/${clientId}`);
        return response.data;
    }
};
