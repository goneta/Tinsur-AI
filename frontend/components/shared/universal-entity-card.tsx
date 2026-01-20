import React from "react"
import { Badge } from "@/components/ui/badge"
import { Card } from "@/components/ui/card"
import { cn, formatCurrency } from "@/lib/utils"
import { Check, ShieldCheck } from "lucide-react"
import { useLanguage } from "@/contexts/language-context"

export interface EntityItem {
    id: string
    label: React.ReactNode
    value?: string
    price?: number
    isChecked?: boolean // If true, shows a checkmark (visual or interactive)
    icon?: React.ReactNode
    checkClassName?: string // Custom class for check container
    iconClassName?: string // Custom class for check icon
    isSectionHeader?: boolean // If true, renders as a section title
    priceClassName?: string // Custom class for price text
}

export interface UniversalEntityCardProps {
    header: {
        title: string
        subtitle?: string
        status?: string
        statusColor?: string // Optional override
        icon?: any
        badgeText?: string
        customContent?: React.ReactNode
    }
    items?: {
        id: string
        label: React.ReactNode
        price?: number
        checked?: boolean
        disabled?: boolean
        onCheckedChange?: (checked: boolean) => void
        checkClassName?: string
        iconClassName?: string
        isSectionHeader?: boolean
        priceClassName?: string
    }[]
    financials?: {
        label: React.ReactNode
        amount: string | number | React.ReactNode
        isTotal?: boolean
    }[]
    footer?: {
        validUntil?: string
        createdAt?: string
        footerText?: string
    } | React.ReactNode
    actions?: React.ReactNode
    onToggleExpand?: () => void
    isExpanded?: boolean
    className?: string
    onClick?: () => void
    isSelected?: boolean
}

