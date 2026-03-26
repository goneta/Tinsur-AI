import axios from "axios";
import { QuoteElement, QuoteElementCategory } from "@/types/quote-element";
export type { QuoteElement, QuoteElementCategory } from "@/types/quote-element";

const getAuthHeader = () => {
    const token = typeof window !== 'undefined' ? localStorage.getItem('access_token') : null;
    return token ? { Authorization: `Bearer ${token}` } : {};
};

const API_URL = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000/api/v1";

export const quoteElementApi = {
    list: async (params?: { category?: QuoteElementCategory; active_only?: boolean }): Promise<QuoteElement[]> => {
        const searchParams = new URLSearchParams();
        if (params?.category) searchParams.append("category", params.category);
        if (params?.active_only) searchParams.append("active_only", "true");

        const response = await axios.get(`${API_URL}/quote-elements/`, {
            headers: getAuthHeader(),
            params: searchParams
        });
        return response.data;
    },

    create: async (data: Partial<QuoteElement>): Promise<QuoteElement> => {
        const response = await axios.post(`${API_URL}/quote-elements/`, data, {
            headers: getAuthHeader(),
        });
        return response.data;
    },

    update: async (id: string, data: Partial<QuoteElement>): Promise<QuoteElement> => {
        const response = await axios.put(`${API_URL}/quote-elements/${id}`, data, {
            headers: getAuthHeader(),
        });
        return response.data;
    },

    delete: async (id: string): Promise<void> => {
        await axios.delete(`${API_URL}/quote-elements/${id}`, {
            headers: getAuthHeader(),
        });
    }
};
