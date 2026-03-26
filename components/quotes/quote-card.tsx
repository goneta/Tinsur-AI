import { Quote } from "@/types/quote"
import { useState, useMemo } from "react"
import { Button } from "@/components/ui/button"
import { UniversalEntityCard, EntityItem } from "@/components/shared/universal-entity-card"
import { Loader2, Send, ThumbsUp, ThumbsDown, Archive, Pencil, Trash, Check } from "lucide-react"
import { PremiumPolicyType } from "@/lib/premium-policy-api"

import { cn } from "@/lib/utils"
import { useLanguage } from "@/contexts/language-context"

interface QuoteCardProps {
    quote: Quote
    policyTypeName: string
    premiumPolicyType?: PremiumPolicyType
    onSend: (quote: Quote) => void
    onApprove: (quote: Quote) => void
    onReject: (quote: Quote) => void
    onArchive?: (quote: Quote) => void
    onDelete?: (quote: Quote) => void
    onEdit?: (quote: Quote) => void
    loadingId?: string | null
}

export function QuoteCard({
    quote,
    policyTypeName,
    premiumPolicyType,
    onSend,
    onApprove,
    onReject,
    onArchive,
    onDelete,
    onEdit,
    loadingId
}: QuoteCardProps) {
    const { t } = useLanguage()
    const isProcessing = loadingId === quote.id
    const [selectedServices, setSelectedServices] = useState<string[]>(
        quote.included_services || (quote.details as any)?.selected_services || []
    )
    const [isExpanded, setIsExpanded] = useState(false)

    // Calculate premium dynamically
    const basePremium = Number(quote.final_premium) || 0 // Assuming final_premium in quote includes selected services at time of creation? 
    // Actually, if we change services, we should start from a base + additives.
    // If we don't know the Base Premium (without services), this is hard.
    // However, usually Quote Premium = Base + Services.
    // Let's try to recalculate: 
    // If we assume `premiumPolicyType.price` is the base for the policy type?
    // Or if `quote.details.base_premium` exists?
    // Fallback: Use quote premium and assume it matches current selection, then adjust diff.

    // Better approach: Calculate total from scratch if we have all info.
    // Base = PremiumType Price? Or Quote Base?
    // Let's try to find a base.

    const quoteBase = Number((quote.details as any)?.base_premium) || Number(premiumPolicyType?.price) || (Number(quote.final_premium) - 0) // Fallback

    const currentPremium = useMemo(() => {
        if (!premiumPolicyType?.services) return Number(quote.final_premium);

        const servicesTotal = selectedServices.reduce((sum: number, serviceId: string) => {
            const service = premiumPolicyType.services.find(s => s.id === serviceId || s.name_en === serviceId);
            return sum + (service?.default_price || 0);
        }, 0);

        return quoteBase + servicesTotal;
    }, [quoteBase, selectedServices, premiumPolicyType, quote.final_premium]);


    // --- Helper Logic ---
    const getStatusColor = (status: string) => {
        switch (status) {
            case 'policy_created':
            case 'accepted': return 'bg-green-100 text-green-800'
            case 'rejected': return 'bg-red-100 text-red-800'
            case 'sent': return 'bg-blue-100 text-blue-800'
            case 'draft_from_client': return 'bg-purple-100 text-purple-800'
            case 'expired': return 'bg-gray-100 text-gray-800'
            case 'archived': return 'bg-gray-100 text-gray-800'
            default: return 'bg-yellow-100 text-yellow-800'
        }
    }

    const getStatusLabel = () => {
        const s = quote.status as string;
        if (s === 'policy_created' || s === 'accepted') {
            if (quote.created_by_name === 'Online' || quote.created_by_name === 'Unknown') {
                return t("Approved (Co)", "Approved (Co)")
            } else {
                return t("Approved (Cli)", "Approved (Cli)")
            }
        }
        if (s === 'draft_from_client') return t("Draft (Client)", "Draft (Client)")
        return t(quote.status, quote.status)
    }

    // --- Map Data to Entity Items ---
    const availableServices = premiumPolicyType?.services || []

    // Combine available services with any extra ones in quote that might not be in type definition (legacy?)
    // Actually, just use available services if present to allow "Show All".
    // If no premiumPolicyType, fall back to quote included only.

    const displayServices = isExpanded && availableServices.length > 0
        ? availableServices
        : (availableServices.length > 0
            ? availableServices.filter(s => selectedServices.includes(s.id) || selectedServices.includes(s.name_en))
            : (quote.included_services?.map(s => ({ id: s, name_en: s, default_price: 0 })) || [])
        ); // Fallback for legacy

    const items: EntityItem[] = displayServices.map((service: any, idx) => {
        const id = service.id || service.name_en || `svc-${idx}`;
        const isChecked = selectedServices.includes(id) || selectedServices.includes(service.name_en);

        return {
            id: id,
            label: service.name_en || service,
            price: service.default_price,
            checked: isChecked,
            onCheckedChange: (checked: boolean) => {
                if (quote.status !== 'draft') return; // Read only if not draft
                const val = id; // prefer ID
                setSelectedServices((prev: string[]) =>
                    checked ? [...prev, val] : prev.filter((v: string) => v !== val && v !== service.name_en)
                )
            },
            disabled: quote.status !== 'draft'
        };
    });

    // 2. Criteria / Details (Append to items or separate?)
    // UniversalEntityCard accepts one list. Let's keep criteria hidden or separate?
    // Reference image shows Services list.
    // Let's append Criteria but make them read-only/checked.
    if (quote.details && Object.keys(quote.details).length > 0) {
        Object.entries(quote.details).forEach(([key, value], idx) => {
            if (['vehicle_name', 'final_premium', 'base_premium', 'selected_services', 'vehicle_id'].includes(key)) return;
            // items.push({ ... }) // Maybe skip details for cleaner card matching reference?
            // Reference image mainly shows services.
        })
    }

    // --- Financials ---
    const fees = [
        { label: t("Company Admin Fee", "Company Admin Fee"), amount: Number(quote.admin_fee || 0) },
        { label: t("Govt Tax (0%)", "Govt Tax (0%)"), amount: Number(quote.tax_amount || 0) }
    ].filter(f => f.amount >= 0)

    // --- Actions ---
    const renderActions = () => (
        <div className="grid grid-cols-2 gap-2 w-full">
            {quote.status === 'draft' && (
                <Button
                    className="col-span-2 w-full bg-[#00539F] hover:bg-blue-800 text-white font-bold rounded-xl"
                    onClick={(e) => { e.stopPropagation(); onSend(quote); }}
                    disabled={isProcessing}
                >
                    {isProcessing ? <Loader2 className="mr-2 h-4 w-4 animate-spin" /> : <Send className="mr-2 h-4 w-4" />}
                    {t("Send to Client", "Send to Client")}
                </Button>
            )}

            {['sent', 'draft_from_client'].includes(quote.status as string) && (
                <>
                    <Button
                        className="bg-green-600 hover:bg-green-700 text-white font-bold rounded-xl"
                        onClick={(e) => { e.stopPropagation(); onApprove(quote); }}
                        disabled={isProcessing}
                    >
                        {isProcessing ? <Loader2 className="mr-2 h-4 w-4 animate-spin" /> : <ThumbsUp className="mr-2 h-4 w-4" />}
                        {t("Approve", "Approve")}
                    </Button>
                    <Button
                        variant="outline"
                        className="border-red-200 text-red-600 hover:bg-red-50 font-bold rounded-xl"
                        onClick={(e) => { e.stopPropagation(); onReject(quote); }}
                        disabled={isProcessing}
                    >
                        {isProcessing ? <Loader2 className="mr-2 h-4 w-4 animate-spin" /> : <ThumbsDown className="mr-2 h-4 w-4" />}
                        {t("Reject", "Reject")}
                    </Button>
                </>
            )}

            {((quote.status as string) === 'policy_created' || (quote.status as string) === 'accepted') && (
                <div className="col-span-2 w-full p-3 bg-green-50 text-green-700 rounded-xl text-center text-sm font-black border border-green-100 flex items-center justify-center gap-2 uppercase tracking-wide">
                    <Check className="h-4 w-4 stroke-[3]" /> {t("Active Policy", "Active Policy")}
                </div>
            )}

            {/* Edit/Delete for Drafts */}
            {['draft', 'sent', 'draft_from_client'].includes(quote.status as string) && (
                <div className="col-span-2 flex justify-center gap-4 mt-2">
                    {onEdit && (
                        <button onClick={(e) => { e.stopPropagation(); onEdit(quote) }} className="text-gray-400 hover:text-blue-600 transition-colors">
                            <Pencil className="h-4 w-4" />
                        </button>
                    )}
                    {onDelete && (
                        <button onClick={(e) => { e.stopPropagation(); onDelete(quote) }} className="text-gray-400 hover:text-red-600 transition-colors">
                            <Trash className="h-4 w-4" />
                        </button>
                    )}
                </div>
            )}
        </div>
    )

    const title = (quote.details as any)?.vehicle_name || quote.client_name || "Insurance Quote"
    const subtitle = (quote.details as any)?.vehicle_name ? quote.client_name : `${policyTypeName} #${quote.quote_number}`

    return (
        <UniversalEntityCard
            header={{
                title: title,
                subtitle: subtitle,
                status: getStatusLabel(),
                statusColor: getStatusColor(quote.status)
            }}
            items={items}
            financials={[
                ...fees.map(f => ({ label: f.label, amount: f.amount })),
                {
                    label: `${t("Total Premium", "Total Premium")} (${t(quote.premium_frequency, quote.premium_frequency)})`,
                    amount: currentPremium,
                    isTotal: true
                }
            ]}
            footer={{
                validUntil: new Date(quote.valid_until).toLocaleDateString()
            }}
            actions={renderActions()}
            className={quote.status as string === 'archived' ? 'opacity-60 grayscale' : ''}
            onClick={() => { }}
            onToggleExpand={() => setIsExpanded(!isExpanded)}
            isExpanded={isExpanded}
        />
    )
}

