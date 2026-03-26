"use client"

import { ColumnDef } from "@tanstack/react-table"
import { Claim } from "@/types/claim"
import { DataTableColumnHeader } from "@/components/ui/data-table-column-header"
import { Button } from "@/components/ui/button"
import { MoreHorizontal, Eye } from "lucide-react"
import { format } from "date-fns"
import { ClaimStatusBadge } from "@/components/claims/claim-status-badge"

import {
    DropdownMenu,
    DropdownMenuContent,
    DropdownMenuItem,
    DropdownMenuLabel,
    DropdownMenuSeparator,
    DropdownMenuTrigger,
} from "@/components/ui/dropdown-menu"

// ... imports

// Props for actions
interface ClaimActionsProps {
    row: Claim
    onView: (claim: Claim) => void
    t: (key: string, defaultVal?: string) => string
}

const ClaimActions = ({ row, onView, t }: ClaimActionsProps) => {
    return (
        <DropdownMenu>
            <DropdownMenuTrigger asChild>
                <Button variant="ghost" className="h-8 w-8 p-0">
                    <span className="sr-only">{t('claims.open_menu', 'Open menu')}</span>
                    <MoreHorizontal className="h-4 w-4" />
                </Button>
            </DropdownMenuTrigger>
            <DropdownMenuContent align="end">
                <DropdownMenuLabel>{t('claims.actions', 'Actions')}</DropdownMenuLabel>
                <DropdownMenuItem onClick={() => onView(row)}>
                    <Eye className="mr-2 h-4 w-4" />
                    {t('claims.view_details', 'View Details')}
                </DropdownMenuItem>
                <DropdownMenuItem onClick={() => navigator.clipboard.writeText(row.claim_number)}>
                    {t('claims.copy_number', 'Copy Claim Number')}
                </DropdownMenuItem>
            </DropdownMenuContent>
        </DropdownMenu>
    )
}

const formatCurrency = (amount: number) => {
    return new Intl.NumberFormat('fr-SN', { style: 'currency', currency: 'XOF' }).format(amount);
};

export const columns = (
    onView: (claim: Claim) => void,
    t: (key: string, defaultVal?: string) => string,
    formatPrice: (amount: number) => string
): ColumnDef<Claim>[] => [
        {
            accessorKey: "claim_number",
            header: ({ column }) => (
                <DataTableColumnHeader column={column} title={t('claims.claim_number', 'Claim Number')} />
            ),
            cell: ({ row }) => <div className="font-medium">{row.getValue("claim_number")}</div>,
        },
        {
            accessorKey: "incident_date",
            header: ({ column }) => (
                <DataTableColumnHeader column={column} title={t('claims.incident_date', 'Incident Date')} />
            ),
            cell: ({ row }) => format(new Date(row.getValue("incident_date")), 'MMM d, yyyy'),
        },
        {
            accessorKey: "incident_description",
            header: ({ column }) => (
                <DataTableColumnHeader column={column} title={t('claims.description', 'Description')} />
            ),
            cell: ({ row }) => (
                <div className="max-w-[300px] truncate" title={row.getValue("incident_description")}>
                    {row.getValue("incident_description")}
                </div>
            ),
        },
        {
            accessorKey: "claim_amount",
            header: ({ column }) => (
                <DataTableColumnHeader column={column} title={t('claims.amount', 'Amount')} />
            ),
            cell: ({ row }) => formatPrice(row.getValue("claim_amount")),
        },
        {
            accessorKey: "status",
            header: ({ column }) => (
                <DataTableColumnHeader column={column} title={t('claims.status', 'Status')} />
            ),
            cell: ({ row }) => <ClaimStatusBadge status={row.getValue("status")} />,
        },
        {
            id: "actions",
            cell: ({ row }) => (
                <ClaimActions
                    row={row.original}
                    onView={onView}
                    t={t}
                />
            ),
        },
    ]
