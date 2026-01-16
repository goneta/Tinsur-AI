export interface Claim {
    id: string;
    claim_number: string;
    policy_id: string;
    client_id: string;
    company_id: string;
    adjuster_id?: string;
    incident_date: string;
    incident_description: string;
    incident_location?: string;
    status: 'submitted' | 'under_review' | 'approved' | 'rejected' | 'paid' | 'closed';
    claim_amount: number;
    approved_amount?: number;
    evidence_files: string[];
    created_at: string;
    updated_at: string;
    created_by?: string;
}
