
export interface CoInsuranceShare {
    id: string;
    company_id: string;
    company_name: string;
    share_percentage: number;
    fee_percentage: number;
    notes?: string;
    created_at: string;
}

export interface CoInsuranceShareCreateRequest {
    company_id: string;
    share_percentage: number;
    fee_percentage?: number;
    notes?: string;
}
