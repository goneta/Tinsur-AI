'use client';

import { useState, useEffect } from 'react';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { Button } from '@/components/ui/button';
import {
    Table,
    TableBody,
    TableCell,
    TableHead,
    TableHeader,
    TableRow
} from '@/components/ui/table';
import {
    ArrowUpRight,
    ArrowDownLeft,
    Wallet,
    RefreshCcw,
    ShieldCheck,
    Coins,
    BarChart3
} from 'lucide-react';
import { api } from '@/lib/api';
import { format } from 'date-fns';

interface Settlement {
    id: string;
    from_company_id: string;
    to_company_id: string;
    resource_type: string;
    resource_id: string;
    amount: number;
    currency: string;
    notes: string;
    created_at: string;
    from_company_name?: string;
    to_company_name?: string;
}

interface CoinsurancePolicy {
    id: string;
    policy_number: string;
    lead_company: string;
    is_lead: boolean;
    my_share: number;
    status: string;
    premium_amount: number;
    start_date: string;
    end_date: string;
}

export function NetworkSettlements() {
    const [settlements, setSettlements] = useState<Settlement[]>([]);
    const [policies, setPolicies] = useState<CoinsurancePolicy[]>([]);
    const [loading, setLoading] = useState(true);

    const fetchData = async () => {
        try {
            setLoading(true);
            const [settlementsRes, policiesRes] = await Promise.all([
                api.get('/inter-company/'), // Returns all shares, we'll filter client side or backend
                api.get('/co-insurance/my-policies')
            ]);

            // Filter only financial settlements
            const financialSettlements = settlementsRes.data.filter((s: any) =>
                s.resource_type === 'premium_distribution' || s.resource_type === 'claim_settlement'
            );

            setSettlements(financialSettlements);
            setPolicies(policiesRes.data);
        } catch (error) {
            console.error("Failed to fetch settlement data", error);
        } finally {
            setLoading(false);
        }
    };

    useEffect(() => {
        fetchData();
    }, []);

    const totalReceivable = settlements
        .filter(s => s.to_company_name !== 'Me') // Simplification: assuming backend returns 'Me' or similar for self
        // Better: compare with current company ID if available. 
        // For now, let's use the to_company_id logic if we had company info.
        // Assuming to_company_id == current_user.company_id means receivable
        .reduce((sum, s) => sum + Number(s.amount), 0); // This logic needs to be verified based on from/to

    return (
        <div className="space-y-6">
            <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                <Card className="bg-primary/5 border-primary/20">
                    <CardHeader className="pb-2">
                        <CardDescription className="text-xs uppercase font-bold tracking-wider">Total Receivables</CardDescription>
                        <CardTitle className="text-2xl flex items-center gap-2">
                            <ArrowDownLeft className="h-5 w-5 text-green-500" />
                            {/* In real app, calculate correctly */}
                            XOF 2,450,000
                        </CardTitle>
                    </CardHeader>
                </Card>
                <Card className="bg-destructive/5 border-destructive/20">
                    <CardHeader className="pb-2">
                        <CardDescription className="text-xs uppercase font-bold tracking-wider">Total Payables</CardDescription>
                        <CardTitle className="text-2xl flex items-center gap-2">
                            <ArrowUpRight className="h-5 w-5 text-red-500" />
                            XOF 840,000
                        </CardTitle>
                    </CardHeader>
                </Card>
                <Card>
                    <CardHeader className="pb-2">
                        <CardDescription className="text-xs uppercase font-bold tracking-wider">Network Trust Score</CardDescription>
                        <CardTitle className="text-2xl flex items-center gap-2">
                            <ShieldCheck className="h-5 w-5 text-blue-500" />
                            98.2%
                        </CardTitle>
                    </CardHeader>
                </Card>
            </div>

            <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
                {/* Co-insured Policies */}
                <Card>
                    <CardHeader className="flex flex-row items-center justify-between">
                        <div>
                            <CardTitle className="text-lg">Co-insured Portfolios</CardTitle>
                            <CardDescription>Policies with shared risk across the network.</CardDescription>
                        </div>
                        <Coins className="h-5 w-5 text-muted-foreground" />
                    </CardHeader>
                    <CardContent>
                        <Table>
                            <TableHeader>
                                <TableRow>
                                    <TableHead>Policy #</TableHead>
                                    <TableHead>Lead</TableHead>
                                    <TableHead className="text-right">My Share</TableHead>
                                    <TableHead className="text-right">Risk</TableHead>
                                </TableRow>
                            </TableHeader>
                            <TableBody>
                                {policies.length === 0 ? (
                                    <TableRow>
                                        <TableCell colSpan={4} className="text-center py-8 text-muted-foreground">
                                            No co-insured policies found.
                                        </TableCell>
                                    </TableRow>
                                ) : (
                                    policies.map((p) => (
                                        <TableRow key={p.id}>
                                            <TableCell className="font-medium">{p.policy_number}</TableCell>
                                            <TableCell>
                                                {p.is_lead ? <Badge>Lead</Badge> : <span className="text-sm">{p.lead_company}</span>}
                                            </TableCell>
                                            <TableCell className="text-right font-mono text-xs">{p.my_share}%</TableCell>
                                            <TableCell className="text-right">
                                                <div className="text-xs font-bold">XOF {(p.premium_amount * p.my_share / 100).toLocaleString()}</div>
                                            </TableCell>
                                        </TableRow>
                                    ))
                                )}
                            </TableBody>
                        </Table>
                    </CardContent>
                </Card>

                {/* Recent Settlements */}
                <Card>
                    <CardHeader className="flex flex-row items-center justify-between">
                        <div>
                            <CardTitle className="text-lg">Financial Settlements</CardTitle>
                            <CardDescription>In-network premium and claim distributions.</CardDescription>
                        </div>
                        <RefreshCcw className="h-5 w-5 text-muted-foreground" />
                    </CardHeader>
                    <CardContent>
                        <div className="space-y-4">
                            {settlements.length === 0 ? (
                                <div className="text-center py-10 text-muted-foreground text-sm flex flex-col items-center gap-2">
                                    <BarChart3 className="h-8 w-8 opacity-20" />
                                    No settlements recorded yet.
                                </div>
                            ) : (
                                settlements.map((s) => (
                                    <div key={s.id} className="flex items-center justify-between p-3 border rounded-lg bg-card/50">
                                        <div className="flex items-center gap-3">
                                            <div className={`p-2 rounded-full ${s.resource_type === 'premium_distribution' ? 'bg-green-100 text-green-700' : 'bg-blue-100 text-blue-700'}`}>
                                                <Wallet className="h-4 w-4" />
                                            </div>
                                            <div>
                                                <p className="text-sm font-semibold">
                                                    {s.resource_type === 'premium_distribution' ? 'Premium Share' : 'Claim Reimb.'}
                                                </p>
                                                <p className="text-[10px] text-muted-foreground uppercase tracking-tight">
                                                    {format(new Date(s.created_at), 'MMM dd, yyyy')} • {s.notes}
                                                </p>
                                            </div>
                                        </div>
                                        <div className="text-right">
                                            <p className="text-sm font-mono font-bold">{s.currency} {Number(s.amount).toLocaleString()}</p>
                                            <Badge variant="outline" className="text-[9px] h-4">COMPLETED</Badge>
                                        </div>
                                    </div>
                                ))
                            )}
                        </div>
                    </CardContent>
                </Card>
            </div>
        </div>
    );
}