export function UniversalEntityCard({
    header,
    items = [],
    financials = [],
    footer,
    actions,
    onToggleExpand,
    isExpanded,
    className,
    onClick,
    isSelected
}: UniversalEntityCardProps) {
    const { t } = useLanguage()

    // Helper to determine status color if not provided
    const getStatusColor = (status: string) => {
        if (header.statusColor) return header.statusColor;
        switch (status?.toLowerCase()) {
            case 'active': return 'bg-green-100 text-green-700';
            case 'approved': return 'bg-blue-100 text-blue-700';
            case 'draft': return 'bg-gray-100 text-gray-700';
            case 'pending': return 'bg-orange-100 text-orange-700';
            case 'rejected': return 'bg-red-100 text-red-700';
            default: return 'bg-gray-100 text-gray-700';
        }
    };

    const Icon = header.icon || ShieldCheck;

    return (
        <Card
            className={cn(
                "relative overflow-hidden flex flex-col bg-white shadow-lg border-0 rounded-[2rem] w-full transition-all duration-300",
                isSelected ? "ring-4 ring-primary ring-opacity-50" : "hover:shadow-xl",
                className
            )}
            onClick={onClick}
        >
            <div className="p-6 flex flex-col h-full">

                {/* Header Section */}
                {header.customContent ? (
                    <div className="mb-6">
                        {header.customContent}
                    </div>
                ) : (
                    <div className="flex justify-between items-start mb-6">
                        <div className="flex items-start gap-4">
                            {/* Icon Circle */}
                            <div className="h-12 w-12 rounded-full bg-[#00539F] flex items-center justify-center shrink-0">
                                <Icon className="h-6 w-6 text-white" />
                            </div>

                            <div className="flex flex-col">
                                <h3 className="text-xl font-black text-slate-900 uppercase tracking-tight leading-tight">
                                    {header.title}
                                </h3>
                                {header.subtitle && (
                                    <span className={cn("text-sm font-bold uppercase tracking-wide text-[#00539F]")}>
                                        {header.subtitle}
                                    </span>
                                )}
                            </div>
                        </div>

                        <div className="flex flex-col items-end gap-2">
                            {header.badgeText && (
                                <Badge variant="secondary" className="bg-blue-50 text-blue-700 hover:bg-blue-100 font-bold px-2 py-0.5 text-[10px] uppercase tracking-wider">
                                    {header.badgeText}
                                </Badge>
                            )}
                            {header.status && (
                                <Badge className={cn("font-bold uppercase tracking-widest text-[10px] px-3 py-1", getStatusColor(header.status))}>
                                    {header.status}
                                </Badge>
                            )}
                        </div>
                    </div>
                )}

                {/* Items List */}
                <div className="flex-1 space-y-3 mb-8">
                    {items.map((item, idx) => {
                        if (item.isSectionHeader) {
                            return (
                                <div key={item.id || idx} className="pt-2 pb-1">
                                    <h4 className="text-[10px] font-bold text-gray-400 uppercase tracking-widest border-b border-gray-100 pb-1">
                                        {item.label}
                                    </h4>
                                </div>
                            );
                        }

                        return (
                            <div key={item.id || idx} className="flex items-start justify-between group">
                                <div className="flex items-start gap-3">
                                    <div
                                        onClick={() => !item.disabled && item.onCheckedChange?.(!item.checked)}
                                        className={cn(
                                            "mt-0.5 rounded-full flex items-center justify-center border-2 transition-colors",
                                            item.checkClassName || "h-5 w-5",
                                            item.checked ? "bg-black border-black" : "bg-white border-gray-200",
                                            !item.disabled && "cursor-pointer"
                                        )}
                                    >
                                        {item.checked && <Check className={cn("text-white stroke-[4]", item.iconClassName || "h-3.5 w-3.5")} />}
                                    </div>
                                    <span className={cn("text-sm font-bold text-slate-700 leading-tight", item.disabled && "text-gray-400")}>
                                        {item.label}
                                    </span>
                                </div>

                                {/* Price for item if applicable */}
                                {item.price !== undefined && (
                                    <span className={cn("text-sm font-black text-[#00539F]", item.priceClassName)}>
                                        {item.price > 0 ? `+${formatCurrency(item.price)}` : 'Incl.'}
                                    </span>
                                )}
                            </div>
                        );
                    })}
                    {/* Expand/Collapse Toggle if needed */}
                    {onToggleExpand && (
                        <button onClick={onToggleExpand} className="text-xs font-bold text-gray-400 uppercase tracking-widest hover:text-[#00539F] transition-colors mt-2">
                            {isExpanded ? t("- Show Less", "- Show Less") : t("Show All Options", "Show All Options")}
                        </button>
                    )}
                </div>

                {/* Financial Breakdown */}
                {financials.length > 0 && (
                    <div className="border-t border-gray-100 pt-4 mb-4 space-y-2">
                        {financials.map((fee, idx) => (
                            <div key={idx} className={cn("flex justify-between items-center text-xs font-bold uppercase tracking-wide", fee.isTotal ? "text-slate-900 text-sm mt-3 pt-3 border-t border-dashed border-gray-200" : "text-gray-400")}>
                                <span>{fee.label}</span>
                                <span className={cn(fee.isTotal && "text-xl font-black text-[#00539F]")}>{typeof fee.amount === 'number' ? formatCurrency(fee.amount) : fee.amount}</span>
                            </div>
                        ))}
                    </div>
                )}

                {/* Footer and Actions */}
                <div className="mt-auto">
                    {React.isValidElement(footer) ? (
                        footer
                    ) : (
                        footer && typeof footer === 'object' && ('validUntil' in footer || 'createdAt' in footer) && (
                            <div className="flex justify-between items-end mb-4 border-t border-gray-100 pt-4">
                                {(footer as any).createdAt && (
                                    <div className="text-left">
                                        <span className="text-[10px] uppercase tracking-widest font-bold text-gray-400 block">{t("Created", "Created")}</span>
                                        <span className="text-xs font-black text-slate-900">{(footer as any).createdAt}</span>
                                    </div>
                                )}
                                {(footer as any).validUntil && (
                                    <div className="text-right">
                                        <span className="text-[10px] uppercase tracking-widest font-bold text-gray-400 block">{t("Valid Until", "Valid Until")}</span>
                                        <span className="text-xs font-black text-slate-900">{(footer as any).validUntil}</span>
                                    </div>
                                )}
                            </div>
                        )
                    )}

                    {actions && (
                        <div className="pt-2">
                            {actions}
                        </div>
                    )}
                </div>
            </div>
        </Card>
    )
}
