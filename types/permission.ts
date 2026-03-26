export interface Permission {
    id: string;
    scope: string;
    action: string;
    description: string;
}

export interface Role {
    id: string;
    name: string;
    description: string;
    permissions: Permission[];
}

export interface RoleCreate {
    name: string;
    description?: string;
    permissions?: string[]; // IDs
}

export interface RoleUpdate {
    description?: string;
    permissions?: string[]; // IDs
}
