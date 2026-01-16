import { api } from '@/lib/api';
import { Permission, Role, RoleCreate, RoleUpdate } from '@/types/permission';

export const permissionApi = {
    getPermissions: async () => {
        const response = await api.get<Permission[]>('/permissions/permissions');
        return response.data;
    },
    getRoles: async () => {
        const response = await api.get<Role[]>('/permissions/roles');
        return response.data;
    },
    createRole: async (data: RoleCreate) => {
        const response = await api.post<Role>('/permissions/roles', data);
        return response.data;
    },
    updateRole: async (id: string, data: RoleUpdate) => {
        const response = await api.put<Role>(`/permissions/roles/${id}`, data);
        return response.data;
    }
};

export type { Role, Permission };
