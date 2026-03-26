'use client';

import { useEffect, useState, use } from 'react';
import { useRouter } from 'next/navigation';
import { format } from 'date-fns';
import {
    ArrowLeft,
    Printer,
    Edit,
    CreditCard,
    Download,
    FileText,
    CheckCircle2,
    XCircle,
    AlertCircle,
    Clock,
    Bot,
    QrCode,
    Users,
    Loader2
} from 'lucide-react';
import { useLanguage } from '@/contexts/language-context';

import { policyApi } from '@/lib/policy-api';
import { paymentApi } from '@/lib/payment-api';
import { coInsuranceApi } from '@/lib/co-insurance-api';
import { AiAPI } from '@/lib/ai-api';
import { Policy } from '@/types/policy';
import { Payment } from '@/types/payment';
import { CoInsuranceShare } from '@/types/co-insurance';
import { Button } from '@/components/ui/button';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { Separator } from '@/components/ui/separator';
import { Dialog, DialogContent, DialogFooter, DialogHeader, DialogTitle } from '@/components/ui/dialog';
import { Textarea } from '@/components/ui/textarea';
import {
    Table,
    TableBody,
    TableCell,
    TableHead,
    TableHeader,
    TableRow,
} from '@/components/ui/table';
import { formatCurrency, formatDate } from '@/lib/utils';
import { PolicyFormDialog } from '@/components/policies/policy-form-dialog';
import { CoInsuranceModal } from '@/components/policies/co-insurance-modal';
import { PaymentScheduleView } from '@/components/policies/payment-schedule-view';
import { PolicyAgreementView } from '@/components/policies/policy-agreement-view';
import { CancellationWorkflow } from '@/components/policies/cancellation-workflow';
import { clientApi } from '@/lib/client-api';
import { Client } from '@/types/client';

