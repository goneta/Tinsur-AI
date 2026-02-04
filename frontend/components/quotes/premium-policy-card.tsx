import { PremiumPolicyType } from "@/lib/premium-policy-api"
import { Button } from "@/components/ui/button"
import { Badge } from "@/components/ui/badge"
import { UniversalEntityCard, EntityItem } from "@/components/shared/universal-entity-card"
import { Check } from "lucide-react"

interface PremiumPolicyCardProps {
    policy: PremiumPolicyType & { company_name?: string; company_primary_color?: string }
    onSelect: (policy: PremiumPolicyType) => void
    isSelected?: boolean
    isRecommended?: boolean
}

export function PremiumPolicyCard({ policy, onSelect, isSelected, isRecommended }: PremiumPolicyCardProps) {

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

    // Map features to items
    const items: EntityItem[] = (policy.services || []).map((service: any, idx: number) => ({
        id: `svc-${idx}`,
        label: service.name_en,
        isChecked: true
    }))

    return (
        <UniversalEntityCard
            header={{
                title: policy.name,
                subtitle: policy.tagline,
                status: isRecommended ? "RECOMMENDED" : (policy.is_featured ? "BEST SELLER" : undefined),
                statusColor: isRecommended ? "bg-yellow-500 text-white border-none" : "bg-black text-white"
            }}
            extra={policy.company_name ? (
                <Badge
                    className="text-[10px] font-black uppercase tracking-widest px-2 py-1"
                    style={policy.company_primary_color ? {
                        backgroundColor: policy.company_primary_color,
                        borderColor: policy.company_primary_color,
                        color: getBadgeTextColor(policy.company_primary_color)
                    } : undefined}
                    variant={policy.company_primary_color ? undefined : 'outline'}
                >
                    {policy.company_name}
                </Badge>
            ) : undefined}
            items={items}
            financials={[
                { label: "Price", amount: policy.price }, // Explicitly show price, or maybe in total? Use total for prominence.
                { label: "Per Month", amount: policy.price, isTotal: true }
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

