"use client"

import { ColumnDef } from "@tanstack/react-table"
import { Badge } from "@/components/ui/badge"
import { Button } from "@/components/ui/button"
import { MoreHorizontal, Pencil, Trash2, Eye, SquarePen } from "lucide-react"
import {
    DropdownMenu,
    DropdownMenuContent,
    DropdownMenuItem,
    DropdownMenuLabel,
    DropdownMenuTrigger,
} from "@/components/ui/dropdown-menu"
import { DataTableColumnHeader } from "@/components/ui/data-table-column-header"
import { Avatar, AvatarFallback, AvatarImage } from "@/components/ui/avatar"
import { Camera, Loader2 } from "lucide-react"
import { getProfileImageUrl } from "@/lib/api"
import { useState } from "react"
import { EmployeeTableActions } from "./components/employee-table-actions"
import { ProfileUploader } from "@/components/shared/profile-uploader"

export interface Employee {
    id: string;
    first_name: string;
    last_name: string;
    email: string;
    phone?: string;
    role: string;
    profile_picture?: string;
    last_paid_month?: string;
    employee_profile?: {
        job_title?: string;
        department?: string;
        base_salary?: number;
        currency?: string;
        payment_method?: string;
    };
    pos_location?: {
        id: string;
        name: string;
        city: string;
    };
}


export const columns = (
    onEdit: (employee: Employee) => void,
    onRefresh: () => void
): ColumnDef<Employee>[] => [
        {
            accessorKey: "profile_picture",
            header: "",
            cell: ({ row }) => (
                <ProfileUploader
                    entityId={row.original.id}
                    entityType="user"
                    currentImageUrl={row.original.profile_picture}
                    name={`${row.original.first_name} ${row.original.last_name}`}
                    size="sm"
                    onUploadSuccess={onRefresh}
                />
            ),
        },
        {
            accessorKey: "first_name",
            id: "name",
            header: ({ column }) => (
                <DataTableColumnHeader column={column} title="Name" />
            ),
            cell: ({ row }) => {
                const firstName = row.original.first_name;
                const lastName = row.original.last_name;
                return <div className="font-medium">{firstName} {lastName}</div>
            },
        },
        {
            accessorKey: "email",
            header: ({ column }) => (
                <DataTableColumnHeader column={column} title="Email" />
            ),
        },
        {
            accessorKey: "employee_profile.department",
            id: "department",
            header: ({ column }) => (
                <DataTableColumnHeader column={column} title="Department" />
            ),
            cell: ({ row }) => row.original.employee_profile?.department || "-",
        },
        {
            accessorKey: "phone",
            header: ({ column }) => (
                <DataTableColumnHeader column={column} title="Phone" />
            ),
            cell: ({ row }) => row.original.phone || "-",
        },
        {
            accessorKey: "pos_location.city",
            id: "pos_city",
            header: ({ column }) => (
                <DataTableColumnHeader column={column} title="POS City" />
            ),
            cell: ({ row }) => row.original.pos_location?.city || "-",
        },
        {
            accessorKey: "role",
            header: ({ column }) => (
                <DataTableColumnHeader column={column} title="Role" />
            ),
            cell: ({ row }) => <Badge variant="outline" className="capitalize">{row.getValue("role")}</Badge>,
        },
        {
            id: "actions",
            cell: ({ row }) => <EmployeeTableActions row={row.original} onEdit={onEdit} />,
        },
    ]
