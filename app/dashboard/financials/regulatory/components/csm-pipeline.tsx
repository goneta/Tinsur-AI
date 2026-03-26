'use client';

import React, { useState, useEffect } from 'react';
import {
    AreaChart,
    Area,
    XAxis,
    YAxis,
    CartesianGrid,
    Tooltip,
    ResponsiveContainer
} from 'recharts';
import { Badge } from '@/components/ui/badge';
import { useLanguage } from '@/contexts/language-context';

const MONTHS = ["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"];

interface Projection {
    month: string;
    release: number;
}

export default function CSMPipeline() {
    const [projections, setProjections] = useState<Projection[]>([]);
    const [loading, setLoading] = useState(true);
    const { formatPrice } = useLanguage();

    useEffect(() => {
        const fetchProjections = async () => {
            try {
                const res = await fetch('/api/v1/regulatory/ifrs17/projections');
                const data = await res.json();

                // Map to month names
                const currentMonth = new Date().getMonth();
                const chartData = data.map((p: any, i: number) => ({
                    month: MONTHS[(currentMonth + i) % 12],
                    release: p.projected_release
                }));

                setProjections(chartData);
            } catch (error) {
                console.error("Failed to fetch projections:", error);
            } finally {
                setLoading(false);
            }
        };
        fetchProjections();
    }, []);

    if (loading) return <div className="h-[300px] flex items-center justify-center">Predicting profit releases...</div>;

    const totalRelease = projections.reduce((acc, curr) => acc + curr.release, 0);

    return (
        <div className="space-y-4">
            <div className="h-[300px] w-full mt-4">
                <ResponsiveContainer width="100%" height="100%">
                    <AreaChart
                        data={projections}
                        margin={{ top: 10, right: 30, left: 0, bottom: 0 }}
                    >
                        <defs>
                            <linearGradient id="colorRelease" x1="0" y1="0" x2="0" y2="1">
                                <stop offset="5%" stopColor="#82ca9d" stopOpacity={0.8} />
                                <stop offset="95%" stopColor="#82ca9d" stopOpacity={0} />
                            </linearGradient>
                        </defs>
                        <CartesianGrid strokeDasharray="3 3" vertical={false} />
                        <XAxis dataKey="month" />
                        <YAxis tickFormatter={(value: number) => `$${value}`} />
                        <Tooltip
                            formatter={(value: any) => formatPrice(Number(value) || 0)}
                            contentStyle={{ borderRadius: '8px', border: 'none', boxShadow: '0 4px 6px -1px rgb(0 0 0 / 0.1)' }}
                        />
                        <Area
                            type="monotone"
                            dataKey="release"
                            stroke="#82ca9d"
                            fillOpacity={1}
                            fill="url(#colorRelease)"
                        />
                    </AreaChart>
                </ResponsiveContainer>
            </div>
            <div className="p-4 bg-muted/50 rounded-lg flex justify-between items-center">
                <div>
                    <p className="text-sm text-muted-foreground">Total 12-Month Expected Revenue</p>
                    <p className="text-2xl font-bold text-green-700">{formatPrice(totalRelease)}</p>
                </div>
                <div className="text-right">
                    <p className="text-sm text-muted-foreground font-medium">Reporting Standard</p>
                    <Badge variant="outline">IFRS 17 (GMM)</Badge>
                </div>
            </div>
        </div>
    );
}
