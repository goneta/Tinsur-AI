/**
 * TypeScript types for Policy.
 */

export interface Policy {
    id: string;
    company_id: string;
    client_id: string;
    policy_type_id: string;
    quote_id?: string;
    policy_number: string;
    sales_agent_id?: string;
    pos_location_id?: string;

    // Coverage & Premium
    coverage_amount?: number;
    premium_amount: number;
    premium_frequency: 'monthly' | 'quarterly' | 'semi-annual' | 'annual';

    // Dates
    start_date: string;
    end_date: string;

    // Status
    status: 'pending_activation' | 'active' | 'suspended' | 'cancelled' | 'expired' | 'renewed';
    cancellation_reason?: string;

    // Documents
    policy_document_url?: string;
    qr_code_data?: string;

    // Additional
    details?: any; // JSONB
    notes?: string;

    // Audit
    created_at: string;
    updated_at: string;
    client_name: string;
    created_by_name: string;
}

export interface PolicyCreateRequest {
    client_id: string;
    policy_type_id: string;
    quote_id?: string;
    policy_number?: string; // Optional if auto-generated
    sales_agent_id?: string;
    pos_location_id?: string;

    coverage_amount?: number;
    premium_amount: number;
    premium_frequency?: 'monthly' | 'quarterly' | 'semi-annual' | 'annual';

    start_date: string;
    end_date: string;

    status?: 'pending_activation' | 'active' | 'suspended' | 'cancelled' | 'expired' | 'renewed';
    details?: any;
    notes?: string;
}

export interface PolicyUpdateRequest {
    coverage_amount?: number;
    premium_amount?: number;
    premium_frequency?: 'monthly' | 'quarterly' | 'semi-annual' | 'annual';

    start_date?: string;
    end_date?: string;

    status?: 'pending_activation' | 'active' | 'suspended' | 'cancelled' | 'expired' | 'renewed';
    cancellation_reason?: string;

    details?: any;
    notes?: string;
}

export interface PolicyRenewalRequest {
    new_end_date: string;
    premium_amount: number;
    coverage_amount?: number;
}

export interface PolicyCancellationRequest {
    cancellation_reason: string;
}

export interface EndorsementCreateRequest {
    endorsement_type: 'address_change' | 'coverage_change' | 'premium_change' | 'other';
    changes: any;
    premium_adjustment: number;
    effective_date: string;
    reason?: string;
}
