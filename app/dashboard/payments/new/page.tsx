"use client";

import { useEffect, useState, use } from "react";
import { useRouter, useSearchParams } from "next/navigation";
import { ArrowLeft } from "lucide-react";

import { Button } from "@/components/ui/button";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { PaymentForm } from "@/components/payments/payment-form";
import { policyApi } from "@/lib/policy-api";
import { Policy } from "@/types/policy";
import { formatCurrency } from "@/lib/utils";
import { useLanguage } from '@/contexts/language-context';

export default function NewPaymentPage() {
    const { t } = useLanguage();
    const router = useRouter();
    const searchParams = useSearchParams();
    const policyId = searchParams.get("policy_id");

    const [policy, setPolicy] = useState<Policy | null>(null);
    const [loading, setLoading] = useState(true);

    useEffect(() => {
        if (policyId) {
            policyApi.getPolicy(policyId)
                .then(setPolicy)
                .catch((err) => console.error("Failed to load policy", err))
                .finally(() => setLoading(false));
        } else {
            setLoading(false);
        }
    }, [policyId]);

    const handleSuccess = () => {
        if (policyId) {
            router.push(`/dashboard/policies/${policyId}`);
        } else {
            router.push("/dashboard/payments");
        }
    };

    if (!policyId) {
        return (
            <div className="p-8">
                <div className="flex items-center space-x-2 mb-6">
                    <Button variant="ghost" size="icon" onClick={() => router.back()}>
                        <ArrowLeft className="h-4 w-4" />
                    </Button>
                    <h2 className="text-3xl font-bold tracking-tight">{t('payments.new_payment', 'New Payment')}</h2>
                </div>
                <p>{t('payments.select_policy_msg', 'Please select a policy to make a payment.')}</p>
                {/* TODO: Add policy selector if needed, for now assume entry from policy details */}
            </div>
        );
    }

    if (loading) {
        return <div className="p-8">{t('common.loading', 'Loading policy details...')}</div>;
    }

    if (!policy) {
        return <div className="p-8">{t('payments.policy_not_found', 'Policy not found.')}</div>;
    }

    return (
        <div className="space-y-6 p-8 pt-6">
            <div className="flex items-center space-x-2">
                <Button variant="ghost" size="icon" onClick={() => router.back()}>
                    <ArrowLeft className="h-4 w-4" />
                </Button>
                <div>
                    <h2 className="text-3xl font-bold tracking-tight">{t('payments.process_payment', 'Process Payment')}</h2>
                    <p className="text-muted-foreground">{t('payments.record_payment_desc', 'Record a new payment for policy')} {policy.policy_number}</p>
                </div>
            </div>

            <div className="grid gap-6 md:grid-cols-3">
                <div className="md:col-span-2">
                    <Card>
                        <CardHeader>
                            <CardTitle>{t('payments.details', 'Payment Details')}</CardTitle>
                            <CardDescription>{t('payments.enter_info', 'Enter the payment information below')}</CardDescription>
                        </CardHeader>
                        <CardContent>
                            <PaymentForm
                                policyId={policy.id}
                                policyNumber={policy.policy_number}
                                defaultAmount={policy.premium_amount}
                                onSuccess={handleSuccess}
                            />
                        </CardContent>
                    </Card>
                </div>

                <div>
                    <Card>
                        <CardHeader>
                            <CardTitle>{t('payments.policy_summary', 'Policy Summary')}</CardTitle>
                        </CardHeader>
                        <CardContent className="space-y-4">
                            <div>
                                <span className="text-sm font-medium text-muted-foreground">{t('payments.client', 'Client')}</span>
                                <p className="font-medium">{policy.client_name}</p>
                            </div>
                            <div>
                                <span className="text-sm font-medium text-muted-foreground">{t('payments.policy_number', 'Policy Number')}</span>
                                <p className="font-medium">{policy.policy_number}</p>
                            </div>
                            <div>
                                <span className="text-sm font-medium text-muted-foreground">{t('payments.premium_amount', 'Premium Amount')}</span>
                                <p className="text-lg font-bold">{formatCurrency(policy.premium_amount)}</p>
                            </div>
                            <div>
                                <span className="text-sm font-medium text-muted-foreground">{t('payments.coverage', 'Coverage')}</span>
                                <p>{formatCurrency(policy.coverage_amount || 0)}</p>
                            </div>
                            <div>
                                <span className="text-sm font-medium text-muted-foreground">{t('payments.frequency', 'Frequency')}</span>
                                <p className="capitalize">{t(policy.premium_frequency) || policy.premium_frequency}</p>
                            </div>
                        </CardContent>
                    </Card>
                </div>
            </div>
        </div>
    );
}
