"use client"

import { ColumnDef } from "@tanstack/react-table"
import { Payment } from "@/types/payment"
import { DataTableColumnHeader } from "@/components/ui/data-table-column-header"
import { Button } from "@/components/ui/button"
import { Badge } from "@/components/ui/badge"
import { MoreHorizontal, Eye } from "lucide-react"
import { formatCurrency, formatDate } from "@/lib/utils"

import {
    DropdownMenu,
    DropdownMenuContent,
    DropdownMenuItem,
    DropdownMenuLabel,
    DropdownMenuTrigger,
} from "@/components/ui/dropdown-menu"

// Props for actions
interface PaymentActionsProps {
    row: Payment
    onView: (id: string) => void
    t: (key: string, defaultVal?: string) => string
}

const PaymentActions = ({ row, onView, t }: PaymentActionsProps) => {
    return (
        <DropdownMenu>
            <DropdownMenuTrigger asChild>
                <Button variant="ghost" className="h-8 w-8 p-0">
                    <span className="sr-only">{t('payments.open_menu', 'Open menu')}</span>
                    <MoreHorizontal className="h-4 w-4" />
                </Button>
            </DropdownMenuTrigger>
            <DropdownMenuContent align="end">
                <DropdownMenuLabel>{t('payments.actions', 'Actions')}</DropdownMenuLabel>
                <DropdownMenuItem onClick={() => onView(row.id)}>
                    <Eye className="mr-2 h-4 w-4" /> {t('payments.view_details', 'View Details')}
                </DropdownMenuItem>
                <DropdownMenuItem onClick={() => navigator.clipboard.writeText(row.payment_number)}>
                    {t('payments.copy_number', 'Copy Payment #')}
                </DropdownMenuItem>
            </DropdownMenuContent>
        </DropdownMenu>
    )
}

const getStatusBadge = (status: string) => {
    const variantMap: Record<string, "default" | "secondary" | "destructive" | "outline"> = {
        completed: 'default',
        pending: 'secondary',
        processing: 'secondary',
        failed: 'destructive',
        refunded: 'outline',
    };

    // Custom logic to handle styling that isn't just a variant if needed, 
    // but here we just use the variant map.
    // 'completed' often best as green, which isn't a default variant in some shadcn setups unless customized.
    // We will stick to 'default' or 'outline' for now, or add a class.
    const className = status === 'completed' ? 'bg-green-600 hover:bg-green-700 border-transparent text-primary-foreground' : '';

    return <Badge variant={variantMap[status] || 'default'} className={className}>{status}</Badge>;
}

export const columns = (
    onView: (id: string) => void,
    t: (key: string, defaultVal?: string) => string,
    formatPrice: (amount: number) => string
): ColumnDef<Payment>[] => [
        {
            accessorKey: "payment_number",
            header: ({ column }) => (
                <DataTableColumnHeader column={column} title={t('common.column.payment_number', 'Payment #')} />
            ),
            cell: ({ row }) => <div className="font-medium">{row.getValue("payment_number")}</div>,
        },
        {
            accessorKey: "client_name",
            header: ({ column }) => (
                <DataTableColumnHeader column={column} title={t('common.column.client_name', 'Client')} />
            ),
            cell: ({ row }) => row.getValue("client_name") || "-",
        },
        {
            accessorKey: "policy_number_display", // Using helper field
            header: ({ column }) => (
                <DataTableColumnHeader column={column} title={t('common.column.policy_number_display', 'Policy')} />
            ),
            cell: ({ row }) => row.original.policy_number_display || "-",
        },
        {
            accessorKey: "created_at",
            header: ({ column }) => (
                <DataTableColumnHeader column={column} title={t('common.column.created_at', 'Date')} />
            ),
            cell: ({ row }) => formatDate(row.getValue("created_at")),
        },
        {
            accessorKey: "amount",
            header: ({ column }) => (
                <DataTableColumnHeader column={column} title={t('common.column.amount', 'Amount')} />
            ),
            cell: ({ row }) => formatPrice(row.getValue("amount")),
        },
        {
            accessorKey: "payment_method",
            header: ({ column }) => (
                <DataTableColumnHeader column={column} title={t('common.column.payment_method', 'Method')} />
            ),
            cell: ({ row }) => <div className="capitalize">{(row.getValue("payment_method") as string).replace('_', ' ')}</div>,
        },
        {
            accessorKey: "status",
            header: ({ column }) => (
                <DataTableColumnHeader column={column} title={t('common.column.status', 'Status')} />
            ),
            cell: ({ row }) => getStatusBadge(row.getValue("status")),
        },
        {
            id: "actions",
            cell: ({ row }) => (
                <PaymentActions
                    row={row.original}
                    onView={onView}
                    t={t}
                />
            ),
        },
    ]
