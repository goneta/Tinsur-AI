'use client';

import { useState, useEffect } from 'react';
import { portalApi, PortalPayment } from '@/lib/portal-api';
import { formatCurrency, formatDate } from '@/lib/utils';
import {
    CreditCard,
    Calendar,
    CheckCircle,
    XCircle,
    Clock,
    ChevronRight,
    Smartphone,
    Building2,
    Banknote,
    PlusCircle
} from 'lucide-react';
import { Button } from '@/components/ui/button';
import { Card, CardContent } from '@/components/ui/card';
import { Loader2 } from 'lucide-react';

interface PortalPaymentsTabProps {
    onMakePayment: () => void;
}

export function PortalPaymentsTab({ onMakePayment }: PortalPaymentsTabProps) {
    const [payments, setPayments] = useState<PortalPayment[]>([]);
    const [isLoading, setIsLoading] = useState(true);

    useEffect(() => {
        const fetchPayments = async () => {
            try {
                const data = await portalApi.getMyPayments();
                setPayments(data);
            } catch (error) {
                console.error("Failed to fetch payments", error);
            } finally {
                setIsLoading(false);
            }
        };
        fetchPayments();
    }, []);

    const getStatusIcon = (status: string) => {
        switch (status) {
            case 'completed': return <CheckCircle className="h-5 w-5 text-green-500" />;
            case 'failed': return <XCircle className="h-5 w-5 text-red-500" />;
            default: return <Clock className="h-5 w-5 text-yellow-500" />;
        }
    };

    const getPaymentIcon = (method: string) => {
        switch (method) {
            case 'mobile_money': return <Smartphone className="h-5 w-5" />;
            case 'bank_transfer': return <Building2 className="h-5 w-5" />;
            case 'stripe': return <CreditCard className="h-5 w-5" />;
            default: return <Banknote className="h-5 w-5" />;
        }
    };

    const getFrequencyLabel = (freq?: string) => {
        if (!freq) return 'Other';
        const f = freq.toLowerCase();
        if (f.includes('month')) return 'Monthly';
        if (f.includes('quarter')) return 'Quarterly';
        if (f.includes('year') || f.includes('annual')) return 'Yearly';
        return freq.charAt(0).toUpperCase() + freq.slice(1);
    };

    const groupedPayments = payments.reduce((acc, payment) => {
        const freq = getFrequencyLabel(payment.premium_frequency);
        if (!acc[freq]) acc[freq] = [];
        acc[freq].push(payment);
        return acc;
    }, {} as Record<string, PortalPayment[]>);

    if (isLoading) {
        return (
            <div className="flex h-[400px] items-center justify-center">
                <Loader2 className="h-8 w-8 animate-spin text-muted-foreground" />
            </div>
        );
    }

    return (
        <div className="space-y-12 animate-in fade-in duration-500">
            <div className="flex flex-col md:flex-row md:items-center justify-between gap-6">
                <div>
                    <h3 className="text-4xl font-black text-gray-900 mb-2">Historique des paiements</h3>
                    <p className="text-gray-400 text-lg font-bold">Consultez et gérez vos primes d&apos;assurance.</p>
                </div>
                <Button
                    onClick={onMakePayment}
                    className="px-8 py-7 rounded-[25px] bg-[#00539F] text-white font-black text-lg hover:bg-[#004380] transition-all shadow-xl gap-3"
                >
                    <PlusCircle className="h-6 w-6" />
                    Make a Payment
                </Button>
            </div>

            {payments.length === 0 ? (
                <div className="py-24 text-center bg-gray-50/50 rounded-[40px] border border-gray-100">
                    <div className="inline-block p-10 bg-white shadow-xl rounded-full mb-8">
                        <Banknote className="h-20 w-20 text-gray-200" />
                    </div>
                    <h3 className="text-2xl font-black text-gray-900 mb-2">No payments found</h3>
                    <p className="text-gray-400 text-lg font-bold max-w-sm mx-auto">You haven&apos;t made any payments yet. Your history will appear here.</p>
                </div>
            ) : (
                <div className="space-y-16">
                    {Object.entries(groupedPayments).map(([freq, items]) => (
                        <div key={freq} className="space-y-8">
                            <div className="flex items-center gap-4">
                                <div className="h-px flex-1 bg-gray-100" />
                                <h4 className="text-sm font-black text-[#00539F] uppercase tracking-[0.2em]">{freq} Payments</h4>
                                <div className="h-px flex-1 bg-gray-100" />
                            </div>

                            <div className="grid grid-cols-1 gap-6">
                                {items.map((payment) => (
                                    <div
                                        key={payment.id}
                                        className="grid grid-cols-12 items-center gap-6 p-8 border border-gray-100 rounded-[35px] bg-white hover:bg-gray-50/50 transition-all shadow-sm hover:shadow-md group"
                                    >
                                        <div className="col-span-12 lg:col-span-6 flex items-center gap-6">
                                            <div className="p-5 bg-[#00539F]/10 rounded-[25px] flex-shrink-0 shadow-inner group-hover:scale-110 transition-transform">
                                                {getPaymentIcon(payment.payment_method)}
                                            </div>
                                            <div>
                                                <div className="flex items-center gap-3 mb-2">
                                                    <h4 className="text-xl font-black text-gray-900">{payment.payment_number}</h4>
                                                    <span className={`px-4 py-1.5 rounded-full text-[10px] font-black uppercase tracking-wider ${payment.status === 'completed' ? 'bg-green-100 text-green-700' :
                                                            payment.status === 'failed' ? 'bg-red-100 text-red-700' : 'bg-yellow-100 text-yellow-700'
                                                        }`}>
                                                        {payment.status}
                                                    </span>
                                                </div>
                                                <div className="flex items-center gap-4 text-sm text-gray-400 font-bold">
                                                    <span className="flex items-center gap-1.5">
                                                        <Calendar className="h-4 w-4" />
                                                        {formatDate(payment.created_at)}
                                                    </span>
                                                    <span>•</span>
                                                    <span>Policy: {payment.policy_number_display || 'N/A'}</span>
                                                </div>
                                            </div>
                                        </div>

                                        <div className="col-span-12 lg:col-span-4 flex items-center justify-between lg:justify-end gap-12">
                                            <div className="text-right">
                                                <p className="text-sm text-gray-400 font-bold uppercase mb-1">Method</p>
                                                <p className="text-black font-black capitalize">{payment.payment_method.replace('_', ' ')}</p>
                                            </div>
                                            <div className="text-right">
                                                <p className="text-sm text-gray-400 font-bold uppercase mb-1">Amount</p>
                                                <p className="text-3xl font-black text-black">
                                                    {formatCurrency(payment.amount, payment.currency)}
                                                </p>
                                            </div>
                                        </div>

                                        <div className="col-span-12 lg:col-span-2 flex justify-end">
                                            <Button variant="ghost" className="rounded-full h-12 w-12 p-0 hover:bg-[#00539F]/10 group/btn">
                                                <ChevronRight className="h-6 w-6 text-gray-300 group-hover/btn:text-[#00539F] transition-colors" />
                                            </Button>
                                        </div>
                                    </div>
                                ))}
                            </div>
                        </div>
                    ))}
                </div>
            )}
        </div>
    );
}
