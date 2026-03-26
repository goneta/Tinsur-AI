/**
 * TypeScript types for User.
 */

export interface User {
    id: string;
    company_id: string;
    email: string;
    first_name: string;
    last_name: string;
    phone?: string;
    role: 'super_admin' | 'company_admin' | 'manager' | 'agent' | 'client';
    is_active: boolean;
    is_verified: boolean;
    mfa_enabled: boolean;
    last_login?: string;
    created_at: string;
    updated_at: string;
    company_logo_url?: string;
    primary_color?: string;
    secondary_color?: string;
    pos_location_id?: string;
}

export interface LoginRequest {
    email: string;
    password: string;
}

export interface LoginResponse {
    access_token: string;
    refresh_token: string;
    token_type: string;
    user: User;
}

export interface RegisterRequest {
    email: string;
    password: string;
    first_name: string;
    last_name: string;
    phone?: string;
    company_name: string;
    company_subdomain: string;
}

export interface UserCreate {
    email: string;
    password: string;
    first_name: string;
    last_name: string;
    phone?: string;
    role: User['role'];
    is_active?: boolean;
    pos_location_id?: string;
}

export interface UserUpdate {
    email?: string;
    first_name?: string;
    last_name?: string;
    phone?: string;
    role?: User['role'];
    is_active?: boolean;
    password?: string;
    pos_location_id?: string;
}
