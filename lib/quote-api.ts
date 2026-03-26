/**
 * API functions for Quotes.
 */
import api from '@/lib/api';
import {
    Quote,
    QuoteCreateRequest,
    QuoteUpdateRequest
} from '@/types/quote';

export const quoteApi = {
    // Get all quotes
    getQuotes: async (params?: {
        skip?: number;
        limit?: number;
        client_id?: string;
        policy_type_id?: string;
        status?: string;
    }) => {
        // Backend returns: { quotes: Quote[], total: number, page: number, page_size: number }
        const response = await api.get<{ quotes: Quote[]; total: number }>('/quotes/', { params });
        return response.data;
    },

    // Get single quote
    getQuote: async (id: string) => {
        const response = await api.get<Quote>(`/quotes/${id}`);
        return response.data;
    },

    // Create quote
    createQuote: async (data: QuoteCreateRequest) => {
        const response = await api.post<Quote>('/quotes/', data);
        return response.data;
    },

    // Update quote
    updateQuote: async (id: string, data: QuoteUpdateRequest) => {
        const response = await api.put<Quote>(`/quotes/${id}`, data);
        return response.data;
    },

    // Convert quote to policy
    convertQuoteToPolicy: async (id: string) => {
        const response = await api.post<any>(`/quotes/${id}/convert`);
        return response.data;
    },

    // Approve quote (Admin or Client self-service)
    approveQuote: async (id: string) => {
        const response = await api.post<any>(`/quotes/${id}/approve`);
        return response.data;
    },

    // Calculate premium (simulation)
    calculatePremium: async (data: any) => {
        const response = await api.post<any>('/quotes/calculate-premium', data);
        return response.data;
    },

    // Delete quote
    deleteQuote: async (id: string) => {
        await api.delete(`/quotes/${id}`);
    }
};
