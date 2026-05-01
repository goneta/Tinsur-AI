"use client"

import { ColumnDef } from "@tanstack/react-table"
import { Quote } from "@/types/quote"
import { Button } from "@/components/ui/button"
import { MoreHorizontal, FileText, Trash, Send, CheckCircle, XCircle, Archive } from "lucide-react"
import {
    DropdownMenu,
    DropdownMenuContent,
    DropdownMenuItem,
    DropdownMenuLabel,
    DropdownMenuTrigger,
} from "@/components/ui/dropdown-menu"
import { Badge } from "@/components/ui/badge"
import { DataTableColumnHeader } from "@/components/ui/data-table-column-header"
import { format } from "date-fns"
import { useLanguage } from "@/contexts/language-context"

const statusColor = (status: string) => {
    switch (status?.toLowerCase()) {
        case 'draft': return 'secondary';
        case 'draft_from_client': return 'secondary';
        case 'sent': return 'default';
        case 'submitted': return 'default';
        case 'under_review': return 'default';
        case 'accepted': return 'default';
        case 'policy_created': return 'default';
        case 'approved': return 'default';
        case 'archived': return 'outline';
        case 'rejected': return 'destructive';
        case 'expired': return 'destructive';
        default: return 'outline';
    }
};

export const columns = (
    onView: (id: string) => void,
    onDelete: (id: string) => void,
    onSend: (quote: Quote) => void,
    onApprove: (quote: Quote) => void,
    onReject: (quote: Quote) => void,
    onArchive: (quote: Quote) => void,
    policyTypes: Record<string, string>,
    t?: (key: string, fallback: string) => string
): ColumnDef<Quote>[] => {
    const translate = t || ((key: string, fallback: string) => fallback);

    return [
        {
            accessorKey: "quote_number",
            header: ({ column }) => (
                <DataTableColumnHeader column={column} title={translate("col.quote_number", "Quote #")} />
            ),
            cell: ({ row }) => <div className="font-medium">{row.getValue("quote_number") || ""}</div>,
        },
        {
            accessorKey: "client_name",
            header: ({ column }) => (
                <DataTableColumnHeader column={column} title={translate("col.client", "Client")} />
            ),
            cell: ({ row }) => <div>{row.getValue("client_name") || translate("Unknown", "Unknown")}</div>,
        },
        {
            accessorKey: "policy_type_id",
            header: ({ column }) => (
                <DataTableColumnHeader column={column} title={translate("col.type", "Type")} />
            ),
            cell: ({ row }) => {
                const typeId = row.getValue("policy_type_id") as string;
                return <div>{policyTypes[typeId] || translate("Unknown", "Unknown")}</div>
            },
        },
        {
            accessorKey: "premium_amount",
            header: ({ column }) => (
                <DataTableColumnHeader column={column} title={translate("col.premium", "Premium")} />
            ),
            cell: ({ row }) => {
                const amount = parseFloat(row.getValue("premium_amount"));
                const formatted = new Intl.NumberFormat("en-US", {
                    style: "currency",
                    currency: "USD",
                }).format(amount);
                return <div>{formatted}</div>;
            },
        },
        {
            accessorKey: "status",
            header: ({ column }) => (
                <DataTableColumnHeader column={column} title={translate("col.status", "Status")} />
            ),
            cell: ({ row }) => {
                const status = (row.getValue("status") as string) || "";
                return (
                    <div className="flex">
                        <Badge variant={statusColor(status) as any}>
                            {status.toUpperCase()}
                        </Badge>
                    </div>
                )
            },
        },
        {
            accessorKey: "created_at",
            header: ({ column }) => (
                <DataTableColumnHeader column={column} title={translate("col.created", "Created")} />
            ),
            cell: ({ row }) => {
                const date = row.getValue("created_at") as string;
                return <div>{date ? format(new Date(date), "MMM d, yyyy") : ""}</div>
            },
        },
        {
            id: "actions",
            cell: ({ row }) => {
                const quote = row.original;

                return (
                    <DropdownMenu>
                        <DropdownMenuTrigger asChild>
                            <Button variant="ghost" className="h-8 w-8 p-0">
                                <span className="sr-only">{translate("Open menu", "Open menu")}</span>
                                <MoreHorizontal className="h-4 w-4" />
                            </Button>
                        </DropdownMenuTrigger>
                        <DropdownMenuContent align="end">
                            <DropdownMenuLabel>{translate("Actions", "Actions")}</DropdownMenuLabel>
                            <DropdownMenuItem onClick={() => setTimeout(() => onView(quote.id), 0)}>
                                <FileText className="mr-2 h-4 w-4" /> {translate("View Details", "View Details")}
                            </DropdownMenuItem>
                            {['draft', 'draft_from_client'].includes(quote.status) && (
                                <DropdownMenuItem onClick={() => setTimeout(() => onSend(quote), 0)}>
                                    <Send className="mr-2 h-4 w-4" /> {translate("Send to Client", "Send to Client")}
                                </DropdownMenuItem>
                            )}
                            {['sent', 'draft_from_client', 'submitted', 'under_review'].includes(quote.status) && (
                                <>
                                    <DropdownMenuItem className="text-green-600" onClick={() => setTimeout(() => onApprove(quote), 0)}>
                                        <CheckCircle className="mr-2 h-4 w-4" /> {translate("btn.approve", "Approve")}
                                    </DropdownMenuItem>
                                    <DropdownMenuItem className="text-red-600" onClick={() => setTimeout(() => onReject(quote), 0)}>
                                        <XCircle className="mr-2 h-4 w-4" /> {translate("btn.reject", "Reject")}
                                    </DropdownMenuItem>
                                </>
                            )}
                            {['accepted', 'policy_created', 'approved'].includes(quote.status) && (
                                <DropdownMenuItem className="text-gray-600" onClick={() => setTimeout(() => onArchive(quote), 0)}>
                                    <Archive className="mr-2 h-4 w-4" /> {translate("Archive", "Archive")}
                                </DropdownMenuItem>
                            )}
                            {['draft', 'draft_from_client'].includes(quote.status) && (
                                <DropdownMenuItem className="text-red-600" onClick={() => setTimeout(() => onDelete(quote.id), 0)}>
                                    <Trash className="mr-2 h-4 w-4" /> {translate("btn.delete", "Delete")}
                                </DropdownMenuItem>
                            )}
                        </DropdownMenuContent>
                    </DropdownMenu>
                )
            },
        },
    ]
}
