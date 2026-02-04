export interface Quote {
    id: string;
    company_id: string;
    client_id: string;
    policy_type_id: string;
    quote_number: string;
    coverage_amount?: number;
    discount_percent: number;
    premium_frequency: 'monthly' | 'quarterly' | 'semi-annual' | 'annual';
    duration_months: number;
    premium_amount: number;
    final_premium: number;
    apr_percent?: number;
    arrangement_fee?: number;
    extra_fee?: number;
    admin_fee?: number; // New
    tax_amount?: number; // New
    tax_percent?: number; // New
    total_financed_amount?: number;
    total_installment_price?: number;
    monthly_installment?: number; // New
    excess?: number;
    included_services?: any[];
    risk_score?: number;
    status: 'draft' | 'draft_from_client' | 'submitted' | 'under_review' | 'approved' | 'rejected' | 'expired' | 'sent' | 'accepted' | 'policy_created' | 'archived';
    details?: Record<string, any>;
    notes?: string;
    valid_until: string;
    created_by: string;
    created_at: string;
    updated_at: string;
    is_expired: boolean;
    client_name: string;
    created_by_name: string;
}

export interface QuoteCreate {
    client_id: string;
    policy_type_id: string;
    coverage_amount: number;
    premium_frequency: 'monthly' | 'quarterly' | 'semi-annual' | 'annual';
    duration_months: number;
    discount_percent: number;
    excess?: number;
    included_services?: any[];
    financial_overrides?: Record<string, any>;
    details?: Record<string, any>; // Risk factors
    notes?: string;
    created_by?: string;
}

export type QuoteCreateRequest = QuoteCreate;

export interface QuoteUpdate {
    coverage_amount?: number;
    premium_frequency?: 'monthly' | 'quarterly' | 'semi-annual' | 'annual';
    duration_months?: number;
    discount_percent?: number;
    status?: string;
    details?: Record<string, any>;
    notes?: string;
}

export type QuoteUpdateRequest = QuoteUpdate;

export interface QuoteListResponse {
    quotes: Quote[];
    total: number;
    page: number;
    page_size: number;
}

export interface QuoteCalculationRequest {
    client_id: string;
    policy_type_id: string;
    coverage_amount: number;
    premium_frequency: string;
    duration_months: number;
    risk_factors: Record<string, any>;
    selected_services?: string[];
    financial_overrides?: Record<string, any>;
}

export interface QuoteCalculationResponse {
    base_premium: number;
    risk_adjustment: number;
    discount_amount: number;
    tax_amount: number;
    final_premium: number;
    apr_percent: number;
    arrangement_fee: number;
    extra_fee: number;
    admin_fee: number;
    total_financed_amount: number;
    monthly_installment: number;
    total_installment_price: number;
    excess: number;
    included_services: any[];
    risk_score: number;
    risk_factors_analysis: Record<string, any>;
    recommendations: string[];
    calculation_breakdown?: Record<string, any>;
}

export interface PolicyType {
    id: string;
    name: string;
    code: string;
    description?: string;
}
