'use client';

import { useState } from 'react';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import { Label } from '@/components/ui/label';
import { Textarea } from '@/components/ui/textarea';
import { ShieldCheck, ShieldAlert, ShieldQuestion, CheckCircle2, XCircle, Clock, Info } from 'lucide-react';
import { Client } from '@/types/client';
import { clientApi } from '@/lib/client-api';
import { useToast } from '@/components/ui/use-toast';

interface IdVerificationCardProps {
    client: Client;
    onStatusUpdate: () => void;
}

export function IdVerificationCard({ client, onStatusUpdate }: IdVerificationCardProps) {
    const [isUpdating, setIsUpdating] = useState(false);
    const [notes, setNotes] = useState(client.kyc_notes || '');
    const { toast } = useToast();

    const updateStatus = async (status: 'verified' | 'rejected') => {
        setIsUpdating(true);
        try {
            await clientApi.updateKycStatus(client.id, status, notes, client.kyc_results);
            toast({
                title: `Client ${status === 'verified' ? 'Verified' : 'Rejected'}`,
                description: `Verification status updated successfully.`,
            });
            onStatusUpdate();
        } catch (error) {
            toast({
                title: 'Error',
                description: 'Failed to update KYC status.',
                variant: 'destructive',
            });
        } finally {
            setIsUpdating(false);
        }
    };

    const StatusIcon = () => {
        if (client.kyc_status === 'verified') return <ShieldCheck className="h-5 w-5 text-green-600" />;
        if (client.kyc_status === 'rejected') return <ShieldAlert className="h-5 w-5 text-red-600" />;
        return <ShieldQuestion className="h-5 w-5 text-yellow-600" />;
    };

    const StatusBadge = () => {
        if (client.kyc_status === 'verified') return <Badge className="bg-green-500 hover:bg-green-600">Verified</Badge>;
        if (client.kyc_status === 'rejected') return <Badge variant="destructive">Rejected</Badge>;
        return <Badge variant="outline" className="text-yellow-700 border-yellow-200 bg-yellow-50">Pending Review</Badge>;
    };

    return (
        <Card className="border-slate-200 shadow-sm overflow-hidden">
            <CardHeader className="bg-slate-50/50 border-b pb-4">
                <div className="flex items-center justify-between">
                    <div className="flex items-center gap-2">
                        <StatusIcon />
                        <div>
                            <CardTitle className="text-lg">Identity Verification</CardTitle>
                            <CardDescription>powered by Google Gemini Vision</CardDescription>
                        </div>
                    </div>
                    <StatusBadge />
                </div>
            </CardHeader>
            <CardContent className="pt-6 space-y-6">
                {/* OCR Results Grid */}
                {client.kyc_results ? (
                    <div className="grid grid-cols-2 gap-4 bg-slate-50 p-4 rounded-lg border border-slate-100">
                        <div className="space-y-1">
                            <Label className="text-[10px] uppercase text-slate-500 font-bold">Extracted Name</Label>
                            <div className="text-sm font-semibold">{client.kyc_results.full_name || '-'}</div>
                        </div>
                        <div className="space-y-1">
                            <Label className="text-[10px] uppercase text-slate-500 font-bold">Document Number</Label>
                            <div className="text-sm font-semibold">{client.kyc_results.id_number || '-'}</div>
                        </div>
                        <div className="space-y-1">
                            <Label className="text-[10px] uppercase text-slate-500 font-bold">Date of Birth</Label>
                            <div className="text-sm font-semibold">{client.kyc_results.dob || '-'}</div>
                        </div>
                        <div className="space-y-1">
                            <Label className="text-[10px] uppercase text-slate-500 font-bold">Expiry Date</Label>
                            <div className={`text-sm font-semibold ${client.kyc_results.is_expired ? 'text-red-600' : 'text-slate-900'}`}>
                                {client.kyc_results.expiry_date || '-'}
                                {client.kyc_results.is_expired && <span className="ml-2 text-[10px] font-bold">(EXPIRED)</span>}
                            </div>
                        </div>
                    </div>
                ) : (
                    <div className="flex flex-col items-center justify-center py-6 text-slate-400 bg-slate-50/50 rounded-lg border border-dashed border-slate-200">
                        <Info className="h-8 w-8 mb-2 opacity-50" />
                        <p className="text-sm">No AI scan results available.</p>
                    </div>
                )}

                {/* Review Notes */}
                <div className="space-y-2">
                    <Label className="text-xs font-bold text-slate-700">Verification Notes</Label>
                    <Textarea
                        placeholder="Add internal notes about this verification..."
                        value={notes}
                        onChange={(e) => setNotes(e.target.value)}
                        className="text-sm min-h-[80px] bg-white"
                    />
                </div>

                {/* Actions */}
                <div className="flex gap-3 pt-2">
                    <Button
                        onClick={() => updateStatus('verified')}
                        disabled={isUpdating || client.kyc_status === 'verified'}
                        className="flex-1 bg-green-600 hover:bg-green-700 text-white"
                    >
                        <CheckCircle2 className="h-4 w-4 mr-2" /> Approve
                    </Button>
                    <Button
                        variant="outline"
                        onClick={() => updateStatus('rejected')}
                        disabled={isUpdating || client.kyc_status === 'rejected'}
                        className="flex-1 border-red-200 text-red-700 hover:bg-red-50 hover:text-red-800"
                    >
                        <XCircle className="h-4 w-4 mr-2" /> Reject
                    </Button>
                </div>
            </CardContent>
        </Card>
    );
}
