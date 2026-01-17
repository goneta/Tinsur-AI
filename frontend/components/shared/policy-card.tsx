import React, { useMemo } from 'react';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import { Avatar, AvatarFallback, AvatarImage } from "@/components/ui/avatar";
import { UniversalEntityCard } from '@/components/shared/universal-entity-card';
import { Check, CreditCard, ShieldCheck, FileText, Car, Home, User } from 'lucide-react';
import { useLanguage } from '@/contexts/language-context';

interface PolicyFeature {
    id: string;
    label: string;
    included: boolean;
}

interface PolicyCardProps {
    policy: {
        id: string;
        vehicleName: string; // Used as main title if Auto/House, or fallback
        registrationNumber: string;
        policyNumber: string;
        status: string;
        activeDate: string;
        premium: string; // Formatted annual premium
        premiumAmount?: number; // Raw annual premium for calc
        coverLevel: string; // Used as Policy Type Label (e.g. Sante, Auto Gold)
        type?: string; // specific type key: health, home, auto
        features: PolicyFeature[];
        vehicleImage?: string;
        entityImage?: string; // Vehicle or House image
        clientImage?: string;
        clientName?: string;
    };
    onViewDocuments: () => void;
    onMakeClaim: () => void;
    onMakePayment: () => void;
    onViewPayment?: () => void;
    className?: string;
}

export function PolicyCard({ policy, onViewDocuments, onMakeClaim, onMakePayment, onViewPayment, className }: PolicyCardProps) {
    const { t, formatPrice } = useLanguage();

    const items = policy.features.slice(0, 5).map((feature, idx) => ({
        id: `feat-${idx}`,
        label: feature.label,
        checked: feature.included,
        disabled: true,
        checkClassName: "h-4 w-4", // Smaller checks
        iconClassname: "h-2.5 w-2.5"
    }));

    // Logic to determine Icon and Image
    const { mainImage, mainIcon: MainIcon, mainTitle, secondaryTitle } = useMemo(() => {
        const typeLower = (policy.type || policy.coverLevel || "").toLowerCase();

        // Default to entity/vehicle image or car icon
        let img = policy.entityImage || policy.vehicleImage;
        let icon = Car;
        let title = t(policy.vehicleName, policy.vehicleName) || t("Vehicle", "Vehicle");
        let sub = t("Active Policy", "Active Policy");

        // Logic for Health
        if (typeLower.includes('health') || typeLower.includes('santé') || typeLower.includes('sante')) {
            img = policy.clientImage;
            icon = User;
            title = policy.clientName || title;
        }
        // Logic for Home
        else if (typeLower.includes('home') || typeLower.includes('house') || typeLower.includes('habitation')) {
            img = policy.entityImage;
            icon = Home;
            // title remains vehicleName (which should be Address or House Name in this context)
        }

        // If no title, fallback
        if (!title || title === 'Unknown') {
            title = t("Insurance Policy", "Insurance Policy");
        }

        return { mainImage: img, mainIcon: icon, mainTitle: title, secondaryTitle: sub };
    }, [policy, t]);

    // Financials Calculation
    const annualPremium = policy.premiumAmount || 0;
    const monthlyPremium = annualPremium > 0 ? annualPremium / 12 : 0;

    return (
        <UniversalEntityCard
            header={{
                title: mainTitle,
                customContent: (
                    <div className="w-full">
                        {/* Top: Policy Type Label */}
                        <div className="flex justify-end mb-2">
                            <Badge className="bg-green-100 text-green-700 hover:bg-green-200 border-none font-bold uppercase tracking-widest text-[10px] px-3 py-1">
                                {t(policy.coverLevel, policy.coverLevel)}
                            </Badge>
                        </div>

                        <div className="flex gap-4 items-start mb-6">
                            {/* Entity/Client Image */}
                            <Avatar className="h-12 w-12 border-2 border-green-500">
                                <AvatarImage src={mainImage} alt={mainTitle} />
                                <AvatarFallback className="bg-green-500 text-white">
                                    <MainIcon className="h-6 w-6" />
                                </AvatarFallback>
                            </Avatar>

                            <div className="flex flex-col">
                                {/* Main Title (Vehicle/House/Client Name) */}
                                <h3 className="text-sm font-black text-slate-900 uppercase tracking-tight leading-tight">
                                    {mainTitle}
                                </h3>

                                {/* Status */}
                                <span className="text-[10px] font-bold text-green-600 uppercase tracking-wide mt-1">
                                    {secondaryTitle}
                                </span>
                            </div>
                        </div>

                        {/* IDs Section */}
                        <div className="bg-slate-50 rounded-xl p-3 border border-slate-100 flex items-center justify-between gap-2 overflow-hidden">
                            {/* Reg Number */}
                            <div className="bg-white px-2 py-1 rounded border border-slate-200">
                                <span className="font-black text-slate-800 text-[10px] whitespace-nowrap">{policy.registrationNumber}</span>
                            </div>

                            <div className="h-4 w-px bg-slate-200 shrink-0"></div>

                            {/* Policy ID */}
                            <div className="flex flex-col items-start min-w-0">
                                <span className="text-[8px] font-bold text-slate-400 uppercase tracking-wider">{t("Policy ID", "Policy ID")}</span>
                                <span className="text-xs font-bold text-slate-800 truncate w-full">{policy.policyNumber}</span>
                            </div>
                        </div>
                    </div>
                )
            }}
            items={items}
            onToggleExpand={() => { }}

            financials={[
                {
                    label: <span className="text-xs font-bold text-slate-600 uppercase tracking-wider">{t("Amount (Annual)", "Amount (Annual)")}:</span>,
                    amount: <span className="text-lg font-black text-[#00539F]">{formatPrice ? formatPrice(annualPremium) : policy.premium}</span>,
                    isTotal: false
                },
                // Monthly Breakdown
                monthlyPremium > 0 ? {
                    label: <span className="text-xs font-bold text-slate-600 uppercase tracking-wider">{t("Amount (Per Month)", "Amount (Per Month)")}:</span>,
                    amount: <span className="text-lg font-black text-[#00539F] opacity-80">{formatPrice ? formatPrice(monthlyPremium) : (monthlyPremium).toFixed(2)}</span>,
                    isTotal: false
                } : null
            ].filter(Boolean) as any}

            footer={{
                footerText: "Active Since",
                createdAt: policy.activeDate
            }}

            actions={
                <div className="flex flex-col gap-3 w-full">
                    <Button
                        variant="outline"
                        className="w-full rounded-xl border-2 border-[#00539F] text-[#00539F] font-bold hover:bg-[#00539F]/5"
                        onClick={onMakePayment}
                    >
                        <CreditCard className="mr-2 h-4 w-4" />
                        {t("Make Payment", "Make Payment")}
                    </Button>
                    <div className="grid grid-cols-2 gap-3">
                        <Button variant="ghost" className="rounded-xl bg-slate-50 text-slate-600 font-bold hover:bg-slate-100 border border-slate-200" onClick={onViewDocuments}>{t("Documents", "Documents")}</Button>
                        <Button variant="ghost" className="rounded-xl bg-slate-50 text-slate-600 font-bold hover:bg-slate-100 border border-slate-200" onClick={onMakeClaim}>{t("Make Claim", "Make Claim")}</Button>
                    </div>
                </div>
            }
            className={className}
        />
    );
}
