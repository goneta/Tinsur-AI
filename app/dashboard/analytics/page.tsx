"use client";

import { useState, useEffect } from "react";
import { useQuery } from "@tanstack/react-query";
import { UnifiedFilter } from "@/components/analytics/unified-filter";
import { AnalyticsFilter, AnalyticsDashboardResponse } from "@/lib/types/analytics";
import { analyticsApi } from "@/lib/analytics-api";
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from "@/components/ui/card";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";
import { Loader2, TrendingUp, TrendingDown, DollarSign, Users, FileText, AlertCircle } from "lucide-react";
import {
    LineChart,
    Line,
    BarChart,
    Bar,
    XAxis,
    YAxis,
    CartesianGrid,
    Tooltip,
    Legend,
    ResponsiveContainer,
    Pie,
    Cell
} from 'recharts';
import { formatCurrency } from "@/lib/utils";
import { useLanguage } from "@/contexts/language-context";

// --- Components ---

function MetricCard({ title, value, previousValue, trend, prefix = "" }: { title: string, value: number, previousValue?: number, trend?: 'up' | 'down' | 'stable', prefix?: string }) {
    const isPositive = trend === 'up';
    const isNegative = trend === 'down';
    const { t } = useLanguage();

    // Basic formatting
    const formattedValue = new Intl.NumberFormat('en-US', { maximumFractionDigits: 1 }).format(value);

    return (
        <Card>
            <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
                <CardTitle className="text-sm font-medium">
                    {title}
                </CardTitle>
                {title.includes("Revenue") ? <DollarSign className="h-4 w-4 text-muted-foreground" /> :
                    title.includes("Policies") ? <FileText className="h-4 w-4 text-muted-foreground" /> :
                        <Users className="h-4 w-4 text-muted-foreground" />}
            </CardHeader>
            <CardContent>
                <div className="text-2xl font-bold">{prefix}{formattedValue}</div>
                <p className="text-xs text-muted-foreground flex items-center mt-1">
                    {trend && (
                        <>
                            {isPositive ? <TrendingUp className="h-3 w-3 text-green-500 mr-1" /> :
                                isNegative ? <TrendingDown className="h-3 w-3 text-red-500 mr-1" /> : null}
                            <span className={isPositive ? "text-green-500" : isNegative ? "text-red-500" : ""}>
                                {previousValue ? `${((value - previousValue) / previousValue * 100).toFixed(1)}%` : "0%"}
                            </span>
                            <span className="ml-1">{t('analytics.trend_from_period')}</span>
                        </>
                    )}
                </p>
            </CardContent>
        </Card>
    )
}

export default function AnalyticsPage() {
    const { t } = useLanguage();
    const [filter, setFilter] = useState<AnalyticsFilter>({
        period_type: 'month',
        scope: 'company',
        company_id: '85ecdbd1-d151-4cd8-850b-53efc4ac1cb8', // Hardcoded for demo, normally from auth context

    });

    const { data, isLoading, error, refetch } = useQuery<AnalyticsDashboardResponse>({
        queryKey: ['analytics', filter],
        queryFn: () => analyticsApi.getDashboardMetrics(filter),
        retry: false
    });

    const handleExport = (format: "csv" | "pdf") => {
        // Determine report type based on active tab or default
        // For simplicity, defaulting to financial_close
        analyticsApi.exportReport(filter, format, "financial_close"); // Could add dialog to select type
    };

    if (isLoading) {
        return <div className="flex items-center justify-center h-screen"><Loader2 className="h-8 w-8 animate-spin" /></div>;
    }

    if (error) {
        return <div className="p-8 text-red-500">Error loading metrics: {(error as any).message}</div>
    }

    const financials = data?.financials;
    const operations = data?.operations;

    return (
        <div className="flex-1 space-y-4 p-8 pt-6">
            <div className="flex items-center justify-between space-y-2">
                <h2 className="text-3xl font-bold tracking-tight">{t('analytics.title')}</h2>
            </div>

            <UnifiedFilter
                initialFilter={filter}
                onFilterChange={setFilter}
                onExport={handleExport}
            />

            <Tabs defaultValue="overview" className="space-y-4">
                <TabsList>
                    <TabsTrigger value="overview">{t('analytics.overview')}</TabsTrigger>
                    <TabsTrigger value="financials">{t('analytics.financials')}</TabsTrigger>
                    <TabsTrigger value="operations">{t('analytics.operations')}</TabsTrigger>
                </TabsList>

                <TabsContent value="overview" className="space-y-4">
                    <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-4">
                        {financials && (
                            <>
                                <MetricCard
                                    title={t('analytics.total_revenue')}
                                    value={financials.total_revenue.value}
                                    previousValue={financials.total_revenue.previous_value}
                                    trend={financials.total_revenue.trend}
                                    prefix="$" // Or dynamic currency
                                />
                                <MetricCard
                                    title={t('analytics.net_profit')}
                                    value={financials.net_profit.value}
                                    previousValue={financials.net_profit.previous_value}
                                    trend={financials.net_profit.trend}
                                    prefix="$"
                                />
                            </>
                        )}
                        {operations && (
                            <>
                                <MetricCard
                                    title={t('analytics.active_policies')}
                                    value={operations.active_policies.value}
                                    previousValue={operations.active_policies.previous_value}
                                    trend={operations.active_policies.trend}
                                />
                                <MetricCard
                                    title={t('analytics.claims_ratio')}
                                    value={operations.claims_ratio.value}
                                    previousValue={operations.claims_ratio.previous_value}
                                    trend={operations.claims_ratio.trend}
                                    prefix="" // Ratio is %
                                />
                            </>
                        )}
                    </div>

                    <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-7">
                        <Card className="col-span-4">
                            <CardHeader>
                                <CardTitle>{t('analytics.revenue_overview')}</CardTitle>
                                <CardDescription>{t('analytics.income_vs_expenses')}</CardDescription>
                            </CardHeader>
                            <CardContent className="pl-2">
                                <div className="h-[300px] w-full flex items-center justify-center text-muted-foreground">
                                    {/* Placeholder for complex time series - requires backend endpoint for historical data */}
                                    {t('analytics.chart_loading')}
                                </div>
                            </CardContent>
                        </Card>

                        <Card className="col-span-3">
                            <CardHeader>
                                <CardTitle>{t('analytics.top_agents')}</CardTitle>
                                <CardDescription>{t('analytics.sales_leaderboard')}</CardDescription>
                            </CardHeader>
                            <CardContent>
                                <div className="space-y-4">
                                    {data?.performance.top_agents.map((agent, i) => (
                                        <div key={i} className="flex items-center">
                                            <div className="ml-4 space-y-1">
                                                <p className="text-sm font-medium leading-none">{agent.name}</p>
                                                <p className="text-sm text-muted-foreground">{agent.count} Policies</p>
                                            </div>
                                            <div className="ml-auto font-medium">{formatCurrency(agent.sales)}</div>
                                        </div>
                                    ))}
                                    {data?.performance.top_agents.length === 0 && <div className="text-sm text-muted-foreground text-center py-4">{t('analytics.no_data')}</div>}
                                </div>
                            </CardContent>
                        </Card>
                    </div>
                </TabsContent>
            </Tabs>
        </div>
    );
}
