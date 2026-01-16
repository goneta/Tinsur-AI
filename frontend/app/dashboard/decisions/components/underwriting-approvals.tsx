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
                title: "Error",
                description: "Please provide decision notes.",
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
                    title: decisionType === 'approved' ? "Referral Approved" : "Referral Rejected",
                    description: `The quote has been updated to ${decisionType === 'approved' ? 'Accepted' : 'Rejected'}.`,
                });
                setIsDecisionModalOpen(false);
                fetchReferrals();
            }
        } catch (error) {
            toast({
                title: "Error",
                description: "Failed to process decision.",
                variant: "destructive"
            });
        }
    };

    if (loading) return <div>Loading approvals...</div>;

    return (
        <Card>
            <CardHeader>
                <CardTitle>Quotes Awaiting Approval</CardTitle>
                <CardDescription>
                    These cases exceed agent authority limits or have high-risk flags.
                </CardDescription>
            </CardHeader>
            <CardContent>
                {referrals.length === 0 ? (
                    <div className="text-center py-6 text-muted-foreground">
                        No pending approvals in the queue.
                    </div>
                ) : (
                    <Table>
                        <TableHeader>
                            <TableRow>
                                <TableHead>Quote #</TableHead>
                                <TableHead>Client</TableHead>
                                <TableHead>Coverage</TableHead>
                                <TableHead>Referred By</TableHead>
                                <TableHead>Reason</TableHead>
                                <TableHead className="text-right">Actions</TableHead>
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
                                            <CheckCircle2 className="h-4 w-4 mr-1" /> Approve
                                        </Button>
                                        <Button
                                            size="sm"
                                            variant="outline"
                                            className="text-red-600 border-red-200 hover:bg-red-50"
                                            onClick={() => handleAction(ref, 'rejected')}
                                        >
                                            <XCircle className="h-4 w-4 mr-1" /> Reject
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
                        <DialogTitle>{decisionType === 'approved' ? 'Approve' : 'Reject'} Underwriting Referral</DialogTitle>
                        <DialogDescription>
                            Please provide justification for your decision.
                            This will be sent to the referring agent and client.
                        </DialogDescription>
                    </DialogHeader>
                    <div className="py-4">
                        <Textarea
                            placeholder="Decision notes..."
                            value={decisionNote}
                            onChange={(e) => setDecisionNote(e.target.value)}
                            className="min-h-[100px]"
                        />
                    </div>
                    <DialogFooter>
                        <Button variant="ghost" onClick={() => setIsDecisionModalOpen(false)}>Cancel</Button>
                        <Button
                            className={decisionType === 'approved' ? 'bg-green-600 hover:bg-green-700' : 'bg-red-600 hover:bg-red-700'}
                            onClick={submitDecision}
                        >
                            Confirm {decisionType === 'approved' ? 'Approval' : 'Rejection'}
                        </Button>
                    </DialogFooter>
                </DialogContent>
            </Dialog>
        </Card>
    );
}
