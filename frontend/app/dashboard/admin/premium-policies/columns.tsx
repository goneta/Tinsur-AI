"use client"

import { ColumnDef } from "@tanstack/react-table"
import { PremiumPolicyType } from "@/lib/premium-policy-api"
import { DataTableColumnHeader } from "@/components/ui/data-table-column-header"
import { Badge } from "@/components/ui/badge"
import { Button } from "@/components/ui/button"
import { Pencil, Trash2 } from "lucide-react"
import { useLanguage } from "@/contexts/language-context"

export const columns = (
    onEdit: (policyType: PremiumPolicyType) => void,
    onDelete: (policyType: PremiumPolicyType) => void,
    formatPrice: (amount: number) => string,
    t: (key: string, fallback: string) => string
): ColumnDef<PremiumPolicyType>[] => [
        {
            accessorKey: "name",
            header: ({ column }) => (
                <DataTableColumnHeader column={column} title={t('common.column.name', 'Policy Name')} />
            ),
        },
        {
            accessorKey: "price",
            header: ({ column }) => (
                <DataTableColumnHeader column={column} title={t('premium_policies.price', 'Price (FCFA)')} />
            ),
            cell: ({ row }) => {
                return <div>{formatPrice(parseFloat(row.getValue("price")))}</div>
            },
        },
        {
            accessorKey: "criteria",
            header: t('premium_policies.criteria_count', 'Criteria Counts'),
            cell: ({ row }) => {
                const criteria = row.original.criteria || []
                return <div>{criteria.length} {t('premium_policies.criteria', 'Criteria')}</div>
            },
            accessorFn: (row) => row.criteria?.length || 0,
        },
        {
            accessorKey: "is_active",
            header: t('common.column.status', 'Status'),
            cell: ({ row }) => {
                const isActive = row.getValue("is_active") as boolean
                return (
                    <Badge variant={isActive ? "default" : "secondary"}>
                        {isActive ? t('status.active', 'Active') : t('status.inactive', 'Inactive')}
                    </Badge>
                )
            },
        },
        {
            id: "actions",
            cell: ({ row }) => (
                <div className="flex items-center gap-2">
                    <Button
                        variant="ghost"
                        size="icon"
                        onClick={() => onEdit(row.original)}
                    >
                        <Pencil className="h-4 w-4" />
                    </Button>
                    <Button
                        variant="ghost"
                        size="icon"
                        className="text-destructive"
                        onClick={() => onDelete(row.original)}
                    >
                        <Trash2 className="h-4 w-4" />
                    </Button>
                </div>
            ),
        },
    ]
