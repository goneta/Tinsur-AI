/**
 * TypeScript types for Policy Type.
 */

export interface PolicyType {
    id: string;
    company_id: string;
    name: string;
    code: string;
    description?: string;
    is_active: boolean;
    created_at: string;
    updated_at: string;
}

export interface PolicyTypeCreateRequest {
    name: string;
    code: string;
    description?: string;
    is_active?: boolean;
}

export interface PolicyTypeUpdateRequest {
    name?: string;
    code?: string;
    description?: string;
    is_active?: boolean;
}
