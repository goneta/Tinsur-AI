
import api from './api';

export interface ApiKey {
    id: string;
    name: string;
    key_prefix: string;
    agent_id?: string;
    is_active: boolean;
    created_at: string;
    expires_at?: string;
    last_used_at?: string;
    plain_text_key?: string; // Only on creation
}

export interface ApiKeyCreate {
    name: string;
    agent_id?: string;
    expires_at?: string;
}

export const apiKeyApi = {
    getAll: async () => {
        const response = await api.get<ApiKey[]>('/api-keys/');
        return response.data;
    },

    create: async (data: ApiKeyCreate) => {
        const response = await api.post<ApiKey>('/api-keys/', data);
        return response.data;
    },

    revoke: async (id: string) => {
        await api.delete(`/api-keys/${id}`);
    },

    update: async (id: string, data: Partial<ApiKeyCreate> & { is_active?: boolean }) => {
        const response = await api.put<ApiKey>(`/api-keys/${id}`, data);
        return response.data;
    }
};
