'use client';

import React, { useState, useEffect } from 'react';
import {
    Table,
    TableBody,
    TableCell,
    TableHead,
    TableHeader,
    TableRow
} from '@/components/ui/table';
import { Button } from '@/components/ui/button';
import {
    Card,
    CardContent,
    CardDescription,
    CardHeader,
    CardTitle
} from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import {
    Dialog,
    DialogContent,
    DialogDescription,
    DialogFooter,
    DialogHeader,
    DialogTitle
} from '@/components/ui/dialog';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { toast } from '@/components/ui/use-toast';
import { formatCurrency } from '@/lib/utils';
import { RotateCcw, TrendingUp, DollarSign } from 'lucide-react';
import { useLanguage } from '@/contexts/language-context';

interface Recovery {
    id: string;
    recovery_type: string;
    claim?: {
        claim_number: string;
        client?: {
            first_name: string;
            last_name: string;
        };
    };
    estimated_amount?: number;
    status: string;
}

export default function RecoveryPipeline() {
    const { t } = useLanguage();
    const [recoveries, setRecoveries] = useState<Recovery[]>([]);
    const [loading, setLoading] = useState(true);
    const [selectedRecovery, setSelectedRecovery] = useState<Recovery | null>(null);
    const [isFinalizeModalOpen, setIsFinalizeModalOpen] = useState(false);
    const [actualAmount, setActualAmount] = useState('');
    const [costs, setCosts] = useState('0');

    const fetchRecoveries = async () => {
        setLoading(true);
        try {
            const res = await fetch('/api/v1/recovery/pending');
            const data = await res.json();
            setRecoveries(data);
        } catch (error) {
            console.error("Failed to fetch recoveries:", error);
        } finally {
            setLoading(false);
        }
    };

    useEffect(() => {
        fetchRecoveries();
    }, []);

    const handleFinalize = (recovery: Recovery) => {
        setSelectedRecovery(recovery);
        setActualAmount(recovery.estimated_amount?.toString() || '');
        setCosts('0');
        setIsFinalizeModalOpen(true);
    };

    const submitFinalize = async () => {
        if (!selectedRecovery) return;
        try {
            const res = await fetch(`/api/v1/recovery/${selectedRecovery.id}/finalize`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({
                    actual_recovered_amount: parseFloat(actualAmount),
                    recovery_costs: parseFloat(costs)
                })
            });

            if (res.ok) {
                toast({
                    title: t('recovery.finalized', 'Recovery Finalized'),
                    description: t('recovery.finalized_desc', `Recovered ${formatCurrency(parseFloat(actualAmount) || 0)} successfully.`),
                });
                setIsFinalizeModalOpen(false);
                fetchRecoveries();
            }
        } catch (error) {
            toast({
                title: t('common.error', 'Error'),
                description: t('recovery.finalize_failed', 'Failed to finalize recovery.'),
                variant: "destructive"
            });
        }
    };

    if (loading) return <div>{t('common.loading', 'Loading...')}</div>;

    return (
        <Card>
            <CardHeader>
                <CardTitle>{t('recovery.title', 'Recovery Pipeline')}</CardTitle>
                <CardDescription>
                    {t('recovery.desc', 'Tracking Subrogation and Salvage cases for revenue recovery.')}
                </CardDescription>
            </CardHeader>
            <CardContent>
                {recoveries.length === 0 ? (
                    <div className="text-center py-6 text-muted-foreground">
                        {t('recovery.no_cases', 'No active recovery cases.')}
                    </div>
                ) : (
                    <Table>
                        <TableHeader>
                            <TableRow>
                                <TableHead>{t('label.type', 'Type')}</TableHead>
                                <TableHead>{t('label.claim', 'Claim #')}</TableHead>
                                <TableHead>{t('label.client', 'Client')}</TableHead>
                                <TableHead>{t('label.estimated', 'Estimated')}</TableHead>
                                <TableHead>{t('label.status', 'Status')}</TableHead>
                                <TableHead className="text-right">{t('common.actions', 'Actions')}</TableHead>
                            </TableRow>
                        </TableHeader>
                        <TableBody>
                            {recoveries.map((rec) => (
                                <TableRow key={rec.id}>
                                    <TableCell>
                                        <Badge variant="secondary" className="capitalize">
                                            {rec.recovery_type}
                                        </Badge>
                                    </TableCell>
                                    <TableCell className="font-medium">{rec.claim?.claim_number}</TableCell>
                                    <TableCell>{rec.claim?.client?.first_name} {rec.claim?.client?.last_name}</TableCell>
                                    <TableCell>{formatCurrency(rec.estimated_amount || 0)}</TableCell>
                                    <TableCell>
                                        <Badge variant="outline" className="capitalize">
                                            {rec.status.replace('_', ' ')}
                                        </Badge>
                                    </TableCell>
                                    <TableCell className="text-right">
                                        <Button
                                            size="sm"
                                            onClick={() => handleFinalize(rec)}
                                            className="bg-blue-600 hover:bg-blue-700"
                                        >
                                            <TrendingUp className="h-4 w-4 mr-1" /> {t('btn.finalize', 'Finalize')}
                                        </Button>
                                    </TableCell>
                                </TableRow>
                            ))}
                        </TableBody>
                    </Table>
                )}
            </CardContent>

            <Dialog open={isFinalizeModalOpen} onOpenChange={setIsFinalizeModalOpen}>
                <DialogContent>
                    <DialogHeader>
                        <DialogTitle>{t('recovery.finalize_title', 'Finalize Claim Recovery')}</DialogTitle>
                        <DialogDescription>
                            {t('recovery.finalize_desc', 'Enter the final amount collected and any associated costs (legal, towing, auction fees).')}
                        </DialogDescription>
                    </DialogHeader>
                    <div className="grid gap-4 py-4">
                        <div className="grid gap-2">
                            <Label htmlFor="actualAmount">{t('recovery.amount_recovered', 'Actual Amount Recovered')}</Label>
                            <Input
                                id="actualAmount"
                                type="number"
                                value={actualAmount}
                                onChange={(e) => setActualAmount(e.target.value)}
                            />
                        </div>
                        <div className="grid gap-2">
                            <Label htmlFor="costs">{t('recovery.recovery_costs', 'Recovery Costs (Fees)')}</Label>
                            <Input
                                id="costs"
                                type="number"
                                value={costs}
                                onChange={(e) => setCosts(e.target.value)}
                            />
                        </div>
                    </div>
                    <DialogFooter>
                        <Button variant="ghost" onClick={() => setIsFinalizeModalOpen(false)}>{t('btn.cancel', 'Cancel')}</Button>
                        <Button onClick={submitFinalize}>{t('recovery.record_btn', 'Record Recovery')}</Button>
                    </DialogFooter>
                </DialogContent>
            </Dialog>
        </Card>
    );
}
