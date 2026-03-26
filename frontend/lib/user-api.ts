
import { api } from '@/lib/api';
import { User, UserCreate, UserUpdate } from '@/types/user';

export type UserListResponse = User[];

export const userApi = {
    list: async (search?: string, role?: string) => {
        const params = new URLSearchParams();
        if (search) params.append('search', search);
        if (role) params.append('role', role);

        const response = await api.get<UserListResponse>(`/users?${params.toString()}`);
        return response.data;
    },

    create: async (data: any) => {
        const response = await api.post<User>('/users', data);
        return response.data;
    },

    update: async (id: string, data: any) => {
        const response = await api.put<User>(`/users/${id}`, data);
        return response.data;
    },

    delete: async (id: string) => {
        const response = await api.delete(`/users/${id}`);
        return response.data;
    }
};
