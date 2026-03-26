'use client';

import { useEffect, useState, use } from 'react';
import { useRouter } from 'next/navigation';
import { paymentApi } from '@/lib/payment-api';
import { Payment } from '@/types/payment';
import { Button } from '@/components/ui/button';
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { formatCurrency, formatDate } from '@/lib/utils';
import { ArrowLeft, Printer } from 'lucide-react';
import { useLanguage } from '@/contexts/language-context';

export default function PaymentDetailsPage({ params }: { params: Promise<{ id: string }> }) {
    const { t } = useLanguage();
    const router = useRouter();
    const resolvedParams = use(params);
    const [payment, setPayment] = useState<Payment | null>(null);
    const [loading, setLoading] = useState(true);

    useEffect(() => {
        const loadPayment = async () => {
            try {
                const data = await paymentApi.getPayment(resolvedParams.id);
                setPayment(data);
            } catch (error) {
                console.error('Failed to load payment:', error);
            } finally {
                setLoading(false);
            }
        };
        loadPayment();
    }, [resolvedParams.id]);

    if (loading) return <div className="p-8">{t('common.loading', 'Loading...')}</div>;
    if (!payment) return <div className="p-8">{t('payments.not_found', 'Payment not found')}</div>;

    const getStatusBadge = (status: string) => {
        const variantMap: Record<string, "default" | "secondary" | "destructive" | "outline"> = {
            completed: 'default',
            pending: 'secondary',
            processing: 'secondary',
            failed: 'destructive',
            refunded: 'outline',
        };
        const style = status === 'completed' ? 'bg-green-600 hover:bg-green-700' : '';
        // Translating the badge content
        const translatedStatus = t(status) || status;
        return <Badge variant={variantMap[status] || 'default'} className={style}>{translatedStatus}</Badge>;
    };

    return (
        <div className="space-y-6 p-8 pt-6">
            <div className="flex items-center justify-between">
                <div className="flex items-center space-x-2">
                    <Button variant="ghost" size="icon" onClick={() => router.back()}>
                        <ArrowLeft className="h-4 w-4" />
                    </Button>
                    <h2 className="text-3xl font-bold tracking-tight">{t('payments.details_title', 'Payment Details')}</h2>
                </div>
                <div className="flex items-center space-x-2">
                    <Button variant="outline">
                        <Printer className="mr-2 h-4 w-4" />
                        {t('payments.print_receipt', 'Print Receipt')}
                    </Button>
                </div>
            </div>

            <div className="grid gap-6 md:grid-cols-2">
                <Card>
                    <CardHeader>
                        <CardTitle>{t('payments.txn_info', 'Transaction Information')}</CardTitle>
                        <CardDescription>{t('payments.txn_desc', 'Details of the payment transaction.')}</CardDescription>
                    </CardHeader>
                    <CardContent className="space-y-4">
                        <div className="grid grid-cols-2 gap-4">
                            <div className="space-y-1">
                                <span className="text-sm font-medium text-muted-foreground">{t('payments.payment_number', 'Payment Number')}</span>
                                <p className="font-medium">{payment.payment_number}</p>
                            </div>
                            <div className="space-y-1">
                                <span className="text-sm font-medium text-muted-foreground">{t('payments.status', 'Status')}</span>
                                <div>{getStatusBadge(payment.status)}</div>
                            </div>
                            <div className="space-y-1">
                                <span className="text-sm font-medium text-muted-foreground">{t('payments.amount', 'Amount')}</span>
                                <p className="text-2xl font-bold">{formatCurrency(payment.amount, payment.currency)}</p>
                            </div>
                            <div className="space-y-1">
                                <span className="text-sm font-medium text-muted-foreground">{t('payments.date', 'Date')}</span>
                                <p>{formatDate(payment.created_at)}</p>
                            </div>
                            <div className="space-y-1">
                                <span className="text-sm font-medium text-muted-foreground">{t('payments.method', 'Method')}</span>
                                <p className="capitalize">{t(payment.payment_method) || payment.payment_method.replace('_', ' ')}</p>
                            </div>
                            {payment.payment_gateway && (
                                <div className="space-y-1">
                                    <span className="text-sm font-medium text-muted-foreground">{t('payments.gateway', 'Gateway')}</span>
                                    <p className="capitalize">{payment.payment_gateway.replace('_', ' ')}</p>
                                </div>
                            )}
                            {payment.reference_number && (
                                <div className="space-y-1 col-span-2">
                                    <span className="text-sm font-medium text-muted-foreground">{t('payments.reference', 'Reference')}</span>
                                    <p className="font-mono text-sm">{payment.reference_number}</p>
                                </div>
                            )}
                        </div>
                    </CardContent>
                </Card>

                <Card>
                    <CardHeader>
                        <CardTitle>{t('payments.related_info', 'Related Information')}</CardTitle>
                        <CardDescription>{t('payments.related_desc', 'Associated client and policy details.')}</CardDescription>
                    </CardHeader>
                    <CardContent className="space-y-4">
                        <div className="grid grid-cols-1 gap-4">
                            <div className="space-y-1">
                                <span className="text-sm font-medium text-muted-foreground">{t('payments.client', 'Client')}</span>
                                <p className="text-lg font-medium">{payment.client_name || t('common.unknown_client', 'Unknown Client')}</p>
                            </div>
                            <div className="space-y-1">
                                <span className="text-sm font-medium text-muted-foreground">{t('payments.policy_number', 'Policy Number')}</span>
                                <p className="font-medium">{payment.policy_number_display || 'N/A'}</p>
                            </div>
                            <div className="space-y-1">
                                <span className="text-sm font-medium text-muted-foreground">{t('payments.created_by', 'Created By')}</span>
                                <p className="font-medium">{payment.created_by_name || t('common.unknown', 'Unknown')}</p>
                            </div>
                        </div>
                    </CardContent>
                </Card>
            </div>
        </div>
    );
}
