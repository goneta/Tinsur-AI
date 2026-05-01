"use client"

import { ColumnDef } from "@tanstack/react-table"
import { Policy } from "@/types/policy"
import { DataTableColumnHeader } from "@/components/ui/data-table-column-header"
import { Badge } from "@/components/ui/badge"
import { Button } from "@/components/ui/button"
import { CheckCircle2, Clock, XCircle, AlertCircle, MoreHorizontal, FileText } from "lucide-react"
import { format } from "date-fns"
import { useRouter } from 'next/navigation'

import {
    DropdownMenu,
    DropdownMenuContent,
    DropdownMenuItem,
    DropdownMenuLabel,
    DropdownMenuSeparator,
    DropdownMenuTrigger,
} from "@/components/ui/dropdown-menu"

// Props for actions to handle navigation and state updates
interface PolicyActionsProps {
    row: Policy
    onView: (id: string) => void
    onEdit: (policy: Policy) => void
    onDelete: (id: string) => void
    t: (key: string) => string
}

const PolicyActions = ({ row, onView, onEdit, onDelete, t }: PolicyActionsProps) => {
    return (
        <DropdownMenu>
            <DropdownMenuTrigger asChild>
                <Button variant="ghost" className="h-8 w-8 p-0">
                    <span className="sr-only">{t('table.open_menu', 'Open menu')}</span>
                    <MoreHorizontal className="h-4 w-4" />
                </Button>
            </DropdownMenuTrigger>
            <DropdownMenuContent align="end">
                <DropdownMenuLabel>{t('table.actions', 'Actions')}</DropdownMenuLabel>
                <DropdownMenuItem onClick={() => setTimeout(() => onView(row.id), 0)}>
                    <FileText className="mr-2 h-4 w-4" />
                    {t('table.view_details', 'View Details')}
                </DropdownMenuItem>
                <DropdownMenuItem onClick={() => navigator.clipboard.writeText(row.policy_number)}>
                    {t('table.copy_number', 'Copy number')}
                </DropdownMenuItem>
                <DropdownMenuSeparator />
                <DropdownMenuItem onClick={() => setTimeout(() => onEdit(row), 0)}>
                    {t('btn.edit', 'Edit')}
                </DropdownMenuItem>
                <DropdownMenuItem
                    className="text-red-600 focus:text-red-600"
                    onClick={() => setTimeout(() => onDelete(row.id), 0)}
                >
                    {t('btn.delete', 'Delete')}
                </DropdownMenuItem>
            </DropdownMenuContent>
        </DropdownMenu>
    )
}

const getStatusBadge = (status: string, t: (key: string, fallback: string) => string) => {
    switch (status) {
        case 'active':
            return <Badge className="bg-green-500 hover:bg-green-600"><CheckCircle2 className="w-3 h-3 mr-1" /> {t('status.active', 'Active')}</Badge>;
        case 'expired':
            return <Badge variant="secondary"><Clock className="w-3 h-3 mr-1" /> {t('status.expired', 'Expired')}</Badge>;
        case 'canceled':
            return <Badge variant="destructive"><XCircle className="w-3 h-3 mr-1" /> {t('status.cancelled', 'Cancelled')}</Badge>;
        case 'lapsed':
            return <Badge variant="destructive" className="bg-orange-500"><AlertCircle className="w-3 h-3 mr-1" /> {t('status.lapsed', 'Lapsed')}</Badge>;
        default:
            return <Badge variant="outline">{status}</Badge>;
    }
};



export const columns = (
    onView: (id: string) => void,
    onEdit: (policy: Policy) => void,
    onDelete: (id: string) => void,
    t: (key: string) => string,
    formatPrice: (amount: number) => string
): ColumnDef<Policy>[] => [
        {
            accessorKey: "policy_number",
            header: ({ column }) => (
                <DataTableColumnHeader column={column} title={t('Policy Number')} />
            ),
            cell: ({ row }) => <div className="font-medium">{row.getValue("policy_number")}</div>,
        },
        {
            accessorKey: "client_name",
            header: ({ column }) => (
                <DataTableColumnHeader column={column} title={t('Client Name')} />
            ),
            cell: ({ row }) => row.getValue("client_name") || "Unknown",
        },
        {
            accessorKey: "start_date",
            header: ({ column }) => (
                <DataTableColumnHeader column={column} title={t('Start Date')} />
            ),
            cell: ({ row }) => format(new Date(row.getValue("start_date")), 'dd/MM/yyyy'),
        },
        {
            accessorKey: "end_date",
            header: ({ column }) => (
                <DataTableColumnHeader column={column} title={t('End Date')} />
            ),
            cell: ({ row }) => format(new Date(row.getValue("end_date")), 'dd/MM/yyyy'),
        },
        {
            accessorKey: "premium_amount",
            header: ({ column }) => (
                <DataTableColumnHeader column={column} title={t('Premium')} />
            ),
            cell: ({ row }) => formatPrice(row.getValue("premium_amount")),
        },
        {
            accessorKey: "premium_frequency",
            header: ({ column }) => (
                <DataTableColumnHeader column={column} title={t('Frequency')} />
            ),
            cell: ({ row }) => <div className="capitalize">{row.getValue("premium_frequency")}</div>,
        },
        {
            accessorKey: "status",
            header: ({ column }) => (
                <DataTableColumnHeader column={column} title={t('Status')} />
            ),
            cell: ({ row }) => getStatusBadge(row.getValue("status"), t),
        },
        {
            id: "actions",
            cell: ({ row }) => (
                <PolicyActions
                    row={row.original}
                    onView={onView}
                    onEdit={onEdit}
                    onDelete={onDelete}
                    t={t}
                />
            ),
        },
    ]
