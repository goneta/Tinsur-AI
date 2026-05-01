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
import { Textarea } from '@/components/ui/textarea';
import { toast } from '@/components/ui/use-toast';
import { formatCurrency } from '@/lib/utils';
import { ShieldAlert, CheckCircle2, XCircle } from 'lucide-react';
import { useLanguage } from '@/contexts/language-context';

interface Referral {
    id: string;
    quote: {
        quote_number: string;
        client: {
            first_name: string;
            last_name: string;
        };
        coverage_amount: number;
    };
    referrer: {
        first_name: string;
        last_name: string;
    };
    reason: string;
}

export default function UnderwritingApprovals() {
    const { t } = useLanguage();
    const [referrals, setReferrals] = useState<Referral[]>([]);
    const [loading, setLoading] = useState(true);
    const [selectedReferral, setSelectedReferral] = useState<Referral | null>(null);
    const [decisionNote, setDecisionNote] = useState('');
    const [isDecisionModalOpen, setIsDecisionModalOpen] = useState(false);
    const [decisionType, setDecisionType] = useState<'approved' | 'rejected' | null>(null);

    const fetchReferrals = async () => {
        setLoading(true);
        try {
            const res = await fetch('/api/v1/underwriting/referrals/pending');
            const data = await res.json();
            setReferrals(data);
        } catch (error) {
            console.error("Failed to fetch referrals:", error);
        } finally {
            setLoading(false);
        }
    };

    useEffect(() => {
        fetchReferrals();
    }, []);

    const handleAction = (referral: Referral, type: 'approved' | 'rejected') => {
        setSelectedReferral(referral);
        setDecisionType(type);
        setDecisionNote('');
        setIsDecisionModalOpen(true);
    };

    const submitDecision = async () => {
        if (!decisionNote.trim()) {
            toast({
                title: t('common.error', 'Error'),
                description: t('underwriting.decision_notes_required', 'Please provide decision notes.'),
                variant: "destructive"
            });
            return;
        }

        if (!selectedReferral) return;

        try {
            const res = await fetch(`/api/v1/underwriting/referrals/${selectedReferral.id}/decide`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({
                    status: decisionType,
                    decision_notes: decisionNote
                })
            });

            if (res.ok) {
                toast({
                    title: decisionType === 'approved' ? t('underwriting.referral_approved', 'Referral Approved') : t('underwriting.referral_rejected', 'Referral Rejected'),
                    description: t('underwriting.decision_processed', `The quote has been updated to ${decisionType === 'approved' ? t('status.accepted', 'Accepted') : t('status.rejected', 'Rejected')}.`),
                });
                setIsDecisionModalOpen(false);
                fetchReferrals();
            }
        } catch (error) {
            toast({
                title: t('common.error', 'Error'),
                description: t('underwriting.decision_failed', 'Failed to process decision.'),
                variant: "destructive"
            });
        }
    };

    if (loading) return <div>{t('common.loading', 'Loading...')}</div>;

    return (
        <Card>
            <CardHeader>
                <CardTitle>{t('underwriting.title', 'Quotes Awaiting Approval')}</CardTitle>
                <CardDescription>
                    {t('underwriting.desc', 'These cases exceed agent authority limits or have high-risk flags.')}
                </CardDescription>
            </CardHeader>
            <CardContent>
                {referrals.length === 0 ? (
                    <div className="text-center py-6 text-muted-foreground">
                        {t('underwriting.no_pending', 'No pending approvals in the queue.')}
                    </div>
                ) : (
                    <Table>
                        <TableHeader>
                            <TableRow>
                                <TableHead>{t('label.quote', 'Quote #')}</TableHead>
                                <TableHead>{t('label.client', 'Client')}</TableHead>
                                <TableHead>{t('label.coverage', 'Coverage')}</TableHead>
                                <TableHead>{t('underwriting.referred_by', 'Referred By')}</TableHead>
                                <TableHead>{t('label.reason', 'Reason')}</TableHead>
                                <TableHead className="text-right">{t('common.actions', 'Actions')}</TableHead>
                            </TableRow>
                        </TableHeader>
                        <TableBody>
                            {referrals.map((ref) => (
                                <TableRow key={ref.id}>
                                    <TableCell className="font-medium">{ref.quote?.quote_number}</TableCell>
                                    <TableCell>{ref.quote?.client?.first_name} {ref.quote?.client?.last_name}</TableCell>
                                    <TableCell>{formatCurrency(ref.quote?.coverage_amount || 0)}</TableCell>
                                    <TableCell>{ref.referrer?.first_name} {ref.referrer?.last_name}</TableCell>
                                    <TableCell>
                                        <Badge variant="outline" className="text-amber-600 border-amber-200 bg-amber-50">
                                            {ref.reason}
                                        </Badge>
                                    </TableCell>
                                    <TableCell className="text-right space-x-2">
                                        <Button
                                            size="sm"
                                            variant="outline"
                                            className="text-green-600 border-green-200 hover:bg-green-50"
                                            onClick={() => handleAction(ref, 'approved')}
                                        >
                                            <CheckCircle2 className="h-4 w-4 mr-1" /> {t('btn.approve', 'Approve')}
                                        </Button>
                                        <Button
                                            size="sm"
                                            variant="outline"
                                            className="text-red-600 border-red-200 hover:bg-red-50"
                                            onClick={() => handleAction(ref, 'rejected')}
                                        >
                                            <XCircle className="h-4 w-4 mr-1" /> {t('btn.reject', 'Reject')}
                                        </Button>
                                    </TableCell>
                                </TableRow>
                            ))}
                        </TableBody>
                    </Table>
                )}
            </CardContent>

            <Dialog open={isDecisionModalOpen} onOpenChange={setIsDecisionModalOpen}>
                <DialogContent>
                    <DialogHeader>
                        <DialogTitle>{decisionType === 'approved' ? t('btn.approve', 'Approve') : t('btn.reject', 'Reject')} {t('underwriting.referral_title', 'Underwriting Referral')}</DialogTitle>
                        <DialogDescription>
                            {t('underwriting.decision_desc', 'Please provide justification for your decision. This will be sent to the referring agent and client.')}
                        </DialogDescription>
                    </DialogHeader>
                    <div className="py-4">
                        <Textarea
                            placeholder={t('underwriting.notes_placeholder', 'Decision notes...')}
                            value={decisionNote}
                            onChange={(e) => setDecisionNote(e.target.value)}
                            className="min-h-[100px]"
                        />
                    </div>
                    <DialogFooter>
                        <Button variant="ghost" onClick={() => setIsDecisionModalOpen(false)}>{t('btn.cancel', 'Cancel')}</Button>
                        <Button
                            className={decisionType === 'approved' ? 'bg-green-600 hover:bg-green-700' : 'bg-red-600 hover:bg-red-700'}
                            onClick={submitDecision}
                        >
                            {t('common.confirm', 'Confirm')} {decisionType === 'approved' ? t('status.approved', 'Approval') : t('status.rejected', 'Rejection')}
                        </Button>
                    </DialogFooter>
                </DialogContent>
            </Dialog>
        </Card>
    );
}
