export interface AnalyticsFilter {
    start_date?: string; // YYYY-MM-DD
    end_date?: string;
    period_type: 'day' | 'week' | 'month' | 'year' | 'custom';
    scope: 'me' | 'team' | 'company' | 'client';
    company_id: string;
    employee_id?: string;
    client_id?: string;
    pos_location_id?: string;
}

export interface MetricValue {
    label: string;
    value: number;
    previous_value?: number;
    change_percentage?: number;
    trend?: 'up' | 'down' | 'stable';
}

export interface TimeSeriesPoint {
    date: string;
    value: number;
    category?: string;
}

export interface FinancialMetrics {
    total_revenue: MetricValue;
    total_expenses: MetricValue;
    net_profit: MetricValue;
    accounts_receivable: MetricValue;
    expense_breakdown: Array<{ name: string; value: number }>;
}

export interface OperationalMetrics {
    total_policies: MetricValue;
    new_policies: MetricValue;
    active_policies: MetricValue;
    claims_ratio: MetricValue;
    policy_growth_chart: TimeSeriesPoint[];
}

export interface PerformanceMetrics {
    top_agents: Array<{ name: string; sales: number; count: number }>;
    sales_by_pos: Array<any>;
}

export interface AnalyticsDashboardResponse {
    period_label: string;
    financials: FinancialMetrics;
    operations: OperationalMetrics;
    performance: PerformanceMetrics;
}
