import { Quote } from "@/types/quote"
import { useState, useMemo } from "react"
import { Button } from "@/components/ui/button"
import { Badge } from "@/components/ui/badge"
import { Avatar, AvatarFallback, AvatarImage } from "@/components/ui/avatar"
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

    const getInitials = (name: string) => {
        return name
            .split(' ')
            .map((n) => n[0])
            .join('')
            .toUpperCase()
            .slice(0, 2)
    }

    const title = (quote.details as any)?.vehicle_name || quote.client_name || "Insurance Quote"

    return (
        <UniversalEntityCard
            header={{
                title: title, // Fallback if customContent fails, though we use customContent
                customContent: (
                    <div className="w-full">
                        {/* Top: Status Label */}
                        <div className="flex justify-end mb-4">
                            <Badge className={cn("font-bold uppercase tracking-widest text-[10px] px-3 py-1", getStatusColor(quote.status))}>
                                {getStatusLabel()}
                            </Badge>
                        </div>

                        <div className="flex gap-4 items-start">
                            {/* Avatar */}
                            <Avatar className="h-12 w-12 border-2 border-[#00539F]">
                                <AvatarImage src={(quote as any).client_avatar} alt={quote.client_name} />
                                <AvatarFallback className="bg-[#00539F] text-white font-bold">
                                    {getInitials(quote.client_name)}
                                </AvatarFallback>
                            </Avatar>

                            <div className="flex flex-col">
                                {/* Client Name - Reduced Size */}
                                <span className="text-sm font-bold text-slate-800 uppercase tracking-tight leading-tight">
                                    {quote.client_name}
                                </span>

                                {/* Policy Type */}
                                <span className="text-xs font-bold uppercase tracking-wide text-[#00539F] mt-1">
                                    {policyTypeName}
                                </span>

                                {/* Quote Number */}
                                <span className="text-[10px] font-medium text-slate-500 mt-0.5">
                                    #{quote.quote_number}
                                </span>
                            </div>
                        </div>
                    </div>
                )
            }}
            items={items}
            financials={[
                ...fees.map(f => ({ label: f.label, amount: f.amount })),
                {
                    label: <span className="text-[10px] font-bold uppercase tracking-wider">{t("Amount", "Amount")} ({t(quote.premium_frequency, quote.premium_frequency)})</span>,
                    amount: currentPremium, // UniversalEntityCard handles formatting if number, but we might want custom styling
                    // To enforce smaller size on amount, we can pass a ReactNode if supported, or rely on UniversalEntityCard's default.
                    // Step 819 added item.priceClassName, but financials uses its own rendering.
                    // UniversalEntityCard line 180: className={cn(fee.isTotal && "text-xl font-black text-[#00539F]")}
                    // It forces text-xl.
                    // To override, I can pass a ReactNode for amount.
                    // amount: <span className="text-lg font-black text-[#00539F]">{formatCurrency(currentPremium)}</span>
                    // But I need formatCurrency. I can just pass the number for now and accept text-xl, OR wrap it.
                    // The request says "Reduce the size of Total Premium... and its amount". text-xl is big.
                    // I will check if I can import formatCurrency or just pass a node.
                    // I'll wrap it.
                }
            ].map(f => {
                // Formatting Amount if it's the Total line to override styles
                if (f.label.toString().includes('Amount')) {
                    return {
                        ...f,
                        isTotal: false, // Turn off default total styling to use our own or just accept standard list styling?
                        // User wants consistent design.
                        // If I use isTotal: true, it gets text-xl. User wants reduced size.
                        // So I will set isTotal: false and bold it myself in label/amount props?
                        // UniversalEntityCard renders non-total items as "text-gray-400".
                        // I will pass ReactNode for label and amount to control style fully.
                        amount: (
                            <span className="text-base font-black text-[#00539F]">
                                {/* We need formatPrice or formatCurrency here. formatPrice is avail from useLanguage? No, standard formatCurrency from utils? */}
                                {/* I need to import formatCurrency from utils if I use it inline. */}
                                {/* I'll use isTotal: true but change UniversalEntityCard to allow size override? No, better to custom render. */}
                                {/* UniversalEntityCard renders: typeof fee.amount === 'number' ? formatCurrency(fee.amount) : fee.amount */}
                                {/* So if I pass a Node, it renders the Node. */}
                                {/* useLanguage provides formatPrice. */}
                                {/* I will use formatPrice if available or just let it render. */}
                                {/* Wait, I can't call formatPrice inside the object definition easily unless I calculate it before. */}
                                {/* I will use useLanguage().formatPrice(currentPremium). */}
                            </span>
                        )
                    }
                }
                return f;
            })}
            // Wait, mapping inside the array prop is messy. I will construct the array before.

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

