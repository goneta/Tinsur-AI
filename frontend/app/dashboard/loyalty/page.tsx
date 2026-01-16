'use client';

import { useState, useEffect } from 'react';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from '@/components/ui/table';
import { Badge } from '@/components/ui/badge';
import { Heart, Users, Award, TrendingUp } from 'lucide-react';
import api from '@/lib/api';

interface LoyaltyStats {
    total_points: number;
    active_members: number;
    tiers: Record<string, number>;
    recent_activity: Array<{
        client_id: string;
        client_name: string;
        points: number;
        tier: string;
        updated_at: string;
    }>;
}

import { useLanguage } from '@/contexts/language-context';

export default function LoyaltyPage() {
    const { t } = useLanguage();
    const [stats, setStats] = useState<LoyaltyStats | null>(null);
    const [loading, setLoading] = useState(true);

    useEffect(() => {
        fetchStats();
    }, []);

    const fetchStats = async () => {
        try {
            const response = await api.get('/loyalty/stats');
            setStats(response.data);
        } catch (error) {
            console.error("Failed to fetch loyalty stats", error);
        } finally {
            setLoading(false);
        }
    };

    if (loading) return <div className="p-8 text-center">Loading stats...</div>;

    return (
        <div className="flex-1 space-y-4 p-4 md:p-8 pt-6">
            <div className="flex items-center justify-between">
                <div>
                    <h2 className="text-3xl font-bold tracking-tight">{t('loyalty.title')}</h2>
                    <p className="text-muted-foreground">{t('loyalty.desc')}</p>
                </div>
            </div>

            <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-4">
                <Card>
                    <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
                        <CardTitle className="text-sm font-medium">{t('loyalty.total_points')}</CardTitle>
                        <Heart className="h-4 w-4 text-pink-500" />
                    </CardHeader>
                    <CardContent>
                        <div className="text-2xl font-bold">{stats?.total_points.toLocaleString()}</div>
                        <p className="text-xs text-muted-foreground">{t('loyalty.total_points_desc', 'Cumulative balance across all clients')}</p>
                    </CardContent>
                </Card>
                <Card>
                    <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
                        <CardTitle className="text-sm font-medium">{t('loyalty.active_members')}</CardTitle>
                        <Users className="h-4 w-4 text-muted-foreground" />
                    </CardHeader>
                    <CardContent>
                        <div className="text-2xl font-bold">{stats?.active_members}</div>
                        <p className="text-xs text-muted-foreground">{t('loyalty.active_members_desc', 'Clients with loyalty profiles')}</p>
                    </CardContent>
                </Card>
                <Card>
                    <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
                        <CardTitle className="text-sm font-medium">{t('loyalty.platinum_tier')}</CardTitle>
                        <Award className="h-4 w-4 text-purple-500" />
                    </CardHeader>
                    <CardContent>
                        <div className="text-2xl font-bold">{stats?.tiers.platinum || 0}</div>
                        <p className="text-xs text-muted-foreground">{t('loyalty.platinum_tier_desc', 'VIP clients with 10k+ points')}</p>
                    </CardContent>
                </Card>
                <Card>
                    <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
                        <CardTitle className="text-sm font-medium">{t('loyalty.conversion_rate')}</CardTitle>
                        <TrendingUp className="h-4 w-4 text-green-500" />
                    </CardHeader>
                    <CardContent>
                        <div className="text-2xl font-bold">12.5%</div>
                        <p className="text-xs text-muted-foreground">+2.1% from last month</p>
                    </CardContent>
                </Card>
            </div>

            <div className="grid gap-4 md:grid-cols-7">
                <Card className="col-span-4">
                    <CardHeader>
                        <CardTitle>{t('loyalty.recent_activity')}</CardTitle>
                        <CardDescription>{t('loyalty.recent_activity_desc', 'Latest point earning and updates.')}</CardDescription>
                    </CardHeader>
                    <CardContent>
                        <Table>
                            <TableHeader>
                                <TableRow>
                                    <TableHead>{t('loyalty.client')}</TableHead>
                                    <TableHead>{t('loyalty.balance')}</TableHead>
                                    <TableHead>{t('loyalty.tier')}</TableHead>
                                    <TableHead>{t('loyalty.last_update')}</TableHead>
                                </TableRow>
                            </TableHeader>
                            <TableBody>
                                {stats?.recent_activity.map((item) => (
                                    <TableRow key={item.client_id}>
                                        <TableCell className="font-medium">{item.client_name}</TableCell>
                                        <TableCell>{item.points.toLocaleString()}</TableCell>
                                        <TableCell>
                                            <Badge variant={
                                                item.tier === 'platinum' ? 'default' :
                                                    item.tier === 'gold' ? 'secondary' : 'outline'
                                            } className="capitalize">
                                                {item.tier}
                                            </Badge>
                                        </TableCell>
                                        <TableCell className="text-xs text-muted-foreground">
                                            {new Date(item.updated_at).toLocaleDateString()}
                                        </TableCell>
                                    </TableRow>
                                ))}
                            </TableBody>
                        </Table>
                    </CardContent>
                </Card>
                <Card className="col-span-3">
                    <CardHeader>
                        <CardTitle>{t('loyalty.tier_distribution')}</CardTitle>
                        <CardDescription>{t('loyalty.tier_distribution_desc', 'Customer breakdown by tier status.')}</CardDescription>
                    </CardHeader>
                    <CardContent className="space-y-4">
                        {['platinum', 'gold', 'silver', 'bronze'].map(tier => (
                            <div key={tier} className="flex items-center justify-between">
                                <span className="capitalize text-sm font-medium">{tier}</span>
                                <div className="flex items-center gap-2">
                                    <div className="h-2 w-32 bg-muted rounded-full overflow-hidden">
                                        <div
                                            className="h-full bg-primary"
                                            style={{ width: `${(stats?.tiers[tier] || 0) / (stats?.active_members || 1) * 100}%` }}
                                        />
                                    </div>
                                    <span className="text-xs text-muted-foreground">{stats?.tiers[tier] || 0}</span>
                                </div>
                            </div>
                        ))}
                    </CardContent>
                </Card>
            </div>
        </div>
    );
}
