'use client';

import { useState, useEffect } from 'react';
import { useLanguage } from '@/contexts/language-context';
import { ClientReferralStats, ReferralStatsData } from '@/components/collaboration/referral-stats';
import { ReferralList } from '@/components/portal/referral-list';
import { portalApi, Referral } from '@/lib/portal-api';
import { useToast } from '@/components/ui/use-toast';
import { Card, CardHeader, CardTitle, CardContent } from '@/components/ui/card';
import { Users2 } from 'lucide-react';

export default function ReferralPage() {
    const { t } = useLanguage();
    const { toast } = useToast();
    const [stats, setStats] = useState<ReferralStatsData | null>(null);
    const [referrals, setReferrals] = useState<Referral[]>([]);
    const [loading, setLoading] = useState(true);
    const [generating, setGenerating] = useState(false);

    useEffect(() => {
        fetchData();
    }, []);

    const fetchData = async () => {
        try {
            setLoading(true);
            const [statsData, referralsData] = await Promise.all([
                portalApi.getReferralStats(),
                portalApi.getReferrals()
            ]);
            setStats(statsData);
            setReferrals(referralsData);
        } catch (error) {
            console.error("Failed to fetch referral data", error);
            // toast({ title: "Error", description: "Failed to load referral data", variant: "destructive" });
        } finally {
            setLoading(false);
        }
    };

    const handleGenerateCode = async () => {
        try {
            setGenerating(true);
            await portalApi.createReferral();
            toast({
                title: t('referrals.code_created', "Code Generated!"),
                description: t('referrals.code_created_desc', "You can now start referring friends."),
            });
            await fetchData(); // Refresh to show the new code
        } catch (error) {
            console.error("Failed to generate code", error);
            toast({
                title: t('common.error', "Error"),
                description: t('referrals.generate_failed', "Failed to generate referral code."),
                variant: 'destructive'
            });
        } finally {
            setGenerating(false);
        }
    };

    return (
        <div className="space-y-6">
            <div className="flex items-center gap-3 mb-6">
                <div className="h-10 w-10 rounded-full bg-blue-100 flex items-center justify-center text-blue-600">
                    <Users2 className="h-6 w-6" />
                </div>
                <div>
                    <h1 className="text-2xl font-bold tracking-tight text-slate-900">{t('referrals.title', 'Refer a Friend')}</h1>
                    <p className="text-muted-foreground">{t('referrals.subtitle', 'Invite friends and earn rewards when they sign up.')}</p>
                </div>
            </div>

            <ClientReferralStats
                stats={stats}
                loading={loading}
                onGenerateCode={handleGenerateCode}
                isGenerating={generating}
            />

            <ReferralList referrals={referrals} />
        </div>
    );
}
