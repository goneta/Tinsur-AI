/**
 * TypeScript types for Payment.
 */

export interface Payment {
    id: string;
    company_id: string;
    client_id: string;
    policy_id: string;
    payment_number: string;
    amount: number;
    currency: string;
    payment_method: 'stripe' | 'mobile_money' | 'bank_transfer' | 'cash';
    payment_gateway?: 'stripe' | 'orange_money' | 'mtn_money' | 'moov_money' | 'wave';
    status: 'pending' | 'processing' | 'completed' | 'failed' | 'refunded';
    reference_number?: string;
    metadata?: Record<string, any>;
    failure_reason?: string;
    paid_at?: string;
    refunded_at?: string;
    created_at: string;
    updated_at: string;
    // Helper fields from joined tables (mapped in frontend if needed, or by backend)
    client_name?: string;
    policy_number_display?: string;
    created_by_name?: string;
}

export interface PaymentListResponse {
    payments: Payment[];
    total: number;
    page: number;
    page_size: number;
}

export interface PaymentProcessRequest {
    policy_id: string;
    amount: number;
    payment_details: Record<string, any>;
}

export interface PaymentRefundRequest {
    refund_amount: number;
    reason: string;
}
