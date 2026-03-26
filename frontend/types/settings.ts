/**
 * Settings-related TypeScript types and interfaces
 */

export interface BankDetails {
    id?: string;
    bank_name: string;
    account_number: string;
    account_name: string;
    swift_code?: string;
    branch?: string;
}

export interface MobileMoneyAccount {
    id?: string;
    provider: string;
    account_number: string;
    account_name: string;
}

export interface CompanySettings {
    id: string;
    name: string;
    email: string;
    phone?: string;
    address?: string;
    registration_number?: string;
    logo_url?: string;
    primary_color?: string;
    secondary_color?: string;
    bank_details: BankDetails[];
    mobile_money_accounts: MobileMoneyAccount[];
    apr_percent?: number;
    arrangement_fee?: number;
    extra_fee?: number;
    // Mandatory Fees
    government_tax_percent?: number;
    admin_fee?: number;

    currency: string;
    country: string;
    timezone?: string;
    is_active: boolean;
    created_at: string;
    updated_at: string;
}

export interface UserSettings {
    id?: string;
    user_id: string;
    theme: 'light' | 'dark';
    language: 'en' | 'fr' | 'es';
    timezone?: string;
    date_format?: string;
    currency_format?: string;
    created_at?: string;
    updated_at?: string;
}

export interface RegionalSettings {
    currency: string;
    country: string;
    timezone: string;
    date_format: string;
}

export interface CompanyUpdateRequest {
    name?: string;
    email?: string;
    phone?: string;
    address?: string;
    registration_number?: string;
    currency?: string;
    country?: string;
    timezone?: string;
    bank_details?: BankDetails[];
    mobile_money_accounts?: MobileMoneyAccount[];
    apr_percent?: number;
    arrangement_fee?: number;
    extra_fee?: number;
    government_tax_percent?: number;
    admin_fee?: number;
    primary_color?: string;
    secondary_color?: string;
}

export interface UserSettingsUpdateRequest {
    theme?: 'light' | 'dark';
    language?: 'en' | 'fr' | 'es';
    timezone?: string;
    date_format?: string;
    currency_format?: string;
}

// Constants
export const SUPPORTED_LANGUAGES = [
    { code: 'en', name: 'English', flag: '🇬🇧' },
    { code: 'fr', name: 'Français', flag: '🇫🇷' },
    { code: 'es', name: 'Español', flag: '🇪🇸' },
] as const;

export const SUPPORTED_CURRENCIES = [
    { code: 'USD', symbol: '$', name: 'US Dollar' },
    { code: 'EUR', symbol: '€', name: 'Euro' },
    { code: 'GBP', symbol: '£', name: 'British Pound' },
    { code: 'XOF', symbol: 'CFA', name: 'West African CFA Franc' },
    { code: 'XAF', symbol: 'FCFA', name: 'Central African CFA Franc' },
    { code: 'GHS', symbol: '₵', name: 'Ghanaian Cedi' },
    { code: 'NGN', symbol: '₦', name: 'Nigerian Naira' },
    { code: 'KES', symbol: 'KSh', name: 'Kenyan Shilling' },
] as const;

export const SUPPORTED_COUNTRIES = [
    { code: 'US', name: 'United States' },
    { code: 'GB', name: 'United Kingdom' },
    { code: 'FR', name: 'France' },
    { code: 'ES', name: 'Spain' },
    { code: 'GH', name: 'Ghana' },
    { code: 'NG', name: 'Nigeria' },
    { code: 'KE', name: 'Kenya' },
    { code: 'SN', name: 'Senegal' },
    { code: 'CI', name: 'Côte d\'Ivoire' },
    { code: 'CM', name: 'Cameroon' },
] as const;

export const MOBILE_MONEY_PROVIDERS = [
    'MTN Mobile Money',
    'Vodafone Cash',
    'AirtelTigo Money',
    'M-Pesa',
    'Orange Money',
    'Wave',
    'Moov Money',
    'Djamo',
] as const;
