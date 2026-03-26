/**
 * TypeScript types for Policy Template.
 */

export interface PolicyTemplate {
    id: string;
    company_id: string;
    policy_type_id: string;

    // Identification
    name: string;
    code: string;
    description?: string;

    // Content & Configuration
    template_content: any; // JSONB
    field_definitions: any[]; // JSONB

    // Versioning
    version: number;
    is_active: boolean;
    language: string;

    // Legal
    terms_and_conditions?: string;
    legal_clauses: any[]; // JSONB

    // Audit
    created_by?: string;
    created_at: string;
    updated_at: string;
}

export interface PolicyTemplateCreateRequest {
    policy_type_id: string;
    name: string;
    code: string;
    description?: string;

    template_content?: any;
    field_definitions?: any[];

    version?: number;
    is_active?: boolean;
    language?: string;

    terms_and_conditions?: string;
    legal_clauses?: any[];
}

export interface PolicyTemplateUpdateRequest {
    name?: string;
    description?: string;

    template_content?: any;
    field_definitions?: any[];

    is_active?: boolean;
    language?: string;

    terms_and_conditions?: string;
    legal_clauses?: any[];
}
