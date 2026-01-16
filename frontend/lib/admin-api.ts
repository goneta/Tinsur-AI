import api from './api';

export interface DashboardStats {
    clients: {
        total: number;
        active: number;
        inactive: number;
        by_risk_profile: Record<string, number>;
        growth: number;
    };
    users: {
        total: number;
        agents: number;
    };
    policies: {
        active: number;
        growth: number;
    };
    quotes: {
        pending: number;
        growth: number;
    };
    revenue: {
        monthly: number;
        growth: number;
    };
}

export interface RecentActivity {
    activities: {
        type: string;
        title: string;
        description: string;
        amount: string | null;
        created_at: string;
    }[];
}

export const adminApi = {
    getStats: async (): Promise<DashboardStats> => {
        const response = await api.get('/admin/stats');
        return response.data;
    },
    getRecentActivity: async (): Promise<RecentActivity> => {
        const response = await api.get('/admin/recent-activity');
        return response.data;
    },
};
