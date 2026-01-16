import { PremiumPolicyType } from "@/lib/premium-policy-api"
import { Button } from "@/components/ui/button"
import { UniversalEntityCard, EntityItem } from "@/components/shared/universal-entity-card"
import { Check } from "lucide-react"

interface PremiumPolicyCardProps {
    policy: PremiumPolicyType
    onSelect: (policy: PremiumPolicyType) => void
    isSelected?: boolean
    isRecommended?: boolean
}

export function PremiumPolicyCard({ policy, onSelect, isSelected, isRecommended }: PremiumPolicyCardProps) {

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

