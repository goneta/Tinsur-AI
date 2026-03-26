'use client';

import { Card, CardContent, CardHeader, CardTitle, CardDescription } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Copy, Plus, Loader2 } from 'lucide-react';
import { useToast } from '@/components/ui/use-toast';
import { formatCurrency } from '@/lib/utils';
import { useLanguage } from '@/contexts/language-context';

export interface ReferralStatsData {
    referral_code: string | null;
    total_earned: number;
    pending_count: number;
    converted_count: number;
    total_referrals: number;
}

interface ReferralStatsProps {
    stats: ReferralStatsData | null;
    loading: boolean;
    onGenerateCode?: () => void;
    isGenerating?: boolean;
}

export function ReferralStats({ stats, loading }: ReferralStatsProps) {
    // We ignore the `loading` prop for strict skeletal loading but use it to prevent crashes if stats is null
    // Actually, let's use it.
    return (
        <ReferralStatsContent stats={stats} loading={loading} onGenerateCode={undefined} isGenerating={false} />
    );
}

// Exporting a more flexible version for the Portal
export function ClientReferralStats({ stats, loading, onGenerateCode, isGenerating }: ReferralStatsProps) {
    return <ReferralStatsContent stats={stats} loading={loading} onGenerateCode={onGenerateCode} isGenerating={isGenerating} />;
}

// Internal implementation
function ReferralStatsContent({ stats, loading, onGenerateCode, isGenerating }: ReferralStatsProps) {
    const { toast } = useToast();
    const { t } = useLanguage();

    const copyCode = () => {
        if (stats?.referral_code) {
            navigator.clipboard.writeText(stats.referral_code);
            toast({
                title: t('referrals.copied', "Copied!"),
                description: t('referrals.copied_desc', "Referral code copied to clipboard.")
            });
        }
    };

    if (loading) {
        return <div className="grid gap-4 md:grid-cols-2">
            <Card className="h-40 animate-pulse bg-muted/20" />
            <Card className="h-40 animate-pulse bg-muted/20" />
        </div>;
    }

    return (
        <div className="grid gap-4 md:grid-cols-2">
            <Card>
                <CardHeader>
                    <CardTitle>{t('referrals.your_code', 'Your Referral Code')}</CardTitle>
                    <CardDescription>{t('referrals.share_desc', 'Share this code to earn rewards.')}</CardDescription>
                </CardHeader>
                <CardContent className="flex items-center gap-4">
                    {stats?.referral_code ? (
                        <>
                            <code className="relative rounded bg-muted px-[0.3rem] py-[0.2rem] font-mono text-xl font-semibold">
                                {stats.referral_code}
                            </code>
                            <Button variant="outline" size="icon" onClick={copyCode}>
                                <Copy className="h-4 w-4" />
                            </Button>
                        </>
                    ) : (
                        <div className="flex flex-col gap-2">
                            <p className="text-sm text-muted-foreground">{t('referrals.no_code', "You don't have a code yet.")}</p>
                            {onGenerateCode && (
                                <Button onClick={onGenerateCode} disabled={isGenerating} size="sm" className="w-fit">
                                    {isGenerating ? <Loader2 className="h-4 w-4 animate-spin mr-2" /> : <Plus className="h-4 w-4 mr-2" />}
                                    {t('referrals.generate', 'Generate Code')}
                                </Button>
                            )}
                        </div>
                    )}
                </CardContent>
            </Card>

            <Card>
                <CardHeader>
                    <CardTitle>{t('referrals.program_stats', 'Program Stats')}</CardTitle>
                </CardHeader>
                <CardContent>
                    <div className="grid grid-cols-2 gap-4">
                        <div>
                            <p className="text-sm font-medium text-muted-foreground">{t('referrals.active_referrals', 'Active Referrals')}</p>
                            <p className="text-2xl font-bold">{stats?.total_referrals || 0}</p>
                        </div>
                        <div>
                            <p className="text-sm font-medium text-muted-foreground">{t('referrals.total_earned', 'Total Earned')}</p>
                            <p className="text-2xl font-bold">{formatCurrency(stats?.total_earned || 0)}</p>
                        </div>
                    </div>
                </CardContent>
            </Card>
        </div>
    );
}

