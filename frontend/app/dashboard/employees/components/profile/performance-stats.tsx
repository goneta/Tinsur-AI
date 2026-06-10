'use client';

import { useState, useMemo } from 'react';
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from '@/components/ui/card';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs';
import { BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, LineChart, Line, AreaChart, Area } from 'recharts';
import { DataView } from '@/components/ui/data-view';
import { FilterPeriod } from './advanced-filter';
import { Users, FileText, Shield, AlertTriangle, TrendingUp } from 'lucide-react';

interface PerformanceStatsProps {
    employeeId: string;
    period: FilterPeriod;
    filterValue: any;
}

export function PerformanceStats({ employeeId, period, filterValue }: PerformanceStatsProps) {
    const [activeTab, setActiveTab] = useState('clients');

    // Mock data for counts
    const counts = {
        clients: 10,
        quotes: 8,
        policies: 7,
        claims: 3
    };

    // Mock chart data based on active tab and period
    const chartData = useMemo(() => {
        const dataSets: Record<string, any[]> = {
            clients: [
                { name: 'Jan', value: 4 }, { name: 'Feb', value: 3 }, { name: 'Mar', value: 2 },
                { name: 'Apr', value: 6 }, { name: 'May', value: 8 }, { name: 'Jun', value: 5 },
            ],
            quotes: [
                { name: 'Jan', value: 2 }, { name: 'Feb', value: 5 }, { name: 'Mar', value: 3 },
                { name: 'Apr', value: 4 }, { name: 'May', value: 3 }, { name: 'Jun', value: 7 },
            ].map((d, idx) => ({ ...d, value: d.value + (idx % 3) })),
            policies: [
                { name: 'Jan', value: 3 }, { name: 'Feb', value: 2 }, { name: 'Mar', value: 5 },
                { name: 'Apr', value: 4 }, { name: 'May', value: 6 }, { name: 'Jun', value: 8 },
            ],
            claims: [
                { name: 'Jan', value: 1 }, { name: 'Feb', value: 0 }, { name: 'Mar', value: 2 },
                { name: 'Apr', value: 1 }, { name: 'May', value: 2 }, { name: 'Jun', value: 1 },
            ]
        };
        return dataSets[activeTab] || dataSets.clients;
    }, [activeTab, period, filterValue]);

    // Mock list data for each tab
    const mockClients = Array.from({ length: counts.clients }).map((_, i) => ({
        id: `c-${i}`,
        first_name: `Client`,
        last_name: `${i + 1}`,
        email: `client${i + 1}@example.com`,
        phone: `+225 010203${i}0`,
        status: 'active',
        client_type: 'individual'
    }));

    const mockQuotes = Array.from({ length: counts.quotes }).map((_, i) => ({
        id: `q-${i}`,
        quote_number: `QT-2023-${100 + i}`,
        client_name: `Client ${i + 1}`,
        amount: 250000 + (i * 10000),
        status: 'pending'
    }));

    const mockPolicies = Array.from({ length: counts.policies }).map((_, i) => ({
        id: `p-${i}`,
        policy_number: `POL-99${i}88`,
        client_name: `Client ${i + 1}`,
        premium: 50000 + (i * 5000),
        status: 'active'
    }));

    const mockClaims = Array.from({ length: counts.claims }).map((_, i) => ({
        id: `cl-${i}`,
        claim_number: `CLM-10${i}2`,
        policy_number: `POL-99${i}88`,
        amount: 120000,
        status: 'pending'
    }));

    // Columns for DataView
    const clientColumns = [
        { accessorKey: 'id', header: 'ID' },
        { accessorKey: 'first_name', header: 'First Name' },
        { accessorKey: 'last_name', header: 'Last Name' },
        { accessorKey: 'email', header: 'Email' },
        { accessorKey: 'status', header: 'Status' }
    ];

    const policyColumns = [
        { accessorKey: 'policy_number', header: 'Policy #' },
        { accessorKey: 'client_name', header: 'Client' },
        { accessorKey: 'premium', header: 'Premium' },
        { accessorKey: 'status', header: 'Status' }
    ];

    const claimColumns = [
        { accessorKey: 'claim_number', header: 'Claim #' },
        { accessorKey: 'policy_number', header: 'Policy #' },
        { accessorKey: 'amount', header: 'Amount' },
        { accessorKey: 'status', header: 'Status' }
    ];

    const quoteColumns = [
        { accessorKey: 'quote_number', header: 'Quote #' },
        { accessorKey: 'client_name', header: 'Client' },
        { accessorKey: 'amount', header: 'Amount' },
        { accessorKey: 'status', header: 'Status' }
    ];

    const renderCard = (item: any) => (
        <Card className="p-4 border-l-4 border-l-primary hover:bg-slate-50 transition-colors">
            <div className="font-bold">{item.first_name || item.quote_number || item.policy_number || item.claim_number} {item.last_name || ''}</div>
            <div className="text-sm text-muted-foreground">{item.email || item.client_name || `Ref: ${item.policy_number || 'N/A'}`}</div>
            <div className="mt-2 flex items-center justify-between">
                <span className="text-xs font-medium uppercase text-primary bg-primary/10 px-2 py-0.5 rounded">{item.status}</span>
                {item.amount && <span className="text-sm font-bold text-slate-700">{new Intl.NumberFormat('fr-FR', { style: 'currency', currency: 'XOF' }).format(item.amount)}</span>}
                {item.premium && <span className="text-sm font-bold text-slate-700">{new Intl.NumberFormat('fr-FR', { style: 'currency', currency: 'XOF' }).format(item.premium)}</span>}
            </div>
        </Card>
    );

    return (
        <Card className="w-full shadow-sm">
            <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-7">
                <div className="space-y-1">
                    <CardTitle className="text-2xl font-bold flex items-center gap-2">
                        <TrendingUp className="h-6 w-6 text-primary" />
                        Performance Statistics
                    </CardTitle>
                    <CardDescription>
                        Records created by this employee.
                    </CardDescription>
                </div>
            </CardHeader>
            <CardContent>
                <Tabs defaultValue="clients" className="space-y-6" onValueChange={setActiveTab}>
                    <TabsList className="grid w-full grid-cols-4 h-auto p-1 bg-muted/50">
                        <TabsTrigger value="clients" className="py-3 flex flex-col gap-1">
                            <Users className="h-4 w-4" />
                            <span className="text-xs font-semibold">Clients ({counts.clients})</span>
                        </TabsTrigger>
                        <TabsTrigger value="quotes" className="py-3 flex flex-col gap-1">
                            <FileText className="h-4 w-4" />
                            <span className="text-xs font-semibold">Quotes ({counts.quotes})</span>
                        </TabsTrigger>
                        <TabsTrigger value="policies" className="py-3 flex flex-col gap-1">
                            <Shield className="h-4 w-4" />
                            <span className="text-xs font-semibold">Policies ({counts.policies})</span>
                        </TabsTrigger>
                        <TabsTrigger value="claims" className="py-3 flex flex-col gap-1">
                            <AlertTriangle className="h-4 w-4" />
                            <span className="text-xs font-semibold">Claims ({counts.claims})</span>
                        </TabsTrigger>
                    </TabsList>

                    {/* Chart Section */}
                    <div className="bg-white p-6 rounded-xl border shadow-sm">
                        <div className="flex items-center justify-between mb-4">
                            <h4 className="text-sm font-bold uppercase tracking-wider text-muted-foreground">Activity Trend</h4>
                            <div className="text-xs text-muted-foreground">Updated for {period} selection</div>
                        </div>
                        <div className="h-[250px] w-full">
                            <ResponsiveContainer width="100%" height="100%">
                                {activeTab === 'clients' ? (
                                    <AreaChart data={chartData}>
                                        <defs>
                                            <linearGradient id="colorValue" x1="0" y1="0" x2="0" y2="1">
                                                <stop offset="5%" stopColor="#2563eb" stopOpacity={0.3} />
                                                <stop offset="95%" stopColor="#2563eb" stopOpacity={0} />
                                            </linearGradient>
                                        </defs>
                                        <CartesianGrid strokeDasharray="3 3" vertical={false} stroke="#f0f0f0" />
                                        <XAxis dataKey="name" axisLine={false} tickLine={false} tick={{ fontSize: 12, fill: '#666' }} />
                                        <YAxis axisLine={false} tickLine={false} tick={{ fontSize: 12, fill: '#666' }} />
                                        <Tooltip
                                            contentStyle={{ borderRadius: '8px', border: 'none', boxShadow: '0 4px 12px rgba(0,0,0,0.1)' }}
                                        />
                                        <Area type="monotone" dataKey="value" stroke="#2563eb" strokeWidth={3} fillOpacity={1} fill="url(#colorValue)" />
                                    </AreaChart>
                                ) : (
                                    <BarChart data={chartData}>
                                        <CartesianGrid strokeDasharray="3 3" vertical={false} stroke="#f0f0f0" />
                                        <XAxis dataKey="name" axisLine={false} tickLine={false} tick={{ fontSize: 12, fill: '#666' }} />
                                        <YAxis axisLine={false} tickLine={false} tick={{ fontSize: 12, fill: '#666' }} />
                                        <Tooltip
                                            contentStyle={{ borderRadius: '8px', border: 'none', boxShadow: '0 4px 12px rgba(0,0,0,0.1)' }}
                                            cursor={{ fill: '#f8fafc' }}
                                        />
                                        <Bar dataKey="value" fill="#2563eb" radius={[4, 4, 0, 0]} />
                                    </BarChart>
                                )}
                            </ResponsiveContainer>
                        </div>
                    </div>

                    {/* List Section */}
                    <div className="space-y-4">
                        <div className="flex items-center gap-2">
                            <h4 className="text-lg font-semibold capitalize text-slate-900 leading-none">{activeTab} Details</h4>
                            <div className="h-px flex-1 bg-slate-100" />
                        </div>

                        <TabsContent value="clients" className="m-0 focus-visible:ring-0">
                            <DataView
                                columns={clientColumns as any}
                                data={mockClients}
                                renderCard={renderCard}
                                defaultView="list"
                            />
                        </TabsContent>

                        <TabsContent value="quotes" className="m-0 focus-visible:ring-0">
                            <DataView
                                columns={quoteColumns as any}
                                data={mockQuotes}
                                renderCard={renderCard}
                                defaultView="list"
                            />
                        </TabsContent>

                        <TabsContent value="policies" className="m-0 focus-visible:ring-0">
                            <DataView
                                columns={policyColumns as any}
                                data={mockPolicies}
                                renderCard={renderCard}
                                defaultView="list"
                            />
                        </TabsContent>

                        <TabsContent value="claims" className="m-0 focus-visible:ring-0">
                            <DataView
                                columns={claimColumns as any}
                                data={mockClaims}
                                renderCard={renderCard}
                                defaultView="list"
                            />
                        </TabsContent>
                    </div>
                </Tabs>
            </CardContent>
        </Card>
    );
}
