import api from '@/lib/api';

export interface TelematicsData {
    id: string;
    policy_id: string;
    device_id: string;
    trip_date: string;
    distance_km: number;
    avg_speed: number;
    max_speed: number;
    safety_score: number;
}

export interface MLModel {
    id: string;
    model_name: string;
    version: string;
    accuracy: number;
    is_active: boolean;
    last_trained: string;
}

export const analyticsService = {
    // Telematics
    async getTelematicsData(policyId: string) {
        const response = await api.get<TelematicsData[]>(`/telematics/history/${policyId}`);
        return response.data;
    },

    async getSafetyScore(policyId: string) {
        const response = await api.get<{
            policy_id: string;
            safety_score: number;
            ubi_adjustment_percent: number;
            rating: string;
        }>(`/telematics/score/${policyId}`);
        return response.data;
    },

    async uploadTelematicsData(policyId: string, data: any) {
        const response = await api.post<TelematicsData>(`/telematics/trip/${policyId}`, data);
        return response.data;
    },

    // ML Models
    async getMLModels() {
        const response = await api.get<MLModel[]>('/ml-models/');
        return response.data;
    }
};
