import api from './api';

export interface Account {
    id: string;
    code: string;
    name: string;
    account_type: string;
    description?: string;
    is_active: boolean;
    created_at: string;
}

export interface LedgerEntry {
    id: string;
    journal_entry_id: string;
    account_id: string;
    debit: number;
    credit: number;
    account_name?: string;
    account_code?: string;
}

export interface JournalEntry {
    id: string;
    entry_date: string;
    description: string;
    reference?: string;
    entries: LedgerEntry[];
}

export interface TrialBalanceItem {
    account_name: string;
    account_code: string;
    total_debit: number;
    total_credit: number;
    balance: number;
}

export interface FinancialReportItem {
    name: string;
    code: string;
    amount: number;
}

export interface ProfitLossData {
    revenue: FinancialReportItem[];
    expenses: FinancialReportItem[];
    total_revenue: number;
    total_expenses: number;
    net_profit: number;
}

export interface BalanceSheetData {
    assets: FinancialReportItem[];
    liabilities: FinancialReportItem[];
    equity: FinancialReportItem[];
    total_assets: number;
    total_liabilities: number;
    total_equity: number;
}

export const accountingApi = {
    getAccounts: async () => {
        const response = await api.get<Account[]>('/accounting/accounts');
        return response.data;
    },

    getLedger: async (limit: number = 100) => {
        const response = await api.get<JournalEntry[]>(`/accounting/ledger?limit=${limit}`);
        return response.data;
    },

    getTrialBalance: async () => {
        const response = await api.get<TrialBalanceItem[]>('/accounting/trial-balance');
        return response.data;
    },

    getProfitLoss: async (startDate?: string, endDate?: string) => {
        const params = new URLSearchParams();
        if (startDate) params.append('start_date', startDate);
        if (endDate) params.append('end_date', endDate);
        const response = await api.get<ProfitLossData>(`/accounting/profit-loss?${params.toString()}`);
        return response.data;
    },

    getBalanceSheet: async (asOfDate?: string) => {
        const params = new URLSearchParams();
        if (asOfDate) params.append('as_of_date', asOfDate);
        const response = await api.get<BalanceSheetData>(`/accounting/balance-sheet?${params.toString()}`);
        return response.data;
    },

    initializeAccounts: async () => {
        const response = await api.post('/accounting/initialize');
        return response.data;
    }
};
