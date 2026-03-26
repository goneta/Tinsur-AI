"use client"

import { ColumnDef } from "@tanstack/react-table"
import { Badge } from "@/components/ui/badge"
import { Button } from "@/components/ui/button"
import { MoreHorizontal, Eye, Edit, Trash, Copy } from "lucide-react"
import {
    DropdownMenu,
    DropdownMenuContent,
    DropdownMenuItem,
    DropdownMenuLabel,
    DropdownMenuSeparator,
    DropdownMenuTrigger,
} from "@/components/ui/dropdown-menu"
import { PolicyTemplate } from "@/types/policy-template"
import { format } from "date-fns"

export const columns = (
    onView: (id: string) => void,
    onEdit: (template: PolicyTemplate) => void,
    onDelete: (id: string) => void,
    onDuplicate: (id: string) => void
): ColumnDef<PolicyTemplate>[] => [
        {
            accessorKey: "name",
            header: "Name",
            cell: ({ row }) => {
                const template = row.original
                return (
                    <div className="flex flex-col">
                        <span className="font-medium text-foreground">{template.name}</span>
                        <span className="text-xs text-muted-foreground font-mono">{template.code}</span>
                    </div>
                )
            },
        },
        {
            accessorKey: "version",
            header: "Version",
            cell: ({ row }) => {
                return <Badge variant="outline">v{row.getValue("version")}</Badge>
            },
        },
        {
            accessorKey: "is_active",
            header: "Status",
            cell: ({ row }) => {
                const isActive = row.getValue("is_active") as boolean
                return (
                    <Badge variant={isActive ? "default" : "secondary"}>
                        {isActive ? "Active" : "Inactive"}
                    </Badge>
                )
            },
        },
        {
            accessorKey: "language",
            header: "Language",
            cell: ({ row }) => {
                return <span className="uppercase text-xs font-semibold">{row.getValue("language")}</span>
            },
        },
        {
            accessorKey: "updated_at",
            header: "Last Updated",
            cell: ({ row }) => {
                return <span>{format(new Date(row.getValue("updated_at")), "MMM dd, yyyy")}</span>
            },
        },
        {
            id: "actions",
            cell: ({ row }) => {
                const template = row.original

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
                            <DropdownMenuItem onClick={() => onView(template.id)}>
                                <Eye className="mr-2 h-4 w-4" /> View Details
                            </DropdownMenuItem>
                            <DropdownMenuItem onClick={() => onEdit(template)}>
                                <Edit className="mr-2 h-4 w-4" /> Edit Template
                            </DropdownMenuItem>
                            <DropdownMenuItem onClick={() => onDuplicate(template.id)}>
                                <Copy className="mr-2 h-4 w-4" /> Duplicate
                            </DropdownMenuItem>
                            <DropdownMenuSeparator />
                            <DropdownMenuItem
                                onClick={() => onDelete(template.id)}
                                className="text-destructive focus:text-destructive"
                            >
                                <Trash className="mr-2 h-4 w-4" /> Delete
                            </DropdownMenuItem>
                        </DropdownMenuContent>
                    </DropdownMenu>
                )
            },
        },
    ]
