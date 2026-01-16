"use client"

import { Badge } from "@/components/ui/badge"

interface ClaimStatusBadgeProps {
    status: string
}

export function ClaimStatusBadge({ status }: ClaimStatusBadgeProps) {
    let variant: "default" | "secondary" | "destructive" | "outline" = "outline"
    let className = ""

    switch (status.toLowerCase()) {
        case 'submitted':
            variant = "secondary"
            className = "bg-blue-100 text-blue-800 hover:bg-blue-100" // Info/New
            break
        case 'under_review':
            variant = "secondary"
            className = "bg-yellow-100 text-yellow-800 hover:bg-yellow-100" // Warning/Pending
            break
        case 'approved':
            variant = "default"
            className = "bg-green-100 text-green-800 hover:bg-green-100 border-green-200" // Success
            break
        case 'paid':
            variant = "default"
            className = "bg-emerald-100 text-emerald-800 hover:bg-emerald-100 border-emerald-200" // Completed
            break
        case 'rejected':
            variant = "destructive"
            break
        case 'closed':
            variant = "outline"
            className = "text-gray-500"
            break
    }

    // Capitalize for display
    const label = status.split('_').map(word => word.charAt(0).toUpperCase() + word.slice(1)).join(' ')

    return (
        <Badge variant={variant} className={className}>
            {label}
        </Badge>
    )
}
