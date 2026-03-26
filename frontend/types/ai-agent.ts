export type PreviewType = 'empty' | 'quote' | 'policy' | 'claim' | 'quote_selection' | 'quote_progress';

export interface PreviewState {
    type: PreviewType;
    data: any | null;
    isLoading?: boolean;
}

export interface QuoteData {
    client_name: string;
    quote_number: string;
    premium_amount: number;
    base_premium?: number;
    risk_adjustment?: string | number;
    discount_percent?: number;
    discount_amount?: number;
    policy_type: string;
    coverage_amount?: number;
    duration_months?: number;
    payment_frequency?: string;
    vehicle_value?: number;
    vehicle_age?: number;
    vehicle_mileage?: number;
    vehicle_registration?: string;
    license_number?: string;
    driver_dob?: string;
    manual_discount?: number;
    coverage_details?: string;
    status?: string;
    valid_until?: string;
}

export interface PolicyData {
    policy_number: string;
    client_name: string;
    effective_date: string;
    expiry_date: string;
    premium: number;
    status: string;
}

export interface ClaimData {
    claim_number: string;
    policy_number: string;
    incident_date: string;
    status: string;
    estimated_amount: number;
}
