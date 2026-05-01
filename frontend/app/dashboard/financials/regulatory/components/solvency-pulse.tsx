'use client';

import React from 'react';
import { useLanguage } from '@/contexts/language-context';

const metrics = [
    { key: 'scr_ratio', labelEn: 'SCR Ratio', value: 185, target: 150, unit: '%', status: 'healthy' },
    { key: 'mcr_ratio', labelEn: 'MCR Ratio', value: 320, target: 100, unit: '%', status: 'healthy' },
    { key: 'own_funds', labelEn: 'Own Funds', value: 12.5, target: 8.0, unit: 'M', status: 'healthy' },
    { key: 'technical_provisions', labelEn: 'Technical Provisions', value: 45.2, target: 50.0, unit: 'M', status: 'warning' },
];

function getStatusColor(status: string) {
    switch (status) {
        case 'healthy': return 'bg-green-500';
        case 'warning': return 'bg-yellow-500';
        case 'critical': return 'bg-red-500';
        default: return 'bg-gray-400';
    }
}

function getBarColor(status: string) {
    switch (status) {
        case 'healthy': return 'bg-green-500';
        case 'warning': return 'bg-yellow-500';
        case 'critical': return 'bg-red-500';
        default: return 'bg-gray-300';
    }
}

export default function SolvencyPulse() {
    const { t } = useLanguage();

    return (
        <div className="space-y-4">
            {metrics.map((metric) => {
                const percentage = Math.min((metric.value / metric.target) * 100, 100);
                return (
                    <div key={metric.key} className="space-y-1.5">
                        <div className="flex items-center justify-between text-sm">
                            <div className="flex items-center gap-2">
                                <span className={`h-2 w-2 rounded-full ${getStatusColor(metric.status)}`} />
                                <span className="font-medium">
                                    {t(`financials.${metric.key}`, metric.labelEn)}
                                </span>
                            </div>
                            <span className="text-muted-foreground">
                                {metric.value}{metric.unit}
                                <span className="text-xs ml-1">/ {metric.target}{metric.unit}</span>
                            </span>
                        </div>
                        <div className="h-2 w-full bg-muted rounded-full overflow-hidden">
                            <div
                                className={`h-full rounded-full transition-all ${getBarColor(metric.status)}`}
                                style={{ width: `${percentage}%` }}
                            />
                        </div>
                    </div>
                );
            })}

            <div className="pt-2 flex items-center gap-4 text-xs text-muted-foreground">
                <div className="flex items-center gap-1">
                    <span className="h-2 w-2 rounded-full bg-green-500" />
                    {t('financials.healthy', 'Healthy')}
                </div>
                <div className="flex items-center gap-1">
                    <span className="h-2 w-2 rounded-full bg-yellow-500" />
                    {t('financials.warning', 'Warning')}
                </div>
                <div className="flex items-center gap-1">
                    <span className="h-2 w-2 rounded-full bg-red-500" />
                    {t('financials.critical', 'Critical')}
                </div>
            </div>
        </div>
    );
}
