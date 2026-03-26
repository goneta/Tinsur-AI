"use client"

import { MoreHorizontal, Eye, SquarePen, Trash2 } from "lucide-react"
import { Button } from "@/components/ui/button"
import {
    DropdownMenu,
    DropdownMenuContent,
    DropdownMenuItem,
    DropdownMenuLabel,
    DropdownMenuTrigger,
} from "@/components/ui/dropdown-menu"
import { Employee } from "../columns"

interface EmployeeTableActionsProps {
    row: Employee
    onEdit: (employee: Employee) => void
}

export function EmployeeTableActions({ row, onEdit }: EmployeeTableActionsProps) {
    return (
        <DropdownMenu>
            <DropdownMenuTrigger asChild>
                <Button variant="ghost" className="h-8 w-8 p-0">
                    <span className="sr-only">Open menu</span>
                    <MoreHorizontal className="h-4 w-4" />
                </Button>
            </DropdownMenuTrigger>
            <DropdownMenuContent align="end">
                <DropdownMenuLabel>Actions</DropdownMenuLabel>
                <DropdownMenuItem onClick={() => window.location.href = `/dashboard/employees/${row.id}`}>
                    <Eye className="mr-2 h-4 w-4" />
                    View Profile
                </DropdownMenuItem>
                <DropdownMenuItem onClick={() => onEdit(row)}>
                    <SquarePen className="mr-2 h-4 w-4" />
                    Edit
                </DropdownMenuItem>
                <DropdownMenuItem className="text-red-600 focus:text-red-600">
                    <Trash2 className="mr-2 h-4 w-4" />
                    Delete
                </DropdownMenuItem>
            </DropdownMenuContent>
        </DropdownMenu>
    )
}
