import { api } from '@/lib/api';

export interface Translation {
    id: number;
    key: string;
    language_code: string;
    value: string;
    group?: string;
    is_active: boolean;
}

export interface TranslationCreate {
    key: string;
    language_code: string;
    value: string;
    group?: string;
}

export interface TranslationUpdate {
    value?: string;
    is_active?: boolean;
}

export const translationApi = {
    getAll: async (lang?: string) => {
        const params = lang ? { lang } : {};
        const response = await api.get<Translation[]>('/translations/list', { params });
        return response.data;
    },

    getMap: async (lang: string) => {
        const response = await api.get<Record<string, Record<string, string>>>(`/translations`, { params: { language_code: lang } });
        // Backend returns { "en": { ... } }, we need just { ... }
        return response.data[lang] || {};
    },

    create: async (data: TranslationCreate) => {
        const response = await api.post<Translation>('/translations/', data);
        return response.data;
    },

    update: async (id: number, data: TranslationUpdate) => {
        const response = await api.put<Translation>(`/translations/${id}`, data);
        return response.data;
    }
};
