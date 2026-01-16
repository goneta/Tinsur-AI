'use client';

import React, { useState, useEffect } from 'react';
import {
    PieChart,
    Pie,
    Cell,
    ResponsiveContainer,
    Label
} from 'recharts';
import { AlertCircle, CheckCircle2 } from 'lucide-react';

export default function SolvencyPulse() {
    interface SolvencyData {
        solvency_ratio: number;
        status: string;
        own_funds: number;
        scr: number;
    }
    const [data, setData] = useState<SolvencyData | null>(null);
    const [loading, setLoading] = useState(true);

    useEffect(() => {
        const fetchSolvency = async () => {
            try {
                const res = await fetch('/api/v1/regulatory/solvency/dashboard');
                const result = await res.json();
                setData(result);
            } catch (error) {
                console.error("Failed to fetch solvency data:", error);
            } finally {
                setLoading(false);
            }
        };
        fetchSolvency();
    }, []);

    if (loading) return <div className="h-[300px] flex items-center justify-center">Loading solvency metrics...</div>;
    if (!data) return <div>Failed to load data</div>;

    const ratio = data.solvency_ratio * 100;
    const status = data.status;

    // Color logic
    const getColor = () => {
        if (ratio >= 150) return '#10b981'; // Green
        if (ratio >= 110) return '#f59e0b'; // Amber
        return '#ef4444'; // Red
    };

    const chartData = [
        { name: 'Ratio', value: ratio },
        { name: 'Remainder', value: Math.max(0, 300 - ratio) } // Visual context up to 300%
    ];

    return (
        <div className="flex flex-col items-center justify-center space-y-4">
            <div className="h-[250px] w-full">
                <ResponsiveContainer width="100%" height="100%">
                    <PieChart>
                        <Pie
                            data={chartData}
                            cx="50%"
                            cy="50%"
                            innerRadius={70}
                            outerRadius={90}
                            startAngle={180}
                            endAngle={0}
                            paddingAngle={0}
                            dataKey="value"
                        >
                            <Cell fill={getColor()} />
                            <Cell fill="#f1f5f9" />
                            <Label
                                value={`${ratio.toFixed(0)}%`}
                                position="center"
                                className="text-4xl font-bold fill-current"
                                dy={-20}
                            />
                        </Pie>
                    </PieChart>
                </ResponsiveContainer>
            </div>

            <div className="grid grid-cols-2 gap-8 w-full px-4 text-center">
                <div>
                    <p className="text-sm text-muted-foreground uppercase font-semibold">Own Funds</p>
                    <p className="text-2xl font-bold">${(data.own_funds / 1000).toFixed(1)}k</p>
                </div>
                <div>
                    <p className="text-sm text-muted-foreground uppercase font-semibold">SCR Requirement</p>
                    <p className="text-2xl font-bold">${(data.scr / 1000).toFixed(1)}k</p>
                </div>
            </div>

            <div className={`mt-4 flex items-center gap-2 p-2 rounded-lg w-full justify-center ${status === 'Healthy' ? 'bg-green-50 text-green-700 border border-green-200' :
                status === 'Watch' ? 'bg-amber-50 text-amber-700 border border-amber-200' :
                    'bg-red-50 text-red-700 border border-red-200'
                }`}>
                {status === 'Healthy' ? <CheckCircle2 className="h-5 w-5" /> : <AlertCircle className="h-5 w-5" />}
                <span className="font-bold">Status: {status}</span>
            </div>
        </div>
    );
}
