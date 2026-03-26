import api from '@/lib/api';

export interface Ticket {
    id: string;
    ticket_number: string;
    subject: string;
    description: string;
    status: 'open' | 'in_progress' | 'resolved' | 'closed';
    priority: 'low' | 'medium' | 'high' | 'urgent';
    created_at: string;
    client_id: string;
}

export interface CreateTicketData {
    subject: string;
    description: string;
    priority: 'low' | 'medium' | 'high' | 'urgent';
}

export const ticketService = {
    async getTickets() {
        const response = await api.get<Ticket[]>('/tickets/');
        return response.data;
    },

    async getTicket(id: string) {
        const response = await api.get<Ticket>(`/tickets/${id}`);
        return response.data;
    },

    async createTicket(data: CreateTicketData) {
        const response = await api.post<Ticket>('/tickets/', data);
        return response.data;
    },

    async updateTicket(id: string, data: Partial<CreateTicketData> & { status?: string }) {
        const response = await api.put<Ticket>(`/tickets/${id}`, data);
        return response.data;
    }
};
