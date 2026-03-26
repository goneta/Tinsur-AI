"use client";

import { useEffect, useState } from "react";
import { companyApi, Company } from "@/lib/company-api";
import { QuoteElementManager } from "./quote-element-manager";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { useToast } from "@/components/ui/use-toast";
import { Loader2, Save } from "lucide-react";

import { useLanguage } from '@/contexts/language-context';

export function FinancialSettings() {
    const { t } = useLanguage();
    return (
        <div className="space-y-8">
            <Card>
                <CardHeader>
                    <CardTitle>{t('admin.financials.base_rates', 'Base Rates')}</CardTitle>
                    <CardDescription>{t('admin.financials.base_rates_desc', 'Standard percentages used as starting points for quote calculations.')}</CardDescription>
                </CardHeader>
                <CardContent>
                    <QuoteElementManager
                        category="base_rate"
                        title={t('admin.financials.base_rates', 'Base Rates')}
                        description={t('admin.financials.manage_rates', 'Manage base percentage rates.')}
                        valueLabel={t('admin.financials.rate_percent', 'Rate (%)')}
                    />
                </CardContent>
            </Card>

            <Card>
                <CardHeader>
                    <CardTitle>Coverage Amounts</CardTitle>
                    <CardDescription>Pre-defined insured values for assets or persons.</CardDescription>
                </CardHeader>
                <CardContent>
                    <QuoteElementManager
                        category="coverage_amount"
                        title="Coverage Amounts"
                        description="Manage selectable coverage amounts."
                        valueLabel="Amount (FCFA)"
                    />
                </CardContent>
            </Card>

            <Card>
                <CardHeader>
                    <CardTitle>Risk Multipliers</CardTitle>
                    <CardDescription>Adjustment factors based on client risk profile.</CardDescription>
                </CardHeader>
                <CardContent>
                    <QuoteElementManager
                        category="risk_multiplier"
                        title="Risk Multipliers"
                        description="Manage risk adjustment factors (e.g. 1.25 for high risk)."
                        valueLabel="Multiplier (x)"
                    />
                </CardContent>
            </Card>

            <Card>
                <CardHeader>
                    <CardTitle>Fixed Fees</CardTitle>
                    <CardDescription>Flat charges such as administrative fees or taxes.</CardDescription>
                </CardHeader>
                <CardContent>
                    <QuoteElementManager
                        category="fixed_fee"
                        title="Fixed Fees"
                        description="Manage fixed cost additions."
                        valueLabel="Fee Amount (FCFA)"
                    />
                </CardContent>
            </Card>

            <Card>
                <CardHeader>
                    <CardTitle>Government Tax</CardTitle>
                    <CardDescription>Manage government taxes applicable to quotes.</CardDescription>
                </CardHeader>
                <CardContent>
                    <QuoteElementManager
                        category="government_tax"
                        title="Government Tax"
                        description="Optional taxes applied to premium."
                        valueLabel="Tax Rate (%)"
                    />
                </CardContent>
            </Card>

            <Card>
                <CardHeader>
                    <CardTitle>Company Discounts</CardTitle>
                    <CardDescription>Manage discretionary discounts.</CardDescription>
                </CardHeader>
                <CardContent>
                    <QuoteElementManager
                        category="company_discount"
                        title="Company Discounts"
                        description="Optional discounts available for selection."
                        valueLabel="Discount Rate (%)"
                    />
                </CardContent>
            </Card>
        </div>
    );
}
