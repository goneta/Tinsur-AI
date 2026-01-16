
import React from 'react';
import { Card } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';

import { Check, FileText, Upload, ShieldCheck, CheckCircle2, CreditCard } from 'lucide-react';
import { useLanguage } from '@/contexts/language-context';

interface PolicyFeature {
    id: string;
    label: string;
    included: boolean;
}

interface PolicyCardProps {
    policy: {
        id: string;
        vehicleName: string;
        registrationNumber: string;
        policyNumber: string;
        status: string;
        activeDate: string;
        premium: string;
        coverLevel: string;
        features: PolicyFeature[];
    };
    onViewDocuments: () => void;
    onMakeClaim: () => void;
    onMakePayment: () => void;
    onViewPayment?: () => void;
    className?: string;
}

export function PolicyCard({ policy, onViewDocuments, onMakeClaim, onMakePayment, onViewPayment, className }: PolicyCardProps) {
    const { t } = useLanguage();
    return (
        <Card className={`rounded-[30px] overflow-hidden border border-gray-100 shadow-xl bg-white ${className}`}>
            <div className="p-8 space-y-8">
                {/* Header */}
                <div className="flex items-start justify-between">
                    <div className="flex items-center gap-4">
                        <div className="h-14 w-14 bg-[#00C853] rounded-full flex items-center justify-center shadow-lg shadow-green-100">
                            <CheckCircle2 className="h-8 w-8 text-white" />
                        </div>
                        <div>
                            <h2 className="text-lg font-black text-gray-900 uppercase tracking-tight">{t(policy.vehicleName, policy.vehicleName)}</h2>
                            <p className="text-[#00C853] font-bold text-xs tracking-widest uppercase">{t("TINSUR.AI POLICY ACTIVE", "TINSUR.AI POLICY ACTIVE")}</p>
                        </div>
                    </div>
                    <Badge className="bg-[#E8F5E9] text-[#00C853] hover:bg-[#E8F5E9] border-none px-4 py-1.5 font-black text-xs uppercase rounded-full">
                        {t(policy.coverLevel, policy.coverLevel)}
                    </Badge>
                </div>

                {/* IDs Section */}
                <div className="flex flex-wrap items-center gap-6 bg-gray-50/50 p-4 rounded-2xl border border-gray-100/50">
                    <div className="bg-white px-4 py-2 rounded-xl border border-gray-200 shadow-sm">
                        <span className="font-black text-gray-900 tracking-wider text-[10px]">{policy.registrationNumber}</span>
                    </div>
                    <div className="h-8 w-px bg-gray-200"></div>
                    <div>
                        <p className="text-[10px] font-bold text-gray-400 uppercase tracking-widest">{t("POLICY ID", "POLICY ID")}</p>
                        <p className="font-bold text-gray-900 font-mono text-sm">{policy.policyNumber}</p>
                    </div>
                    <div className="h-8 w-px bg-gray-200"></div>
                    <div>
                        <p className="text-[10px] font-bold text-gray-400 uppercase tracking-widest">{t("REFERENCE", "REFERENCE")}</p>
                        <p className="font-bold text-gray-900 font-mono text-sm">{policy.id.toUpperCase().slice(0, 8)}</p>
                    </div>
                </div>

                {/* Main Action - Make Payment */}
                <Button
                    variant="outline"
                    className="w-full rounded-2xl border-2 border-[#00539F] text-[#00539F] font-bold h-12 hover:bg-[#00539F]/5 transition-all text-base"
                    onClick={onMakePayment}
                >
                    <CreditCard className="mr-2 h-5 w-5" />
                    {t("Make Payment", "Make Payment")}
                </Button>

                {/* Features List */}
                <div className="space-y-4 py-2">
                    {policy.features.slice(0, 5).map((feature, idx) => (
                        <div key={idx} className="flex items-center justify-between group">
                            <div className="flex items-center gap-3">
                                <div className={`h-5 w-5 rounded-full flex items-center justify-center ${feature.included ? 'bg-[#00C853]/10 text-[#00C853]' : 'bg-gray-100 text-gray-300'}`}>
                                    <Check className="h-3 w-3" />
                                </div>
                                <span className={`font-bold text-sm ${feature.included ? 'text-gray-700' : 'text-gray-400 decoration-slate-300 line-through'}`}>
                                    {feature.label}
                                </span>
                            </div>
                            {feature.included && (
                                <span className="text-[10px] font-black text-gray-300 uppercase tracking-widest opacity-0 group-hover:opacity-100 transition-opacity">{t("Included", "Included")}</span>
                            )}
                        </div>
                    ))}
                    {policy.features.length > 5 && (
                        <div className="flex justify-center pt-2">
                            <span className="text-gray-400 text-xs font-bold cursor-pointer hover:text-[#00539F]">
                                + {policy.features.length - 5} {t("more features", "more features")}
                            </span>
                        </div>
                    )}
                </div>

                {/* Footer Info */}
                <div className="flex items-end justify-between pt-6 border-t border-gray-100">
                    <div>
                        <p className="text-[10px] font-bold text-gray-400 uppercase tracking-widest mb-1">{t("Active Since", "Active Since")}</p>
                        <p className="font-black text-gray-900 text-lg">{policy.activeDate}</p>
                    </div>
                    <div className="text-right">
                        <p className="text-[10px] font-bold text-gray-400 uppercase tracking-widest mb-1">{t("Premium", "Premium")}</p>
                        <p className="font-black text-[#00539F] text-xl">{policy.premium}</p>
                    </div>
                </div>

                {/* Bottom Actions */}
                <div className="grid grid-cols-2 gap-4">
                    <Button
                        variant="ghost"
                        className="bg-gray-50 hover:bg-gray-100 text-gray-600 font-bold h-14 rounded-2xl border border-gray-200"
                        onClick={onViewDocuments}
                    >
                        {t("Documents", "Documents")}
                    </Button>
                    <Button
                        variant="ghost"
                        className="bg-gray-50 hover:bg-gray-100 text-gray-600 font-bold h-14 rounded-2xl border border-gray-200"
                        onClick={onMakeClaim}
                    >
                        {t("Make Claim", "Make Claim")}
                    </Button>
                </div>
            </div>
        </Card>
    );
}
