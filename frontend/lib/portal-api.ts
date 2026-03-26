import api from './api';

// Types
// Reuse types from tickets-api or define here. Since portal is separate app logically, define here.
export interface TicketMessage {
    id: string;
    ticket_id: string;
    sender_id?: string;
    sender_type: 'user' | 'client';
    message: string;
    is_internal: boolean;
    created_at: string;
}

export interface Ticket {
    id: string;
    ticket_number: string;
    category: string;
    priority: string;
    status: string;
    subject: string;
    description?: string;
    created_at: string;
    updated_at: string;
    messages?: TicketMessage[];
}

export interface DashboardStats {
    active_policies: number;
    open_claims: number;
    next_payment: {
        amount: number;
        date: string | null;
        currency: string;
    };
    pending_actions: number;
    client_name: string;
    loyalty: {
        points: number;
        tier: string;
    };
    premium_tier?: string;
    policy_type_name?: string;
    insurance_company?: string;
    insurance_company_phone?: string;
    primary_policy?: {
        id: string;
        policy_number: string;
        renewal_date: string;
        start_date: string;
        vehicles: {
            make: string;
            model: string;
            registration: string;
            year?: number;
        }[];
        drivers: {
            name: string;
            type: string;
        }[];
        cover_type: string;
        usage: string;
        mileage: number;
        parked_overnight: string;
        postcode: string;
        ncd_years: number;
        ncd_protected: boolean;
        voluntary_excess: number;
        compulsory_excess: number;
        policy_type_name: string;
        services: {
            id: string;
            name_en: string;
            name_fr: string | null;
            price: number;
        }[];
    } | null;
    policies?: {
        id: string;
        policy_number: string;
        renewal_date: string;
        start_date: string;
        vehicles: {
            make: string;
            model: string;
            registration: string;
            year?: number;
        }[];
        drivers: {
            name: string;
            type: string;
        }[];
        cover_type: string;
        usage: string;
        mileage: number;
        parked_overnight: string;
        postcode: string;
        ncd_years: number;
        ncd_protected: boolean;
        voluntary_excess: number;
        compulsory_excess: number;
        policy_type_name: string;
        services: {
            id: string;
            name_en: string;
            name_fr: string | null;
            price: number;
        }[];
    }[];
}

export interface PortalPayment {
    id: string;
    policy_id: string;
    amount: number;
    currency: string;
    payment_number: string;
    payment_method: string;
    payment_gateway?: string;
    status: string;
    reference_number?: string;
    paid_at?: string;
    created_at: string;
    policy_number_display?: string;
    premium_frequency?: string;
}

export const portalApi = {
    getDashboardStats: async () => {
        const response = await api.get<DashboardStats>('/portal/dashboard-stats');
        return response.data;
    },

    getMyPolicies: async () => {
        const response = await api.get('/portal/policies');
        return response.data;
    },

    getMyPayments: async () => {
        const response = await api.get<PortalPayment[]>('/portal/payments');
        return response.data;
    },

    registerClient: async (data: any) => {
        const response = await api.post('/portal/register', data);
        return response.data;
    },

    createClaim: async (data: any) => {
        const response = await api.post('/portal/claims', data);
        return response.data;
    },

    processPayment: async (data: any) => {
        const response = await api.post('/portal/payments/process', data);
        return response.data;
    },

    // Quotes
    calculateQuote: async (data: any) => {
        const payload = {
            ...data,
            selected_services: data?.selected_services ?? []
        };
        const response = await api.post<any>('/portal/quotes/calculate', payload);
        return response.data;
    },

    createQuote: async (data: any) => {
        const payload = {
            ...data,
            selected_services: data?.selected_services ?? []
        };
        const response = await api.post<any>('/portal/quotes', payload);
        return response.data;
    },

    // Tickets
    createTicket: async (data: { subject: string; category: string; description: string; priority: string }) => {
        const response = await api.post('/portal/tickets', data);
        return response.data;
    },
    getTickets: async () => {
        const response = await api.get('/portal/tickets');
        return response.data;
    },
    getTicket: async (id: string) => {
        const response = await api.get(`/portal/tickets/${id}`);
        return response.data;
    },
    replyTicket: async (id: string, data: { message: string }) => {
        const response = await api.post(`/portal/tickets/${id}/reply`, data);
        return response.data;
    },

    getPolicyTypes: async () => {
        const response = await api.get('/policy-types/');
        return response.data;
    },

    // --- Referrals ---
    createReferral: async () => {
        const response = await api.post<Referral>('/portal/referrals');
        return response.data;
    },

    getReferrals: async (params?: { skip?: number; limit?: number }) => {
        const response = await api.get<Referral[]>('/portal/referrals', { params });
        return response.data;
    },

    getReferralStats: async () => {
        // We define a specific interface for the stats returned by this endpoint
        interface MyReferralStats {
            referral_code: string | null;
            total_earned: number;
            pending_count: number;
            converted_count: number;
            total_referrals: number;
        }
        const response = await api.get<MyReferralStats>('/portal/referrals/stats');
        return response.data;
    },

    // --- Account Settings ---
    getProfile: async () => {
        const response = await api.get('/portal/profile');
        return response.data;
    },

    updateProfile: async (data: any) => {
        const response = await api.put('/portal/profile', data);
        return response.data;
    },

    changePassword: async (data: any) => {
        const response = await api.post('/portal/security/password', data);
        return response.data;
    },

    toggle2FA: async (data: { enabled: boolean }) => {
        const response = await api.post('/portal/security/2fa', data);
        return response.data;
    },

    deleteAccount: async () => {
        const response = await api.delete('/portal/account');
        return response.data;
    }
};

// Re-export types
import { Referral } from './referral-api';
export type { Referral };
