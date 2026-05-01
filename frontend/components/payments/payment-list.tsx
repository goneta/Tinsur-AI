'use client';

import { useState, useEffect } from 'react';
import { useRouter } from 'next/navigation';
import { paymentApi } from '@/lib/payment-api';
import { Payment } from '@/types/payment';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import {
    Table,
    TableBody,
    TableCell,
    TableHead,
    TableHeader,
    TableRow,
} from '@/components/ui/table';
import { Badge } from '@/components/ui/badge';
import {
    Select,
    SelectContent,
    SelectItem,
    SelectTrigger,
    SelectValue,
} from '@/components/ui/select';
import { formatCurrency, formatDate } from '@/lib/utils';
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from '@/components/ui/card';
import { Search, Filter, RefreshCw, Eye } from 'lucide-react';
import { useLanguage } from '@/contexts/language-context';

export function PaymentList() {
    const { t } = useLanguage();
    const router = useRouter();
    const [payments, setPayments] = useState<Payment[]>([]);
    const [loading, setLoading] = useState(true);
    const [statusFilter, setStatusFilter] = useState('all');
    const [methodFilter, setMethodFilter] = useState('all');

    const loadPayments = async () => {
        setLoading(true);
        try {
            const data = await paymentApi.getPayments({
                status: statusFilter,
                payment_method: methodFilter,
                page: 1, // Pagination TODO
                page_size: 50,
            });
            setPayments(data.payments);
        } catch (error) {
            console.error('Failed to load payments:', error);
        } finally {
            setLoading(false);
        }
    };

    useEffect(() => {
        loadPayments();
    }, [statusFilter, methodFilter]);

    const getStatusBadge = (status: string) => {
        const variants: Record<string, 'default' | 'secondary' | 'destructive' | 'outline' | 'success'> = {
            completed: 'success',
            pending: 'secondary',
            processing: 'default',
            failed: 'destructive',
            refunded: 'outline',
        };
        // Use a generic variant since 'success' might not be in the defaultshadcn Badge theme yet,
        // mapping 'success' to 'default' with green classes if needed, or just use default variants.
        // Assuming 'default', 'secondary', 'destructive', 'outline' exist.
        const variantMap: Record<string, "default" | "secondary" | "destructive" | "outline"> = {
            completed: 'default', // Often success is green, using default usually primary
            pending: 'secondary',
            processing: 'secondary',
            failed: 'destructive',
            refunded: 'outline',
        };

        const style = status === 'completed' ? 'bg-green-600 hover:bg-green-700' : '';

        return <Badge variant={variantMap[status] || 'default'} className={style}>{status}</Badge>;
    };

    return (
        <div className="space-y-4">
            <Card>
                <CardHeader>
                    <CardTitle>{t('label.payments', 'Payments')}</CardTitle>
                    <CardDescription>{t('payment.list_desc', 'View and manage payment transactions.')}</CardDescription>
                </CardHeader>
                <CardContent>
                    <div className="flex flex-col gap-4 md:flex-row md:items-center md:justify-between mb-6">
                        <div className="flex gap-2 items-center">
                            <Filter className="w-4 h-4 text-muted-foreground" />
                            <Select value={statusFilter} onValueChange={setStatusFilter}>
                                <SelectTrigger className="w-[150px]">
                                    <SelectValue placeholder={t('label.status', 'Status')} />
                                </SelectTrigger>
                                <SelectContent>
                                    <SelectItem value="all">{t('payment.all_statuses', 'All Statuses')}</SelectItem>
                                    <SelectItem value="completed">{t('status.completed', 'Completed')}</SelectItem>
                                    <SelectItem value="pending">{t('status.pending', 'Pending')}</SelectItem>
                                    <SelectItem value="failed">{t('status.failed', 'Failed')}</SelectItem>
                                    <SelectItem value="refunded">{t('status.refunded', 'Refunded')}</SelectItem>
                                </SelectContent>
                            </Select>

                            <Select value={methodFilter} onValueChange={setMethodFilter}>
                                <SelectTrigger className="w-[150px]">
                                    <SelectValue placeholder={t('payment.method_label', 'Method')} />
                                </SelectTrigger>
                                <SelectContent>
                                    <SelectItem value="all">{t('payment.all_methods', 'All Methods')}</SelectItem>
                                    <SelectItem value="stripe">Stripe</SelectItem>
                                    <SelectItem value="mobile_money">{t('payment.method.mobile_money', 'Mobile Money')}</SelectItem>
                                    <SelectItem value="bank_transfer">{t('payment.method.bank_transfer', 'Bank Transfer')}</SelectItem>
                                    <SelectItem value="cash">{t('payment.method.cash', 'Cash')}</SelectItem>
                                </SelectContent>
                            </Select>
                        </div>
                        <Button variant="outline" size="sm" onClick={loadPayments}>
                            <RefreshCw className="mr-2 h-4 w-4" />
                            {t('common.refresh', 'Refresh')}
                        </Button>
                    </div>

                    <div className="rounded-md border">
                        <Table>
                            <TableHeader>
                                <TableRow>
                                    <TableHead>{t('label.payment', 'Payment #')}</TableHead>
                                    <TableHead>{t('label.client', 'Client')}</TableHead>
                                    <TableHead>{t('label.policy', 'Policy')}</TableHead>
                                    <TableHead>{t('label.created_by', 'Created By')}</TableHead>
                                    <TableHead>{t('label.date', 'Date')}</TableHead>
                                    <TableHead>{t('label.amount', 'Amount')}</TableHead>
                                    <TableHead>{t('label.method', 'Method')}</TableHead>
                                    <TableHead>{t('label.status', 'Status')}</TableHead>
                                    <TableHead className="text-right">{t('common.actions', 'Actions')}</TableHead>
                                </TableRow>
                            </TableHeader>
                            <TableBody>
                                {loading ? (
                                    <TableRow>
                                        <TableCell colSpan={9} className="h-24 text-center">
                                            {t('common.loading', 'Loading...')}
                                        </TableCell>
                                    </TableRow>
                                ) : payments.length === 0 ? (
                                    <TableRow>
                                        <TableCell colSpan={9} className="h-24 text-center">
                                            {t('payment.no_payments', 'No payments found.')}
                                        </TableCell>
                                    </TableRow>
                                ) : (
                                    payments.map((payment) => (
                                        <TableRow key={payment.id}>
                                            <TableCell className="font-medium">
                                                {payment.payment_number}
                                            </TableCell>
                                            <TableCell>
                                                {payment.client_name || '-'}
                                            </TableCell>
                                            <TableCell>
                                                {payment.policy_number_display || '-'}
                                            </TableCell>
                                            <TableCell>
                                                {payment.created_by_name || '-'}
                                            </TableCell>
                                            <TableCell>
                                                {formatDate(payment.created_at)}
                                            </TableCell>
                                            <TableCell>
                                                {formatCurrency(payment.amount, payment.currency)}
                                            </TableCell>
                                            <TableCell className="capitalize">
                                                {payment.payment_method.replace('_', ' ')}
                                            </TableCell>
                                            <TableCell>
                                                {getStatusBadge(payment.status)}
                                            </TableCell>
                                            <TableCell className="text-right">
                                                <Button
                                                    variant="ghost"
                                                    size="sm"
                                                    onClick={() => router.push(`/dashboard/payments/${payment.id}`)}
                                                >
                                                    <Eye className="h-4 w-4 mr-1" />
                                                    {t('btn.view', 'View')}
                                                </Button>
                                            </TableCell>
                                        </TableRow>
                                    ))
                                )}
                            </TableBody>
                        </Table>
                    </div>
                </CardContent>
            </Card>
        </div>
    );
}
