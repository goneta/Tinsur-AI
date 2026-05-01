/**
 * Updated dashboard content for new layout.
 */
'use client';

import { useAuth } from '@/lib/auth';
import { Button } from '@/components/ui/button';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Users, FileText, Shield, TrendingUp, ArrowRight, Loader2 } from 'lucide-react';
import Link from 'next/link';
import { adminApi, DashboardStats } from '@/lib/admin-api';
import { useState, useEffect } from 'react';
import { formatCurrency } from '@/lib/utils';
import { useLanguage } from '@/contexts/language-context';

export default function DashboardPage() {
    const { t, formatPrice } = useLanguage();
    const [statsData, setStatsData] = useState<DashboardStats | null>(null);
    const [recentActivity, setRecentActivity] = useState<any[]>([]);
    const [loading, setLoading] = useState(true);
    const [loadingActivity, setLoadingActivity] = useState(true);

    useEffect(() => {
        async function fetchData() {
            try {
                const [stats, activity] = await Promise.all([
                    adminApi.getStats(),
                    adminApi.getRecentActivity()
                ]);
                setStatsData(stats);
                setRecentActivity(activity.activities);
            } catch (error) {
                console.error('Failed to fetch dashboard data:', error);
            } finally {
                setLoading(false);
                setLoadingActivity(false);
            }
        }
        fetchData();
    }, []);

    const formatGrowth = (val: number | undefined) => {
        if (val === undefined) return "+0%";
        const prefix = val >= 0 ? "+" : "";
        return `${prefix}${val}%`;
    };

    const stats = [
        {
            title: t('dashboard.total_clients', 'Total Clients'),
            value: loading ? "..." : (statsData?.clients.total.toLocaleString() || "0"),
            change: formatGrowth(statsData?.clients.growth),
            icon: Users,
            color: "text-blue-600 bg-blue-100",
        },
        {
            title: t('dashboard.active_policies', 'Active Policies'),
            value: loading ? "..." : (statsData?.policies.active.toLocaleString() || "0"),
            change: formatGrowth(statsData?.policies.growth),
            icon: Shield,
            color: "text-green-600 bg-green-100",
        },
        {
            title: t('dashboard.pending_quotes', 'Pending Quotes'),
            value: loading ? "..." : (statsData?.quotes.pending.toLocaleString() || "0"),
            change: formatGrowth(statsData?.quotes.growth),
            icon: FileText,
            color: "text-orange-600 bg-orange-100",
        },
        {
            title: t('dashboard.monthly_revenue', 'Monthly Revenue'),
            value: loading ? "..." : formatPrice(statsData?.revenue.monthly || 0),
            change: formatGrowth(statsData?.revenue.growth),
            icon: TrendingUp,
            color: "text-purple-600 bg-purple-100",
        },
    ];

    return (
        <div className="space-y-6">
            <div className="flex items-center justify-between">
                <div>
                    <h2 className="text-2xl font-bold tracking-tight">{t('page.dashboard', 'Dashboard')}</h2>
                    <p className="text-muted-foreground">
                        {t('dashboard.welcome', 'Welcome back! Here is your insurance portfolio summary.')}
                    </p>
                </div>
                <Button>
                    {t('btn.download_report', 'Download Report')}
                </Button>
            </div>

            <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-4">
                {stats.map((stat, index) => (
                    <Card key={index} className="transition-all hover:shadow-md">
                        <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
                            <CardTitle className="text-sm font-medium">
                                {stat.title}
                            </CardTitle>
                            <div className={`rounded-full p-2 ${stat.color}`}>
                                <stat.icon className="h-4 w-4" />
                            </div>
                        </CardHeader>
                        <CardContent>
                            <div className="text-2xl font-bold">{stat.value}</div>
                            <p className="text-xs text-muted-foreground">
                                <span className={stat.change.startsWith('+') ? 'text-green-600' : 'text-red-600'}>
                                    {stat.change}
                                </span>{" "}
                                {t('dashboard.from_last_month', 'from last month')}
                            </p>
                        </CardContent>
                    </Card>
                ))}
            </div>

            <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-7">
                <Card className="col-span-4">
                    <CardHeader>
                        <CardTitle>{t('dashboard.recent_activity', 'Recent Activity')}</CardTitle>
                        <CardDescription>
                            {t('dashboard.recent_activity_desc', 'Your recent actions and notifications.')}
                        </CardDescription>
                    </CardHeader>
                    <CardContent>
                        <div className="space-y-8">
                            {loadingActivity ? (
                                <div className="flex justify-center py-8">
                                    <Loader2 className="h-8 w-8 animate-spin text-muted-foreground" />
                                </div>
                            ) : recentActivity.length > 0 ? (
                                recentActivity.map((activity, i) => (
                                    <div key={i} className="flex items-center">
                                        <div className="ml-4 space-y-1">
                                            <p className="text-sm font-medium leading-none">{activity.title}</p>
                                            <p className="text-sm text-muted-foreground">
                                                {activity.description}
                                            </p>
                                        </div>
                                        {activity.amount && (
                                            <div className="ml-auto font-medium">{activity.amount}</div>
                                        )}
                                    </div>
                                ))
                            ) : (
                                <div className="text-center py-8 text-muted-foreground">
                                    {t('dashboard.no_activity', 'No recent activity')}
                                </div>
                            )}
                        </div>
                    </CardContent>
                </Card>

                <Card className="col-span-3">
                    <CardHeader>
                        <CardTitle>{t('dashboard.quick_actions', 'Quick Actions')}</CardTitle>
                        <CardDescription>
                            {t('dashboard.frequently_used', 'Frequently used actions.')}
                        </CardDescription>
                    </CardHeader>
                    <CardContent className="space-y-4">
                        <Link href="/dashboard/quotes/new">
                            <Button variant="outline" className="w-full justify-between group">
                                {t('dashboard.create_quote', 'Create New Quote')}
                                <ArrowRight className="h-4 w-4 transition-transform group-hover:translate-x-1" />
                            </Button>
                        </Link>
                        <Link href="/dashboard/clients/new">
                            <Button variant="outline" className="w-full justify-between group">
                                {t('dashboard.add_client', 'Add New Client')}
                                <ArrowRight className="h-4 w-4 transition-transform group-hover:translate-x-1" />
                            </Button>
                        </Link>
                        <Link href="/dashboard/payments">
                            <Button variant="outline" className="w-full justify-between group">
                                {t('dashboard.process_payment', 'Process Payment')}
                                <ArrowRight className="h-4 w-4 transition-transform group-hover:translate-x-1" />
                            </Button>
                        </Link>
                    </CardContent>
                </Card>
            </div>
        </div>
    );
}
