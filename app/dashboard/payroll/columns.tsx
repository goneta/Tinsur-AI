"use client"

import { ColumnDef } from "@tanstack/react-table"
import { Badge } from "@/components/ui/badge"
import { Button } from "@/components/ui/button"
import { CircleDollarSign } from "lucide-react"
import { DataTableColumnHeader } from "@/components/ui/data-table-column-header"
import { Avatar, AvatarFallback, AvatarImage } from "@/components/ui/avatar"
import { getProfileImageUrl } from "@/lib/api"

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
}

export const columns = (
    onPay: (employee: Employee) => void,
    onViewProfile: (employee: Employee) => void
): ColumnDef<Employee>[] => [
        {
            accessorKey: "profile_picture",
            header: "",
            cell: ({ row }) => {
                const employee = row.original;
                return (
                    <div
                        className="cursor-pointer transition-transform hover:scale-105 active:scale-95"
                        onClick={() => onViewProfile(employee)}
                        title="View Profile"
                    >
                        <Avatar className="h-10 w-10 border shadow-sm">
                            <AvatarImage
                                src={getProfileImageUrl(employee.profile_picture)}
                                className="object-cover"
                            />
                            <AvatarFallback className="bg-gray-100 text-gray-400">
                                {employee.first_name?.[0]}{employee.last_name?.[0]}
                            </AvatarFallback>
                        </Avatar>
                    </div>
                );
            },
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
                return <div className="font-medium text-primary hover:underline cursor-pointer" onClick={() => onViewProfile(row.original)}>{firstName} {lastName}</div>
            },
        },
        {
            accessorKey: "last_paid_month",
            id: "month",
            header: ({ column }) => (
                <DataTableColumnHeader column={column} title="Month" />
            ),
            cell: ({ row }) => {
                const month = row.original.last_paid_month;
                return <Badge variant="secondary">{month || "Not paid yet"}</Badge>
            },
        },
        {
            accessorKey: "role",
            header: ({ column }) => (
                <DataTableColumnHeader column={column} title="Role" />
            ),
            cell: ({ row }) => <Badge variant="outline" className="capitalize">{row.getValue("role")}</Badge>,
        },
        {
            accessorKey: "employee_profile.base_salary",
            id: "salary",
            header: ({ column }) => (
                <DataTableColumnHeader column={column} title="Salary" />
            ),
            cell: ({ row }) => {
                const salary = row.original.employee_profile?.base_salary;
                const currency = row.original.employee_profile?.currency || "XOF";
                if (!salary) return "Not set";
                return new Intl.NumberFormat('fr-FR', { style: 'currency', currency }).format(salary);
            },
        },
        {
            accessorKey: "employee_profile.payment_method",
            id: "method",
            header: ({ column }) => (
                <DataTableColumnHeader column={column} title="Method" />
            ),
            cell: ({ row }) => {
                const method = row.original.employee_profile?.payment_method;
                return <span className="capitalize">{method?.replace('_', ' ') || "Not set"}</span>;
            },
        },
        {
            id: "actions",
            cell: ({ row }) => (
                <Button size="sm" variant="ghost" onClick={() => onPay(row.original)}>
                    <CircleDollarSign className="h-4 w-4 mr-2" />
                    Pay
                </Button>
            ),
        },
    ]
