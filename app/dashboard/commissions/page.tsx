"use client";

import { useState, useEffect } from "react";
import { Coins, Filter, CheckCircle2, Clock } from "lucide-react";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from "@/components/ui/card";
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from "@/components/ui/table";
import { Badge } from "@/components/ui/badge";
import { useToast } from "@/components/ui/use-toast";
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select";

interface Commission {
    id: string;
    amount: number;
    status: string;
    policy_id: string;
    agent_id: string;
    created_at: string;
    paid_at?: string;
}

import { useLanguage } from '@/contexts/language-context';

/* ... imports */

export default function CommissionsPage() {
    const { t } = useLanguage();
    /* ... state variables ... */
    const [commissions, setCommissions] = useState<Commission[]>([]);
    const [loading, setLoading] = useState(true);
    const [statusFilter, setStatusFilter] = useState<string>("all");
    const { toast } = useToast();

    useEffect(() => {
        fetchCommissions();
    }, [statusFilter]);

    /* ... fetch function and helpers ... */
    const fetchCommissions = async () => {
        /* ... fetch logic ... */
        setLoading(true);
        try {
            let url = "/api/v1/commissions/";
            if (statusFilter !== "all") {
                url += `?status=${statusFilter}`;
            }
            const response = await fetch(url, {
                headers: {
                    Authorization: `Bearer ${localStorage.getItem("token")}`,
                },
            });
            if (response.ok) {
                const data = await response.json();
                setCommissions(data);
            }
        } catch (error) {
            toast({
                title: t('common.error'),
                description: t('commissions.load_error'),
                variant: "destructive",
            });
        } finally {
            setLoading(false);
        }
    };

    const formatMoney = (amount: number) => {
        return new Intl.NumberFormat('fr-CI', { style: 'currency', currency: 'XOF' }).format(amount);
    };

    const totalEarned = commissions.reduce((acc, curr) => acc + curr.amount, 0);
    const pendingAmount = commissions.filter(c => c.status === 'pending').reduce((acc, curr) => acc + curr.amount, 0);

    return (
        <div className="space-y-6">
            <div className="flex justify-between items-center">
                <div>
                    <h2 className="text-3xl font-bold tracking-tight">{t('commissions.title')}</h2>
                    <p className="text-muted-foreground">{t('commissions.desc')}</p>
                </div>
                <div className="flex items-center gap-4">
                    <Select value={statusFilter} onValueChange={setStatusFilter}>
                        <SelectTrigger className="w-[180px]">
                            <Filter className="mr-2 h-4 w-4" />
                            <SelectValue placeholder={t('commissions.filter_placeholder')} />
                        </SelectTrigger>
                        <SelectContent>
                            <SelectItem value="all">{t('commissions.filter_all')}</SelectItem>
                            <SelectItem value="pending">{t('commissions.filter_pending')}</SelectItem>
                            <SelectItem value="paid">{t('commissions.filter_paid')}</SelectItem>
                        </SelectContent>
                    </Select>
                </div>
            </div>

            <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-3">
                <Card>
                    <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
                        <CardTitle className="text-sm font-medium text-slate-500 uppercase">{t('commissions.total_tracked')}</CardTitle>
                        <Coins className="h-4 w-4 text-primary" />
                    </CardHeader>
                    <CardContent>
                        <div className="text-2xl font-bold">{formatMoney(totalEarned)}</div>
                    </CardContent>
                </Card>
                <Card>
                    <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
                        <CardTitle className="text-sm font-medium text-slate-500 uppercase">{t('commissions.pending_payment')}</CardTitle>
                        <Clock className="h-4 w-4 text-orange-500" />
                    </CardHeader>
                    <CardContent>
                        <div className="text-2xl font-bold">{formatMoney(pendingAmount)}</div>
                    </CardContent>
                </Card>
            </div>

            <Card>
                <CardHeader>
                    <CardTitle>{t('commissions.records_title')}</CardTitle>
                </CardHeader>
                <CardContent>
                    <Table>
                        <TableHeader>
                            <TableRow>
                                <TableHead>{t('commissions.date')}</TableHead>
                                <TableHead>{t('commissions.amount')}</TableHead>
                                <TableHead>{t('commissions.status')}</TableHead>
                                <TableHead>{t('commissions.policy_ref')}</TableHead>
                            </TableRow>
                        </TableHeader>
                        <TableBody>
                            {loading ? (
                                <TableRow><TableCell colSpan={4} className="text-center">{t('commissions.loading')}</TableCell></TableRow>
                            ) : commissions.length === 0 ? (
                                <TableRow><TableCell colSpan={4} className="text-center">{t('commissions.no_records')}</TableCell></TableRow>
                            ) : (
                                commissions.map((c) => (
                                    <TableRow key={c.id}>
                                        <TableCell>{new Date(c.created_at).toLocaleDateString()}</TableCell>
                                        <TableCell className="font-bold">{formatMoney(c.amount)}</TableCell>
                                        <TableCell>
                                            <Badge variant={c.status === 'paid' ? 'default' : 'secondary'} className="gap-1">
                                                {c.status === 'paid' ? <CheckCircle2 className="h-3 w-3" /> : <Clock className="h-3 w-3" />}
                                                {c.status.toUpperCase()}
                                            </Badge>
                                        </TableCell>
                                        <TableCell className="text-xs font-mono">{c.policy_id}</TableCell>
                                    </TableRow>
                                ))
                            )}
                        </TableBody>
                    </Table>
                </CardContent>
            </Card>
        </div>
    );
}
