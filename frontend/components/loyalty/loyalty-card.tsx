'use client';

import { LoyaltyPoint } from '@/services/loyaltyService';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Progress } from '@/components/ui/progress';
import { Crown } from 'lucide-react';

interface LoyaltyCardProps {
    loyaltyData: LoyaltyPoint | null;
}

export function LoyaltyCard({ loyaltyData }: LoyaltyCardProps) {
    if (!loyaltyData) {
        return (
            <Card>
                <CardContent className="pt-6">
                    <p>Loading loyalty status...</p>
                </CardContent>
            </Card>
        )
    }

    const { points_balance, tier, total_points_earned } = loyaltyData;

    // Simple tier logic for progress bar
    const nextTierGoal = 1000;
    const progress = Math.min((points_balance / nextTierGoal) * 100, 100);

    return (
        <Card className="bg-gradient-to-br from-indigo-900 to-slate-900 text-white border-none">
            <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
                <CardTitle className="text-sm font-medium">
                    {tier.toUpperCase()} MEMBER
                </CardTitle>
                <Crown className="h-4 w-4 text-yellow-500" />
            </CardHeader>
            <CardContent>
                <div className="text-2xl font-bold">{points_balance.toLocaleString()} Points</div>
                <p className="text-xs text-slate-300">
                    Total Earned: {total_points_earned.toLocaleString()}
                </p>
                <div className="mt-4 space-y-2">
                    <div className="flex justify-between text-xs">
                        <span>Progress to Next Tier</span>
                        <span>{progress.toFixed(0)}%</span>
                    </div>
                    <Progress value={progress} className="h-2 bg-slate-700" indicatorClassName="bg-yellow-500" />
                </div>
            </CardContent>
        </Card>
    );
}
