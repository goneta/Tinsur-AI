'use client';

import React from 'react';
import {
    Card,
    CardContent,
    CardHeader,
    CardTitle,
    CardDescription
} from '@/components/ui/card';
import {
    Activity,
    BarChart3,
    PieChart,
    TrendingUp,
    ShieldCheck
} from 'lucide-react';
import SolvencyPulse from './components/solvency-pulse';
import CSMPipeline from './components/csm-pipeline';
import { useLanguage } from '@/contexts/language-context';

export default function ExecutiveFinancialsPage() {
    const { t } = useLanguage();

    return (
        <div className="flex-1 space-y-4 p-4 md:p-8 pt-6">
            <div className="flex items-center justify-between space-y-2">
                <div>
                    <h2 className="text-3xl font-bold tracking-tight">{t('financials.reg_title')}</h2>
                    <p className="text-muted-foreground">
                        {t('financials.reg_desc')}
                    </p>
                </div>
            </div>

            <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-7">
                {/* Real-time Solvency Pulse */}
                <Card className="col-span-4 lg:col-span-3">
                    <CardHeader>
                        <CardTitle className="flex items-center gap-2">
                            <ShieldCheck className="h-5 w-5 text-indigo-600" />
                            {t('financials.solvency_pulse')}
                        </CardTitle>
                        <CardDescription>
                            {t('financials.solvency_desc')}
                        </CardDescription>
                    </CardHeader>
                    <CardContent>
                        <SolvencyPulse />
                    </CardContent>
                </Card>

                {/* CSM Pipeline Projection */}
                <Card className="col-span-4 lg:col-span-4">
                    <CardHeader>
                        <CardTitle className="flex items-center gap-2">
                            <TrendingUp className="h-5 w-5 text-green-600" />
                            {t('financials.ifrs_pipeline')}
                        </CardTitle>
                        <CardDescription>
                            {t('financials.ifrs_desc')}
                        </CardDescription>
                    </CardHeader>
                    <CardContent className="pl-2">
                        <CSMPipeline />
                    </CardContent>
                </Card>
            </div>
        </div>
    );
}
