'use client';

import React from 'react';
import { useLanguage } from '@/contexts/language-context';

const pipelineData = [
    { quarter: 'Q1 2025', csm: 2.8, release: 0.7, newBusiness: 1.2 },
    { quarter: 'Q2 2025', csm: 3.3, release: 0.8, newBusiness: 1.5 },
    { quarter: 'Q3 2025', csm: 3.9, release: 0.9, newBusiness: 1.1 },
    { quarter: 'Q4 2025', csm: 4.2, release: 1.0, newBusiness: 0.8 },
    { quarter: 'Q1 2026', csm: 4.6, release: 1.1, newBusiness: 1.3 },
    { quarter: 'Q2 2026', csm: 5.1, release: 1.2, newBusiness: 1.6 },
];

const maxValue = 6;

function Bar({ value, color, label }: { value: number; color: string; label: string }) {
    const height = (value / maxValue) * 100;
    return (
        <div className="flex flex-col items-center gap-1 flex-1">
            <span className="text-[10px] text-muted-foreground font-medium">{value}M</span>
            <div className="w-full h-32 bg-muted rounded-t relative flex items-end">
                <div
                    className={`w-full ${color} rounded-t transition-all`}
                    style={{ height: `${height}%` }}
                />
            </div>
        </div>
    );
}

export default function CSMPipeline() {
    const { t } = useLanguage();

    return (
        <div className="space-y-4">
            {/* Chart */}
            <div className="space-y-2">
                {pipelineData.map((item) => (
                    <div key={item.quarter} className="flex items-end gap-1">
                        <span className="text-xs text-muted-foreground w-16 shrink-0">
                            {item.quarter}
                        </span>
                        <div className="flex gap-1 flex-1">
                            <div
                                className="h-5 bg-indigo-500 rounded-sm transition-all"
                                style={{ width: `${(item.csm / maxValue) * 100}%` }}
                                title={`CSM: ${item.csm}M`}
                            />
                            <div
                                className="h-5 bg-emerald-500 rounded-sm transition-all"
                                style={{ width: `${(item.release / maxValue) * 100}%` }}
                                title={`Release: ${item.release}M`}
                            />
                            <div
                                className="h-5 bg-amber-500 rounded-sm transition-all"
                                style={{ width: `${(item.newBusiness / maxValue) * 100}%` }}
                                title={`New Business: ${item.newBusiness}M`}
                            />
                        </div>
                    </div>
                ))}
            </div>

            {/* Legend */}
            <div className="flex items-center gap-4 text-xs text-muted-foreground pt-1">
                <div className="flex items-center gap-1.5">
                    <span className="h-2.5 w-2.5 rounded-sm bg-indigo-500" />
                    {t('financials.csm_balance', 'CSM Balance')}
                </div>
                <div className="flex items-center gap-1.5">
                    <span className="h-2.5 w-2.5 rounded-sm bg-emerald-500" />
                    {t('financials.csm_release', 'CSM Release')}
                </div>
                <div className="flex items-center gap-1.5">
                    <span className="h-2.5 w-2.5 rounded-sm bg-amber-500" />
                    {t('financials.new_business', 'New Business')}
                </div>
            </div>
        </div>
    );
}
