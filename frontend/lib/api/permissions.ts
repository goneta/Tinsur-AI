import api from '@/lib/api';

export interface Permission {
    id: string;
    scope: string;
    action: string;
    description: string;
    key: string;
}

export interface Role {
    id: string;
    name: string;
    description: string;
    permissions: Permission[];
}

export const permissionApi = {
    getRoles: async (): Promise<Role[]> => {
        const response = await api.get('/admin/roles');
        return response.data;
    },

    getPermissions: async (): Promise<Permission[]> => {
        const response = await api.get('/admin/permissions');
        return response.data;
    },

    assignPermissions: async (roleId: string, permissionIds: string[]) => {
        const response = await api.post(`/admin/roles/${roleId}/permissions`, {
            permission_ids: permissionIds,
        });
        return response.data;
    },

    createPermission: async (data: { scope: string, action: string, description?: string }) => {
        const response = await api.post('/admin/permissions', data);
        return response.data;
    }
};
