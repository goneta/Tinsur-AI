import { Quote } from "@/types/quote"
import { useState, useMemo, useEffect } from "react"
import { Button } from "@/components/ui/button"
import { Badge } from "@/components/ui/badge"
import { Avatar, AvatarFallback, AvatarImage } from "@/components/ui/avatar"
import { UniversalEntityCard, EntityItem } from "@/components/shared/universal-entity-card"
import { Loader2, Send, ThumbsUp, ThumbsDown, Archive, Pencil, Trash, Check } from "lucide-react"
import { PremiumPolicyType } from "@/lib/premium-policy-api"
import { QuoteAPI } from "@/lib/api/quotes"
import { formatCurrency, formatDate } from "@/lib/utils"
import { PolicyService } from "@/lib/policy-service-api"

import { cn } from "@/lib/utils"
import { useLanguage } from "@/contexts/language-context"

interface QuoteCardProps {
    quote: Quote
    policyTypeName: string
    premiumPolicyType?: PremiumPolicyType
    allServices?: PolicyService[]
    onServicesUpdated?: (quote: Quote) => void
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
    allServices = [],
    onServicesUpdated,
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
        (quote.included_services || (quote.details as any)?.selected_services || []).map((s: any) =>
            typeof s === 'object' ? s.id || s.name_en : s
        )
    )
    const [isExpanded, setIsExpanded] = useState(false)

    useEffect(() => {
        const next = (quote.details as any)?.selected_services || quote.included_services || [];
        setSelectedServices(
            next.map((s: any) => (typeof s === 'object' ? s.id || s.name_en : s))
        );
    }, [quote.id, quote.included_services, quote.details])

    // Calculate premium dynamically
    const quoteBase = Number(quote.premium_amount || premiumPolicyType?.price || 0)
    const basePolicyPrice = premiumPolicyType?.price ?? quote.premium_amount ?? quoteBase


    // --- Helper Logic ---
    const getStatusColor = (status: string) => {
        switch (status) {
            case 'policy_created':
            case 'approved': return 'bg-green-100 text-green-800'
            case 'accepted': return 'bg-emerald-100 text-emerald-800'
            case 'rejected': return 'bg-red-100 text-red-800'
            case 'sent':
            case 'submitted':
            case 'under_review': return 'bg-blue-100 text-blue-800'
            case 'draft_from_client': return 'bg-purple-100 text-purple-800'
            case 'expired': return 'bg-gray-100 text-gray-800'
            case 'archived': return 'bg-gray-100 text-gray-800'
            default: return 'bg-yellow-100 text-yellow-800'
        }
    }

    const getStatusLabel = () => {
        const s = quote.status as string;
        if (s === 'policy_created') return t("Policy Created", "Policy Created")
        if (s === 'accepted') return t("Accepted", "Accepted")
        if (s === 'approved') return t("Approved", "Approved")
        if (s === 'under_review') return t("Under Review", "Under Review")
        if (s === 'submitted') return t("Submitted", "Submitted")
        if (s === 'draft_from_client') return t("Draft (Client)", "Draft (Client)")
        return t(quote.status, quote.status)
    }

    // --- Map Data to Entity Items ---
    const availableServices = premiumPolicyType?.services || []
    const availableServiceIds = new Set(availableServices.map(s => s.id))
    const serviceCatalog = new Map<string, PolicyService>()
    allServices.forEach(s => serviceCatalog.set(s.id, s))
    availableServices.forEach(s => {
        if (!serviceCatalog.has(s.id)) {
            serviceCatalog.set(s.id, {
                id: s.id,
                company_id: quote.company_id,
                name_en: s.name_en,
                name_fr: s.name_fr,
                description: undefined,
                default_price: Number(s.default_price || 0),
                category: undefined,
                icon_name: undefined,
                is_active: true
            })
        }
    })

    // Combine available services with any extra ones in quote that might not be in type definition (legacy?)
    // Actually, just use available services if present to allow "Show All".
    // If no premiumPolicyType, fall back to quote included only.

    const optionalServices = allServices.filter(s => !availableServiceIds.has(s.id))

    const selectedServiceIds = new Set(
        (quote.included_services || [])
            .map((s: any) => (typeof s === "object" ? s.id : s))
            .filter(Boolean)
    )

    const fallbackIncluded = (availableServices.length === 0 && Array.isArray(quote.included_services))
        ? quote.included_services.map((s: any, idx: number) => ({
            id: s?.id || `included-${idx}`,
            name_en: s?.name_en || s?.name || "Included Service",
            default_price: Number(s?.default_price || 0)
        }))
        : []

    const includedList = availableServices.length > 0 ? availableServices : fallbackIncluded

    const buildOptionalItems = () => {
        const map = new Map<string, PolicyService>()
        optionalServices.forEach((service) => map.set(service.id, service))
        selectedServices.forEach((id) => {
            if (!map.has(id) && serviceCatalog.has(id)) {
                map.set(id, serviceCatalog.get(id)!)
            }
        })
        return Array.from(map.values())
    }

    const optionalList = buildOptionalItems()

    const includedItems = [
        { id: "section-services", label: t("Show All Options", "Show All Options"), isSectionHeader: true },
        { id: "section-included", label: t("Included Services", "Included Services"), isSectionHeader: true },
        ...includedList.map((service: any, idx) => {
            const id = service.id || service.name_en || `included-${idx}`;
            return {
                id,
                label: service.name_en || service.name || t("Included Service", "Included Service"),
                price: Number(service.default_price || 0),
                checked: true,
                disabled: true,
                priceClassName: "text-[10px] uppercase tracking-[0.2em]"
            };
        })
    ]

    const handleOptionalToggle = (serviceId: string, checked: boolean) => {
        if (!(quote.status === 'draft' || quote.status === 'sent' || quote.status === 'draft_from_client')) return;
        setSelectedServices((prev) => {
            const next = checked ? [...prev, serviceId] : prev.filter((id) => id !== serviceId)
            QuoteAPI.update(quote.id, { selected_services: next })
                .then((updated) => onServicesUpdated?.(updated))
                .catch(() => setSelectedServices(prev))
            return next
        })
    }

    const optionalItems = optionalList.map((service) => {
        const isChecked = selectedServices.includes(service.id)
        return {
            id: service.id,
            label: service.name_en,
            price: Number(service.default_price || 0),
            checked: isChecked,
            onCheckedChange: (checked: boolean) => handleOptionalToggle(service.id, checked),
            disabled: !(quote.status === 'draft' || quote.status === 'sent' || quote.status === 'draft_from_client'),
            priceClassName: "text-[10px] uppercase tracking-[0.2em]"
        }
    })

    const items = [...includedItems]
    if (isExpanded) {
        items.push(
            { id: "section-optional", label: t("Optional Services", "Optional Services"), isSectionHeader: true },
            ...optionalItems
        )
    }

    const totalServicesAmount = useMemo(() => {
        const includedTotal = includedList.reduce((sum, s: any) => sum + Number(s.default_price || 0), 0)
        const optionalTotal = optionalServices.reduce((sum, s) => {
            if (selectedServiceIds.has(s.id) || selectedServices.includes(s.id)) {
                return sum + Number(s.default_price || 0)
            }
            return sum
        }, 0)
        return includedTotal + optionalTotal
    }, [includedList, optionalServices, selectedServiceIds, selectedServices])

    const adminFeePercent = Number(quote.admin_fee_percent || 0)
    const discountPercent = Number(quote.admin_discount_percent || quote.discount_percent || 0)
    const taxPercent = Number(quote.tax_percent || 0)

    const adminFeeAmount = (quoteBase + totalServicesAmount) * (adminFeePercent / 100)
    const discountBase = quoteBase + totalServicesAmount + adminFeeAmount
    const discountAmount = discountBase * (discountPercent / 100)
    const taxableBase = discountBase - discountAmount
    const taxAmount = taxableBase * (taxPercent / 100)
    const finalPremium = taxableBase + taxAmount

    const installments = {
        annual: 1,
        monthly: 12,
        quarterly: 4,
        "semi-annual": 2
    } as const
    const frequencyKey = (quote.premium_frequency || "annual") as keyof typeof installments
    const installmentCount = installments[frequencyKey] || 1
    const monthlyAmount = finalPremium / installmentCount
    const annualAmount = monthlyAmount * 12

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
    const financialEntries = [
        { label: t("Base Premium Policy Price", "Base Premium Policy Price"), amount: Number(basePolicyPrice || 0) },
        { label: t("Total Services", "Total Services"), amount: Number(totalServicesAmount || 0) },
        { label: t("Company Admin Fee", "Company Admin Fee"), amount: Number(adminFeeAmount || 0) },
        { label: t("Total Discount", "Total Discount"), amount: -Math.abs(discountAmount || 0) },
        { label: `${t("Govt Tax", "Govt Tax")} (${taxPercent}%)`, amount: Number(taxAmount || 0) },
        { label: t("Amount (Monthly)", "Amount (Monthly)"), amount: monthlyAmount, isTotal: true },
        { label: t("Amount (Annual)", "Amount (Annual)"), amount: annualAmount }
    ]

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

            {['sent', 'draft_from_client', 'submitted', 'under_review'].includes(quote.status as string) && (
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

            {((quote.status as string) === 'policy_created' || (quote.status as string) === 'approved') && (
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
                            <div className="mt-1 text-[10px] uppercase tracking-tight text-gray-400 flex items-center gap-2">
                                <span>{t("Base Price", "Base Price")}:</span>
                                <span className="font-black text-[#00539F]">{formatCurrency(basePolicyPrice)}</span>
                            </div>

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
            financials={financialEntries}
            // Wait, mapping inside the array prop is messy. I will construct the array before.

            footer={{
                validUntil: formatDate(quote.valid_until)
            }}
            actions={renderActions()}
            className={quote.status as string === 'archived' ? 'opacity-60 grayscale' : ''}
            onClick={() => { }}
            onToggleExpand={() => setIsExpanded(!isExpanded)}
            isExpanded={isExpanded}
        />
    )
}

