'use client';

import { useState, useEffect, useCallback } from 'react';
import { useRouter } from 'next/navigation';
import {
    Activity,
    AlertTriangle,
    Car,
    RefreshCw,
    Shield,
    TrendingUp,
} from 'lucide-react';
import { toast } from 'sonner';

import { policyApi } from '@/lib/policy-api';
import { analyticsService, TelematicsData } from '@/services/analyticsService';
import { Policy } from '@/types/policy';

import { Button } from '@/components/ui/button';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select';
import { TelematicsTable } from '@/components/analytics/telematics-table';
import { Badge } from '@/components/ui/badge';
import { Progress } from "@/components/ui/progress"

import { useLanguage } from '@/contexts/language-context';

export default function TelematicsPage() {
    const { t } = useLanguage();
    const router = useRouter();
    const [policies, setPolicies] = useState<Policy[]>([]);
    const [selectedPolicyId, setSelectedPolicyId] = useState<string>('');
    const [telematicsData, setTelematicsData] = useState<TelematicsData[]>([]);
    const [safetyScore, setSafetyScore] = useState<{ score: number; rating: string; adjustment: number } | null>(null);
    const [loading, setLoading] = useState(false);
    const [dataLoading, setDataLoading] = useState(false);

    // Load policies on mount
    useEffect(() => {
        const loadPolicies = async () => {
            setLoading(true);
            try {
                const data = await policyApi.getPolicies({ limit: 100 });
                // Filter for vehicle policies if needed, for now show all or assume backend handles it
                // Show all policies for now as we don't have policy_type name in the type definition yet
                const policiesToShow = data.policies;

                setPolicies(policiesToShow);
                if (policiesToShow.length > 0) {
                    setSelectedPolicyId(policiesToShow[0].id);
                }
            } catch (error) {
                console.error('Failed to load policies:', error);
                toast.error('Failed to load policies');
            } finally {
                setLoading(false);
            }
        };
        loadPolicies();
    }, []);

    // Load telematics data when policy changes
    useEffect(() => {
        if (!selectedPolicyId) return;

        const loadTelematics = async () => {
            setDataLoading(true);
            try {
                const [history, scoreData] = await Promise.all([
                    analyticsService.getTelematicsData(selectedPolicyId),
                    analyticsService.getSafetyScore(selectedPolicyId)
                ]);
                setTelematicsData(history);
                setSafetyScore({
                    score: scoreData.safety_score,
                    rating: scoreData.rating,
                    adjustment: scoreData.ubi_adjustment_percent
                });
            } catch (error) {
                console.error('Failed to load telematics data:', error);
                // toast.error('Failed to load telematics data'); // Suppress for now if no data exists
                setTelematicsData([]);
                setSafetyScore(null);
            } finally {
                setDataLoading(false);
            }
        };

        loadTelematics();
    }, [selectedPolicyId]);

    const handleSimulateTrip = async () => {
        if (!selectedPolicyId) return;

        try {
            setDataLoading(true);
            // Simulate random trip data
            const distance = Math.floor(Math.random() * 50) + 5;
            const avgSpeed = Math.floor(Math.random() * 60) + 30;
            const maxSpeed = avgSpeed + Math.floor(Math.random() * 40);

            // Heuristic for simple "simulation" logic in frontend not needed, backend handles processing
            // We just send raw data the backend capability expects
            const tripData = {
                distance_km: distance,
                avg_speed: avgSpeed,
                max_speed: maxSpeed,
                timestamp: new Date().toISOString(),
                hard_brakes: Math.floor(Math.random() * 3),
                rapid_accelerations: Math.floor(Math.random() * 3),
                device_id: "simulated-device-001"
            };

            await analyticsService.uploadTelematicsData(selectedPolicyId, tripData);

            toast.success('Trip simulated successfully');

            // Reload data
            const [history, scoreData] = await Promise.all([
                analyticsService.getTelematicsData(selectedPolicyId),
                analyticsService.getSafetyScore(selectedPolicyId)
            ]);
            setTelematicsData(history);
            setSafetyScore({
                score: scoreData.safety_score,
                rating: scoreData.rating,
                adjustment: scoreData.ubi_adjustment_percent
            });

        } catch (error) {
            console.error('Failed to simulate trip:', error);
            toast.error('Failed to simulate trip');
        } finally {
            setDataLoading(false);
        }
    };

    if (loading) {
        return <div className="p-8 text-center">Loading...</div>;
    }

    return (
        <div className="space-y-6">
            <div className="flex flex-col gap-4 md:flex-row md:items-center md:justify-between">
                <div>
                    <h2 className="text-3xl font-bold tracking-tight">{t('telematics.title')}</h2>
                    <p className="text-muted-foreground">{t('telematics.desc')}</p>
                </div>
                <div className="w-full md:w-[300px]">
                    <Select value={selectedPolicyId} onValueChange={setSelectedPolicyId}>
                        <SelectTrigger>
                            <SelectValue placeholder="Select Policy" />
                        </SelectTrigger>
                        <SelectContent>
                            {policies.map((policy) => (
                                <SelectItem key={policy.id} value={policy.id}>
                                    {policy.policy_number}
                                </SelectItem>
                            ))}
                        </SelectContent>
                    </Select>
                </div>
            </div>

            {selectedPolicyId ? (
                <>
                    {/* KPI Cards */}
                    <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-4">
                        <Card>
                            <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
                                <CardTitle className="text-sm font-medium">{t('telematics.driving_score')}</CardTitle>
                                <Shield className="h-4 w-4 text-muted-foreground" />
                            </CardHeader>
                            <CardContent>
                                <div className="text-2xl font-bold">{safetyScore?.score?.toFixed(0) || 'N/A'}</div>
                                <p className="text-xs text-muted-foreground">
                                    {t('telematics.rating', 'Rating: {0}').replace('{0}',
                                        safetyScore?.rating ? t(`telematics.rating_${safetyScore.rating.toLowerCase()}`, safetyScore.rating) : 'N/A'
                                    )}
                                </p>
                                <div className="mt-3">
                                    <Progress value={safetyScore?.score || 0} className="h-2"
                                        indicatorClassName={
                                            (safetyScore?.score || 0) > 80 ? "bg-green-500" :
                                                (safetyScore?.score || 0) > 60 ? "bg-yellow-500" : "bg-red-500"
                                        }
                                    />
                                </div>
                            </CardContent>
                        </Card>

                        <Card>
                            <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
                                <CardTitle className="text-sm font-medium">{t('telematics.premium_adjustment', 'Premium Adjustment')}</CardTitle>
                                <TrendingUp className="h-4 w-4 text-muted-foreground" />
                            </CardHeader>
                            <CardContent>
                                <div className={`text-2xl font-bold ${(safetyScore?.adjustment || 0) < 0 ? 'text-green-600' : 'text-red-600'
                                    }`}>
                                    {safetyScore?.adjustment ? `${safetyScore.adjustment > 0 ? '+' : ''}${safetyScore.adjustment.toFixed(1)}%` : '0%'}
                                </div>
                                <p className="text-xs text-muted-foreground">
                                    {t('telematics.driving_history_basis', 'Based on driving history')}
                                </p>
                            </CardContent>
                        </Card>

                        <Card>
                            <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
                                <CardTitle className="text-sm font-medium">{t('telematics.total_trips')}</CardTitle>
                                <Car className="h-4 w-4 text-muted-foreground" />
                            </CardHeader>
                            <CardContent>
                                <div className="text-2xl font-bold">{telematicsData.length}</div>
                                <p className="text-xs text-muted-foreground">
                                    {t('telematics.recorded_trips', 'Recorded trips')}
                                </p>
                            </CardContent>
                        </Card>

                        <Card>
                            <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
                                <CardTitle className="text-sm font-medium">{t('telematics.model_status', 'Model Status')}</CardTitle>
                                <Activity className="h-4 w-4 text-muted-foreground" />
                            </CardHeader>
                            <CardContent>
                                <div className="text-2xl font-bold">{t('telematics.active', 'Active')}</div>
                                <p className="text-xs text-muted-foreground">
                                    {t('telematics.risk_analysis', 'Risk Analysis AI')}
                                </p>
                            </CardContent>
                        </Card>
                    </div>

                    <div className="grid gap-4 md:grid-cols-7">
                        <Card className="col-span-12 md:col-span-7">
                            <CardHeader className="flex flex-row items-center justify-between">
                                <div>
                                    <CardTitle>{t('telematics.trip_details')}</CardTitle>
                                    <CardDescription>{t('telematics.recent_activity', 'Recent driving activity and scores.')}</CardDescription>
                                </div>
                                <Button size="sm" variant="outline" onClick={handleSimulateTrip} disabled={dataLoading}>
                                    <RefreshCw className={`mr-2 h-4 w-4 ${dataLoading ? 'animate-spin' : ''}`} />
                                    {t('telematics.simulate_trip', 'Simulate Trip')}
                                </Button>
                            </CardHeader>
                            <CardContent>
                                {dataLoading && telematicsData.length === 0 ? (
                                    <div className="py-8 text-center text-muted-foreground">{t('common.loading', 'Loading...')}</div>
                                ) : (
                                    telematicsData.length > 0 ? (
                                        <TelematicsTable data={telematicsData} />
                                    ) : (
                                        <div className="py-8 text-center text-muted-foreground">{t('telematics.no_data', 'No trip data available.')}</div>
                                    )
                                )}
                            </CardContent>
                        </Card>
                    </div>
                </>
            ) : (
                <div className="flex h-[400px] flex-col items-center justify-center rounded-lg border bg-card p-8 text-center text-muted-foreground shadow-sm">
                    <Car className="h-12 w-12 opacity-50" />
                    <h3 className="mt-4 text-lg font-semibold">{t('telematics.no_policy_selected', 'No Policy Selected')}</h3>
                    <p className="mb-4 max-w-sm text-sm">{t('telematics.select_policy_desc', 'Select a vehicle insurance policy to view telematics data and safety scores.')}</p>
                </div>
            )}
        </div>
    );
}
