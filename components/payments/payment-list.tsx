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

export function PaymentList() {
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
                    <CardTitle>Payments</CardTitle>
                    <CardDescription>View and manage payment transactions.</CardDescription>
                </CardHeader>
                <CardContent>
                    <div className="flex flex-col gap-4 md:flex-row md:items-center md:justify-between mb-6">
                        <div className="flex gap-2 items-center">
                            <Filter className="w-4 h-4 text-muted-foreground" />
                            <Select value={statusFilter} onValueChange={setStatusFilter}>
                                <SelectTrigger className="w-[150px]">
                                    <SelectValue placeholder="Status" />
                                </SelectTrigger>
                                <SelectContent>
                                    <SelectItem value="all">All Statuses</SelectItem>
                                    <SelectItem value="completed">Completed</SelectItem>
                                    <SelectItem value="pending">Pending</SelectItem>
                                    <SelectItem value="failed">Failed</SelectItem>
                                    <SelectItem value="refunded">Refunded</SelectItem>
                                </SelectContent>
                            </Select>

                            <Select value={methodFilter} onValueChange={setMethodFilter}>
                                <SelectTrigger className="w-[150px]">
                                    <SelectValue placeholder="Method" />
                                </SelectTrigger>
                                <SelectContent>
                                    <SelectItem value="all">All Methods</SelectItem>
                                    <SelectItem value="stripe">Stripe</SelectItem>
                                    <SelectItem value="mobile_money">Mobile Money</SelectItem>
                                    <SelectItem value="bank_transfer">Bank Transfer</SelectItem>
                                    <SelectItem value="cash">Cash</SelectItem>
                                </SelectContent>
                            </Select>
                        </div>
                        <Button variant="outline" size="sm" onClick={loadPayments}>
                            <RefreshCw className="mr-2 h-4 w-4" />
                            Refresh
                        </Button>
                    </div>

                    <div className="rounded-md border">
                        <Table>
                            <TableHeader>
                                <TableRow>
                                    <TableHead>Payment #</TableHead>
                                    <TableHead>Client</TableHead>
                                    <TableHead>Policy</TableHead>
                                    <TableHead>Created By</TableHead>
                                    <TableHead>Date</TableHead>
                                    <TableHead>Amount</TableHead>
                                    <TableHead>Method</TableHead>
                                    <TableHead>Status</TableHead>
                                    <TableHead className="text-right">Actions</TableHead>
                                </TableRow>
                            </TableHeader>
                            <TableBody>
                                {loading ? (
                                    <TableRow>
                                        <TableCell colSpan={9} className="h-24 text-center">
                                            Loading...
                                        </TableCell>
                                    </TableRow>
                                ) : payments.length === 0 ? (
                                    <TableRow>
                                        <TableCell colSpan={9} className="h-24 text-center">
                                            No payments found.
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
                                                    View
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
