"use client"

import { ColumnDef } from "@tanstack/react-table"
import { Client } from "@/types/client"
import { DataTableColumnHeader } from "@/components/ui/data-table-column-header"
import { Badge } from "@/components/ui/badge"
import { Button } from "@/components/ui/button"
import { MoreHorizontal, SquarePen, Trash2 } from "lucide-react"

import {
    DropdownMenu,
    DropdownMenuContent,
    DropdownMenuItem,
    DropdownMenuLabel,
    DropdownMenuTrigger,
} from "@/components/ui/dropdown-menu"
import { ProfileUploader } from "@/components/shared/profile-uploader"
import { ClientTableActions } from "./components/client-table-actions"

// Removed ProfilePictureCell as we're using ClientProfilePicture component

export const columns = (
    onEdit: (client: Client) => void,
    onDelete: (client: Client) => void,
    onRefresh: () => void,
    t: (key: string, defaultVal?: string) => string
): ColumnDef<Client>[] => [
        {
            accessorKey: "profile_picture",
            header: "",
            cell: ({ row }) => (
                <ProfileUploader
                    entityId={row.original.id}
                    entityType="client"
                    currentImageUrl={row.original.profile_picture}
                    name={row.original.client_type === 'individual' ? `${row.original.first_name} ${row.original.last_name}` : row.original.business_name || ''}
                    size="sm"
                    onUploadSuccess={onRefresh}
                />
            ),
        },
        {
            accessorKey: "first_name", // We will use a custom accessor for sorting by full name or business name
            id: "name",
            header: ({ column }) => (
                <DataTableColumnHeader column={column} title={t('clients.col_name', 'Name')} />
            ),
            cell: ({ row }) => {
                const client = row.original
                const name = client.client_type === 'individual'
                    ? `${client.first_name} ${client.last_name}`
                    : client.business_name
                return <div className="font-medium">{name}</div>
            },
            accessorFn: (row) => {
                return row.client_type === 'individual'
                    ? `${row.first_name} ${row.last_name}`
                    : row.business_name
            },
        },
        {
            accessorKey: "client_type",
            header: ({ column }) => (
                <DataTableColumnHeader column={column} title={t('clients.col_type', 'Type')} />
            ),
            cell: ({ row }) => (
                <div className="capitalize">{row.getValue("client_type")}</div>
            ),
        },
        {
            accessorKey: "email",
            header: ({ column }) => (
                <DataTableColumnHeader column={column} title={t('clients.col_email', 'Email')} />
            ),
        },
        {
            accessorKey: "phone_number",
            header: ({ column }) => (
                <DataTableColumnHeader column={column} title={t('clients.col_phone', 'Phone')} />
            ),
        },
        {
            accessorKey: "city",
            header: ({ column }) => (
                <DataTableColumnHeader column={column} title={t('clients.col_city', 'City')} />
            ),
            cell: ({ row }) => row.getValue("city") || "-",
        },
        {
            accessorKey: "risk_profile",
            header: ({ column }) => (
                <DataTableColumnHeader column={column} title={t('clients.col_risk', 'Risk')} />
            ),
            cell: ({ row }) => {
                const risk = row.getValue("risk_profile") as string
                const colors: Record<string, string> = {
                    low: 'bg-green-100 text-green-800',
                    medium: 'bg-yellow-100 text-yellow-800',
                    high: 'bg-red-100 text-red-800',
                };
                return (
                    <span className={`inline-flex items-center rounded-full px-2.5 py-0.5 text-xs font-medium ${colors[risk] || ''}`}>
                        {risk}
                    </span>
                )
            },
        },
        {
            accessorKey: "kyc_status",
            header: ({ column }) => (
                <DataTableColumnHeader column={column} title={t('clients.col_kyc', 'KYC')} />
            ),
            cell: ({ row }) => {
                const status = row.getValue("kyc_status") as string
                const colors: Record<string, string> = {
                    verified: 'bg-green-100 text-green-800',
                    pending: 'bg-yellow-100 text-yellow-800',
                    rejected: 'bg-red-100 text-red-800',
                };
                return (
                    <span className={`inline-flex items-center rounded-full px-2.5 py-0.5 text-xs font-medium ${colors[status] || ''}`}>
                        {status || 'pending'}
                    </span>
                )
            },
        },
        {
            accessorKey: "status",
            header: ({ column }) => (
                <DataTableColumnHeader column={column} title={t('clients.col_status', 'Status')} />
            ),
            cell: ({ row }) => {
                const status = row.getValue("status") as string
                const variants: Record<string, 'default' | 'secondary' | 'destructive'> = {
                    active: 'default',
                    inactive: 'secondary',
                    suspended: 'destructive',
                };
                return <Badge variant={variants[status] || 'default'}>{status}</Badge>;
            },
        },
        {
            id: "actions",
            cell: ({ row }) => (
                <ClientTableActions
                    row={row.original}
                    onEdit={onEdit}
                    onDelete={onDelete}
                />
            ),
        },
    ]
