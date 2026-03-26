import api from './api';

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
    company_id: string;
    client_id?: string;
    category: string;
    priority: string;
    status: string;
    subject: string;
    description?: string;
    assigned_to?: string;
    created_at: string;
    updated_at: string;
    resolved_at?: string;
    messages?: TicketMessage[];
}

export const ticketsApi = {
    getTickets: async (params?: { skip?: number; limit?: number }) => {
        const response = await api.get<Ticket[]>('/tickets/', { params });
        return response.data;
    },

    getTicket: async (id: string) => {
        const response = await api.get<Ticket>(`/tickets/${id}`);
        return response.data;
    },

    replyTicket: async (id: string, data: { message: string; is_internal: boolean }) => {
        const response = await api.post<TicketMessage>(`/tickets/${id}/reply`, data);
        return response.data;
    },

    updateTicket: async (id: string, data: { status?: string; priority?: string; assigned_to?: string }) => {
        const response = await api.patch<Ticket>(`/tickets/${id}`, data);
        return response.data;
    }
};
