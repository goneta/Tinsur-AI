import { api } from '@/lib/api';
import { QuoteElement, QuoteElementCategory } from "@/types/quote-element";
export type { QuoteElement, QuoteElementCategory } from "@/types/quote-element";

export const quoteElementApi = {
    list: async (params?: { category?: QuoteElementCategory; active_only?: boolean }): Promise<QuoteElement[]> => {
        const searchParams: Record<string, string> = {};
        if (params?.category) searchParams.category = params.category;
        if (params?.active_only) searchParams.active_only = "true";

        const response = await api.get('/quote-elements/', { params: searchParams });
        return response.data;
    },

    create: async (data: Partial<QuoteElement>): Promise<QuoteElement> => {
        const response = await api.post('/quote-elements/', data);
        return response.data;
    },

    update: async (id: string, data: Partial<QuoteElement>): Promise<QuoteElement> => {
        const response = await api.put(`/quote-elements/${id}`, data);
        return response.data;
    },

    delete: async (id: string): Promise<void> => {
        await api.delete(`/quote-elements/${id}`);
    }
};