export default function PolicyDetailsPage({ params }: { params: Promise<{ id: string }> }) {
    const router = useRouter();
    const resolvedParams = use(params);
    const { t } = useLanguage();
    const [policy, setPolicy] = useState<Policy | null>(null);
    const [client, setClient] = useState<Client | null>(null);
    const [payments, setPayments] = useState<Payment[]>([]);
    const [shares, setShares] = useState<CoInsuranceShare[]>([]);
    const [loading, setLoading] = useState(true);
    const [isEditOpen, setIsEditOpen] = useState(false);
    const [isCoInsuranceOpen, setIsCoInsuranceOpen] = useState(false);
    const [showAgreement, setShowAgreement] = useState(false);

    const [isClaimOpen, setIsClaimOpen] = useState(false);
    const [claimDescription, setClaimDescription] = useState('');
    const [isSubmittingClaim, setIsSubmittingClaim] = useState(false);
    const [isMounted, setIsMounted] = useState(false);
    const [aiResponse, setAiResponse] = useState('');
    const [isGenerating, setIsGenerating] = useState(false);
    const [showSchedule, setShowSchedule] = useState(false);
    const [isCancellationOpen, setIsCancellationOpen] = useState(false);

    useEffect(() => {
        setIsMounted(true);
    }, []);

    const loadData = async () => {
        try {
            const [policyData, paymentsData, sharesData] = await Promise.all([
                policyApi.getPolicy(resolvedParams.id),
                paymentApi.getPaymentsByPolicy(resolvedParams.id),
                coInsuranceApi.getShares(resolvedParams.id)
            ]);
            setPolicy(policyData);
            setPayments(paymentsData);
            setShares(sharesData);

            // Fetch client details if we have the policy
            if (policyData && policyData.client_id) {
                const clientData = await clientApi.getClient(policyData.client_id);
                setClient(clientData);
            }
        } catch (error) {
            console.error('Failed to load details:', error);
        } finally {
            setLoading(false);
        }
    };

    useEffect(() => {
        loadData();
    }, [resolvedParams.id]);

    const handlePolicyUpdated = () => {
        setIsEditOpen(false);
        loadData();
    };

    const handleFileClaim = async () => {
        if (!policy || !claimDescription) return;

        setIsSubmittingClaim(true);
        setAiResponse('');
        try {
            const result = await AiAPI.chat(claimDescription, [], policy.id);
            setAiResponse(result.response);
            setClaimDescription('');
        } catch (error) {
            console.error(error);
            setAiResponse("Failed to process claim. Please try again.");
        } finally {
            setIsSubmittingClaim(false);
        }
    };

    const handleGenerateSchedule = async () => {
        setShowSchedule(true);
    };

    if (loading || !isMounted) return <div className="p-8">{t('Loading...')}</div>;
    if (!policy) return <div className="p-8">{t('Policy not found')}</div>;

    const getStatusBadge = (status: string) => {
        switch (status) {
            case 'active':
                return <Badge className="bg-green-500 hover:bg-green-600"><CheckCircle2 className="w-3 h-3 mr-1" /> {t('Active')}</Badge>;
            case 'expired':
                return <Badge variant="secondary"><Clock className="w-3 h-3 mr-1" /> {t('Expired')}</Badge>;
            case 'canceled':
                return <Badge variant="destructive"><XCircle className="w-3 h-3 mr-1" /> {t('Canceled')}</Badge>;
            case 'lapsed':
                return <Badge variant="destructive" className="bg-orange-500"><AlertCircle className="w-3 h-3 mr-1" /> {t('Lapsed')}</Badge>;
            default:
                return <Badge variant="outline">{status}</Badge>;
        }
    };

    const getPaymentStatusBadge = (status: string) => {
        const style = status === 'completed' ? 'bg-green-600 hover:bg-green-700' : '';
        return <Badge variant={status === 'completed' ? 'default' : 'secondary'} className={style}>{status}</Badge>;
    };

    if (showSchedule && policy && client) {
        return (
            <div className="p-8 pt-6">
                <PaymentScheduleView
                    policy={policy}
                    client={client}
                    onBack={() => setShowSchedule(false)}
                />
            </div>
        );
    }

    if (showAgreement && policy && client) {
        return (
            <div className="p-8 pt-6">
                <PolicyAgreementView
                    policy={policy}
                    client={client}
                    onBack={() => setShowAgreement(false)}
                />
            </div>
        );
    }

    return (
        <div className="space-y-6 p-8 pt-6">
            {/* Header */}
            <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
                <div className="flex items-center space-x-2">
                    <Button variant="ghost" size="icon" onClick={() => router.back()}>
                        <ArrowLeft className="h-4 w-4" />
                    </Button>
                    <div>
                        <h2 className="text-3xl font-bold tracking-tight">{policy.policy_number}</h2>
                        <p className="text-muted-foreground">{t('Policy Details & History')}</p>
                    </div>
                </div>
                <div className="flex flex-wrap items-center gap-2">
                    <Button variant="outline" onClick={() => window.print()}>
                        <Printer className="mr-2 h-4 w-4" />
                        {t('Print')}
                    </Button>
                    <Button variant="outline" onClick={() => setIsEditOpen(true)}>
                        <Edit className="mr-2 h-4 w-4" />
                        {t('Edit')}
                    </Button>
                    {isMounted && policy && policy.status === 'active' && (
                        <Button
                            variant="destructive"
                            onClick={() => setIsCancellationOpen(true)}
                            className="bg-red-50 text-red-600 hover:bg-red-100 border border-red-200"
                        >
                            <XCircle className="mr-2 h-4 w-4" />
                            {t('Cancel Policy')}
                        </Button>
                    )}
                    <Button
                        onClick={() => setIsClaimOpen(true)}
                        className="bg-purple-600 hover:bg-purple-700 text-white"
                    >
                        <Bot className="mr-2 h-4 w-4" />
                        {t('File Claim with AI')}
                    </Button>
                    <Button onClick={() => router.push(`/dashboard/payments/new?policy_id=${policy.id}`)}>
                        <CreditCard className="mr-2 h-4 w-4" />
                        {t('Make Payment')}
                    </Button>
                </div>
            </div>

            {policy && (
                <CancellationWorkflow
                    open={isCancellationOpen}
                    onOpenChange={setIsCancellationOpen}
                    policy={policy}
                    onSuccess={loadData}
                />
            )}

            {/* Main Content */}
            <div className="grid gap-6 md:grid-cols-3">
                {/* Left Column: Details */}
                <div className="md:col-span-2 space-y-6">
                    <Card>
                        <CardHeader>
                            <div className="flex justify-between items-start">
                                <div>
                                    <CardTitle>{t('Policy Information')}</CardTitle>
                                    <CardDescription>{t('Coverage and premium details')}</CardDescription>
                                </div>
                                {getStatusBadge(policy.status)}
                            </div>
                        </CardHeader>
                        <CardContent className="grid gap-6 sm:grid-cols-2">
                            <div className="space-y-1">
                                <span className="text-sm font-medium text-muted-foreground">{t('Start Date')}</span>
                                <p className="font-medium">{format(new Date(policy.start_date), 'PPP')}</p>
                            </div>
                            <div className="space-y-1">
                                <span className="text-sm font-medium text-muted-foreground">{t('End Date')}</span>
                                <p className="font-medium">{format(new Date(policy.end_date), 'PPP')}</p>
                            </div>
                            <div className="space-y-1">
                                <span className="text-sm font-medium text-muted-foreground">{t('Premium Amount')}</span>
                                <p className="text-lg font-bold">{formatCurrency(policy.premium_amount)}</p>
                            </div>
                            <div className="space-y-1">
                                <span className="text-sm font-medium text-muted-foreground">{t('Frequency')}</span>
                                <p className="capitalize font-medium">{policy.premium_frequency}</p>
                            </div>
                            <div className="space-y-1">
                                <span className="text-sm font-medium text-muted-foreground">{t('Coverage Amount')}</span>
                                <p className="font-medium">{policy.coverage_amount ? formatCurrency(policy.coverage_amount) : 'N/A'}</p>
                            </div>
                            <div className="space-y-1">
                                <span className="text-sm font-medium text-muted-foreground">{t('Created By')}</span>
                                <p className="font-medium">{policy.created_by_name || 'N/A'}</p>
                            </div>
                        </CardContent>
                    </Card>

                    <Card>
                        <CardHeader>
                            <CardTitle>{t('Payment History')}</CardTitle>
                            <CardDescription>{t('Recent transactions for this policy')}</CardDescription>
                        </CardHeader>
                        <CardContent>
                            {payments.length === 0 ? (
                                <div className="text-center py-6 text-muted-foreground">
                                    {t('No payments recorded yet')}
                                </div>
                            ) : (
                                <Table>
                                    <TableHeader>
                                        <TableRow>
                                            <TableHead>{t('No.')}</TableHead>
                                            <TableHead>{t('Date')}</TableHead>
                                            <TableHead>{t('Amount')}</TableHead>
                                            <TableHead>{t('Method')}</TableHead>
                                            <TableHead>{t('Status')}</TableHead>
                                            <TableHead className="text-right">{t('Action')}</TableHead>
                                        </TableRow>
                                    </TableHeader>
                                    <TableBody>
                                        {payments.map((p) => (
                                            <TableRow key={p.id}>
                                                <TableCell className="font-medium">{p.payment_number}</TableCell>
                                                <TableCell>{formatDate(p.created_at)}</TableCell>
                                                <TableCell>{formatCurrency(p.amount, p.currency)}</TableCell>
                                                <TableCell className="capitalize">{p.payment_method.replace('_', ' ')}</TableCell>
                                                <TableCell>{getPaymentStatusBadge(p.status)}</TableCell>
                                                <TableCell className="text-right">
                                                    <Button variant="ghost" size="sm" onClick={() => router.push(`/dashboard/payments/${p.id}`)}>
                                                        {t('View')}
                                                    </Button>
                                                </TableCell>
                                            </TableRow>
                                        ))}
                                    </TableBody>
                                </Table>
                            )}
                        </CardContent>
                    </Card>
                </div>

                {/* Right Column: Client & Documents */}
                <div className="space-y-6">
                    <Card>
                        <CardHeader>
                            <CardTitle>{t('Client Details')}</CardTitle>
                        </CardHeader>
                        <CardContent className="space-y-4">
                            <div className="flex items-center gap-3">
                                <div className="h-10 w-10 rounded-full bg-primary/10 flex items-center justify-center text-primary font-bold">
                                    {policy.client_name?.charAt(0) || 'C'}
                                </div>
                                <div>
                                    <p className="font-medium">{policy.client_name}</p>
                                    <p className="text-xs text-muted-foreground">{t('Client ID')}: ...{policy.client_id.slice(-4)}</p>
                                </div>
                            </div>
                            <Separator />
                            <Button variant="outline" className="w-full" onClick={() => router.push(`/dashboard/clients/${policy.client_id}`)}>
                                {t('View Client Profile')}
                            </Button>
                        </CardContent>
                    </Card>

                    <Card>
                        <CardHeader>
                            <CardTitle>{t('Documents')}</CardTitle>
                        </CardHeader>
                        <CardContent className="space-y-2">
                            <Button
                                variant="outline"
                                className="w-full justify-start"
                                onClick={() => setShowAgreement(true)}
                            >
                                <FileText className="mr-2 h-4 w-4" />
                                {t('Policy Agreement.pdf')}
                            </Button>
                            <Button
                                variant="outline"
                                className="w-full justify-start"
                                onClick={handleGenerateSchedule}
                                disabled={isGenerating}
                            >
                                {isGenerating ? (
                                    <Loader2 className="mr-2 h-4 w-4 animate-spin" />
                                ) : (
                                    <FileText className="mr-2 h-4 w-4" />
                                )}
                                {t('Payment Schedule.pdf')}
                            </Button>
                        </CardContent>
                    </Card>

                    <Card className="border-2 border-primary/20">
                        <CardHeader className="pb-2">
                            <CardTitle className="flex items-center gap-2">
                                <QrCode className="h-5 w-5 text-primary" />
                                Policy Verification
                            </CardTitle>
                            <CardDescription>Authentication for third-parties</CardDescription>
                        </CardHeader>
                        <CardContent className="space-y-4 pt-4">
                            {!policy.qr_code_data ? (
                                <div className="text-center py-4 space-y-4">
                                    <p className="text-xs text-muted-foreground italic">No verification token generated for this policy.</p>
                                    <Button
                                        onClick={async () => {
                                            try {
                                                const res = await fetch(`${process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000'}/api/v1/public/verify/generate/${policy.id}`, { method: 'POST' });
                                                const data = await res.json();
                                                setPolicy({ ...policy, qr_code_data: data.token });
                                            } catch (e) {
                                                console.error(e);
                                            }
                                        }}
                                        className="w-full"
                                    >
                                        Generate Token
                                    </Button>
                                </div>
                            ) : (
                                <div className="flex flex-col items-center gap-4 py-2">
                                    <div className="bg-white p-2 rounded-lg shadow-inner border border-gray-100">
                                        <img
                                            src={`https://api.qrserver.com/v1/create-qr-code/?size=150x150&data=${encodeURIComponent(`${window.location.origin}/verify/${policy.qr_code_data}`)}`}
                                            alt="Verification QR Code"
                                            className="h-32 w-32"
                                        />
                                    </div>
                                    <div className="text-center">
                                        <p className="text-[10px] font-mono text-muted-foreground uppercase tracking-widest mb-1">Secure Token</p>
                                        <p className="text-xs font-mono bg-muted p-1 rounded truncate w-32 mx-auto">
                                            {policy.qr_code_data}
                                        </p>
                                    </div>
                                    <Button
                                        variant="outline"
                                        className="w-full"
                                        onClick={() => window.open(`/verify/${policy.qr_code_data}`, '_blank')}
                                    >
                                        <Printer className="h-4 w-4 mr-2" />
                                        Preview Public Page
                                    </Button>
                                </div>
                            )}
                        </CardContent>
                    </Card>

                    <Card>
                        <CardHeader className="flex flex-row items-center justify-between pb-2">
                            <CardTitle className="text-sm font-bold">Co-insurance</CardTitle>
                            <Button variant="ghost" size="icon" className="h-4 w-4" onClick={() => setIsCoInsuranceOpen(true)}>
                                <Edit className="h-3 w-3" />
                            </Button>
                        </CardHeader>
                        <CardContent className="space-y-4 pt-2">
                            {shares.length === 0 ? (
                                <p className="text-xs text-muted-foreground italic text-center py-2">No participants added.</p>
                            ) : (
                                <div className="space-y-3">
                                    {shares.map(s => (
                                        <div key={s.id} className="flex items-center justify-between bg-gray-50 p-2 rounded text-xs border border-gray-100">
                                            <div className="flex flex-col">
                                                <span className="font-bold">{s.company_name}</span>
                                                <span className="text-[10px] text-muted-foreground">Fee: {s.fee_percentage}%</span>
                                            </div>
                                            <div className="flex items-center gap-2">
                                                <Badge variant="outline" className="font-bold">{s.share_percentage}%</Badge>
                                                <Button
                                                    variant="ghost"
                                                    size="icon"
                                                    className="h-5 w-5 text-red-400 hover:text-red-500 hover:bg-red-50"
                                                    onClick={async () => {
                                                        // Removed blocking confirm() per hydration best practices
                                                        await coInsuranceApi.removeShare(s.id);
                                                        loadData();
                                                    }}
                                                >
                                                    <XCircle className="h-3 w-3" />
                                                </Button>
                                            </div>
                                        </div>
                                    ))}
                                    <div className="pt-2 border-t flex justify-between items-center px-1">
                                        <span className="text-[10px] font-bold text-muted-foreground uppercase">Total Shared</span>
                                        <span className="text-xs font-bold">{shares.reduce((acc, s) => acc + s.share_percentage, 0)}%</span>
                                    </div>
                                </div>
                            )}
                        </CardContent>
                    </Card>
                </div>
            </div>

            {/* Edit DIalogs */}
            {policy && (
                <>
                    <PolicyFormDialog
                        open={isEditOpen}
                        onOpenChange={setIsEditOpen}
                        policy={policy}
                        onSuccess={handlePolicyUpdated}
                    />
                    <CoInsuranceModal
                        open={isCoInsuranceOpen}
                        onOpenChange={setIsCoInsuranceOpen}
                        policyId={policy.id}
                        onSuccess={loadData}
                    />
                </>
            )}

            {/* AI Claim Dialog */}
            <Dialog open={isClaimOpen} onOpenChange={setIsClaimOpen}>
                <DialogContent>
                    <DialogHeader>
                        <DialogTitle>File a Claim with AI</DialogTitle>
                        <CardDescription>Describe what happened, and our AI will process your claim.</CardDescription>
                    </DialogHeader>

                    {!aiResponse ? (
                        <div className="space-y-4 py-4">
                            <Textarea
                                placeholder="I was involved in a car accident on specific date..."
                                className="min-h-[100px]"
                                value={claimDescription}
                                onChange={(e) => setClaimDescription(e.target.value)}
                            />
                        </div>
                    ) : (
                        <div className="py-4 bg-muted/50 p-4 rounded-md whitespace-pre-wrap">
                            {aiResponse}
                        </div>
                    )}

                    <DialogFooter>
                        {!aiResponse ? (
                            <Button onClick={handleFileClaim} disabled={!claimDescription || isSubmittingClaim}>
                                {isSubmittingClaim ? 'Processing...' : 'Submit Claim'}
                            </Button>
                        ) : (
                            <Button onClick={() => { setIsClaimOpen(false); setAiResponse(''); }}>
                                Close
                            </Button>
                        )}
                    </DialogFooter>
                </DialogContent>
            </Dialog>


        </div>
    );
}

