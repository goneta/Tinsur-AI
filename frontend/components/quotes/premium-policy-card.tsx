import { PremiumPolicyType } from "@/lib/premium-policy-api"
import { Button } from "@/components/ui/button"
import { Badge } from "@/components/ui/badge"
import { formatCurrency } from "@/lib/utils"
import { UniversalEntityCard, EntityItem } from "@/components/shared/universal-entity-card"
import { Check } from "lucide-react"
import { useLanguage } from "@/contexts/language-context"

interface PremiumPolicyCardProps {
    policy: PremiumPolicyType & { company_name?: string; company_primary_color?: string }
    onSelect: (policy: PremiumPolicyType) => void
    isSelected?: boolean
    isRecommended?: boolean
}

export function PremiumPolicyCard({ policy, onSelect, isSelected, isRecommended }: PremiumPolicyCardProps) {
    const { language } = useLanguage();

    const getBadgeTextColor = (hex?: string) => {
        if (!hex) return '#ffffff';
        const cleaned = hex.replace('#', '');
        if (cleaned.length !== 6) return '#ffffff';
        const r = parseInt(cleaned.slice(0, 2), 16);
        const g = parseInt(cleaned.slice(2, 4), 16);
        const b = parseInt(cleaned.slice(4, 6), 16);
        const yiq = (r * 299 + g * 587 + b * 114) / 1000;
        return yiq >= 180 ? '#111827' : '#ffffff';
    };

    const localeMap: Record<string, string> = {
        'en': 'en-GB',
        'fr': 'fr-FR',
        'es': 'es-ES'
    };
    const locale = localeMap[language] || 'en-GB';
    const currency = policy.company_currency || (typeof window !== 'undefined' ? (localStorage.getItem('app_currency') || 'XOF') : 'XOF');
    const formattedPrice = formatCurrency(Number(policy.price ?? 0), currency, locale);

    const badgeLabel = isRecommended ? "RECOMMENDED" : policy.is_featured ? "BEST SELLER" : undefined;

    // Map features to items
    const items: EntityItem[] = (policy.services || []).map((service: any, idx: number) => ({
        id: `svc-${idx}`,
        label: service.name_en,
        isChecked: true
    }));

    return (
        <UniversalEntityCard
            header={{
                title: policy.name,
                customContent: (
                    <div className="space-y-3">
                        <div className="flex items-start justify-between gap-4">
                            <div className="space-y-2">
                                {policy.company_name && (
                                    <Badge
                                        className="text-[10px] font-black uppercase tracking-widest px-3 py-1"
                                        style={policy.company_primary_color ? {
                                            backgroundColor: policy.company_primary_color,
                                            borderColor: policy.company_primary_color,
                                            color: getBadgeTextColor(policy.company_primary_color)
                                        } : undefined}
                                    >
                                        {policy.company_name}
                                    </Badge>
                                )}
                                <h3 className="text-2xl font-black text-slate-900">{policy.name}</h3>
                                <p className="text-lg font-black text-slate-900">{formattedPrice}</p>
                            </div>
                            {badgeLabel && (
                                <Badge className={`text-[10px] font-black uppercase tracking-widest px-3 py-1 ${isRecommended ? 'bg-yellow-500 text-white' : 'bg-black text-white'}`}>
                                    {badgeLabel}
                                </Badge>
                            )}
                        </div>
                        {policy.tagline && (
                            <p className="text-sm font-medium text-gray-500">{policy.tagline}</p>
                        )}
                    </div>
                )
            }}
            items={items}
            financials={[
                { label: "Price", amount: formattedPrice },
                { label: "Per Month", amount: formattedPrice, isTotal: true }
            ]}
            isSelected={isSelected}
            onClick={() => onSelect(policy)}
            actions={
                <Button
                    className={`w-full rounded-xl font-bold py-6 ${isSelected ? 'bg-[#00539F] hover:bg-blue-800' : 'bg-slate-900 hover:bg-black'} text-white transition-all`}
                    onClick={(e) => { e.stopPropagation(); onSelect(policy); }}
                >
                    {isSelected ? 'Selected' : 'Select Policy'}
                </Button>
            }
        />
    )
}

