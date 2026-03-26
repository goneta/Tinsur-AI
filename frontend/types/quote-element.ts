export interface QuoteElement {
    id: string;
    company_id: string;
    category: 'base_rate' | 'coverage_amount' | 'risk_multiplier' | 'fixed_fee' | 'government_tax' | 'company_discount';
    name: string;
    value: number;
    description?: string;
    is_active: boolean;
    created_at: string;
    updated_at: string;
}

export type QuoteElementCategory = QuoteElement['category'];

export const QUOTE_ELEMENT_CATEGORIES: { value: QuoteElementCategory; label: string }[] = [
    { value: 'base_rate', label: 'Base Rate' },
    { value: 'coverage_amount', label: 'Coverage Amount' },
    { value: 'risk_multiplier', label: 'Risk Multiplier' },
    { value: 'fixed_fee', label: 'Fixed Fee' },
    { value: 'government_tax', label: 'Government Tax' },
    { value: 'company_discount', label: 'Company Discount' },
];
