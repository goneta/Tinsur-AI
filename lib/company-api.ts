
import api from '@/lib/api';

export interface Company {
    id: string;
    name: string;
    email?: string;
    apr_percent?: number;
    arrangement_fee?: number;
    extra_fee?: number;
}

export const companyApi = {
    getCompanies: async (search?: string) => {
        const response = await api.get<Company[]>('/companies/', {
            params: { search }
        });
        return response.data;
    },

    getCurrentCompany: async () => {
        const response = await api.get<Company>('/companies/me');
        return response.data;
    },

    updateCompany: async (data: Partial<Company>) => {
        const response = await api.put<Company>('/companies/me', data);
        return response.data;
    }
};
