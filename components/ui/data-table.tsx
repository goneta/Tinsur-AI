"use client"

import * as React from "react"
import {
    ColumnDef,
    ColumnFiltersState,
    SortingState,
    VisibilityState,
    flexRender,
    getCoreRowModel,
    getFilteredRowModel,
    getPaginationRowModel,
    getSortedRowModel,
    useReactTable,
} from "@tanstack/react-table"

import {
    Table,
    TableBody,
    TableCell,
    TableHead,
    TableHeader,
    TableRow,
} from "@/components/ui/table"
import { Button } from "@/components/ui/button"
import { Input } from "@/components/ui/input"
import {
    DropdownMenu,
    DropdownMenuCheckboxItem,
    DropdownMenuContent,
    DropdownMenuTrigger,
} from "@/components/ui/dropdown-menu"
import { Settings2 } from "lucide-react"

import {
    Select,
    SelectContent,
    SelectItem,
    SelectTrigger,
    SelectValue,
} from "@/components/ui/select"
import { useLanguage } from '@/contexts/language-context';

interface DataTableProps<TData, TValue> {
    columns: ColumnDef<TData, TValue>[]
    data: TData[]
}

export function DataTable<TData, TValue>({
    columns,
    data,
}: DataTableProps<TData, TValue>) {
    const { t } = useLanguage();
    const [sorting, setSorting] = React.useState<SortingState>([])
    const [columnFilters, setColumnFilters] = React.useState<ColumnFiltersState>([])
    const [columnVisibility, setColumnVisibility] = React.useState<VisibilityState>({})
    const [globalFilter, setGlobalFilter] = React.useState("")
    const [searchKey, setSearchKey] = React.useState<string>("all")
    const [mounted, setMounted] = React.useState(false)

    React.useEffect(() => {
        setMounted(true)
    }, [])

    // Custom filter function that handles date formatting implementation details
    // e.g. "19/07" search against "2023-07-19" data
    const aggressiveFilter = (row: any, columnId: string, filterValue: string) => {
        const itemValue = row.getValue(columnId)
        if (itemValue == null) return false

        const filterStr = String(filterValue).toLowerCase()
        const itemStr = String(itemValue).toLowerCase()

        // 1. Standard Exact/Substring match
        if (itemStr.includes(filterStr)) return true

        // 2. Aggressive match: Remove separators to handle date format diffs
        // e.g. User types "19/07", data is "2023-07-19"
        // "1907" is in "20230719" -> Match
        const cleanFilter = filterStr.replace(/[^a-z0-9]/g, "")
        const cleanItem = itemStr.replace(/[^a-z0-9]/g, "")

        if (cleanFilter.length > 0 && cleanItem.includes(cleanFilter)) return true

        return false
    }

    const table = useReactTable({
        data,
        columns,
        getCoreRowModel: getCoreRowModel(),
        getPaginationRowModel: getPaginationRowModel(),
        onSortingChange: setSorting,
        getSortedRowModel: getSortedRowModel(),
        onColumnFiltersChange: setColumnFilters,
        getFilteredRowModel: getFilteredRowModel(),
        onColumnVisibilityChange: setColumnVisibility,
        onGlobalFilterChange: setGlobalFilter,
        globalFilterFn: aggressiveFilter,
        state: {
            sorting,
            columnFilters,
            columnVisibility,
            globalFilter,
        },
        enableGlobalFilter: true,
        defaultColumn: {
            filterFn: aggressiveFilter
        }
    })

    return (
        <div className="space-y-4">
            <div className="flex items-center justify-between">
                {mounted ? (
                    <div className="flex items-center py-4 w-full max-w-sm gap-2">
                        <div className="relative w-full flex items-center gap-2">
                            <Select
                                value={searchKey}
                                onValueChange={(value) => {
                                    // If "all", reset to global filter
                                    if (value === "all") {
                                        setSearchKey("all")
                                        table.resetColumnFilters()
                                        if (globalFilter) table.setGlobalFilter(globalFilter)
                                    } else {
                                        // If specific column, clear global filter and set column filter
                                        setSearchKey(value)
                                        table.setGlobalFilter("") // Clear global
                                        if (globalFilter) table.getColumn(value)?.setFilterValue(globalFilter)
                                    }
                                }}
                            >
                                <SelectTrigger className="w-[130px]">
                                    <SelectValue placeholder={t('common.columns', 'Columns')} />
                                </SelectTrigger>
                                <SelectContent>
                                    <SelectItem value="all">{t('common.all_columns', 'All Columns')}</SelectItem>
                                    {table.getAllColumns()
                                        .filter((column) => column.getCanFilter())
                                        .map((column) => (
                                            <SelectItem key={column.id} value={column.id} className="capitalize">
                                                {t(`common.column.${column.id}`, column.id.replace(/_/g, " "))}
                                            </SelectItem>
                                        ))}
                                </SelectContent>
                            </Select>
                            <Input
                                placeholder={searchKey !== "all"
                                    ? `${t('common.search', 'Search')} ${t(`common.column.${searchKey}`, searchKey.replace(/_/g, " "))}...`
                                    : `${t('common.search', 'Search')} ${t('common.all_columns', 'All Columns').toLowerCase()}...`}
                                value={(searchKey !== "all" ? (table.getColumn(searchKey)?.getFilterValue() as string) : globalFilter) ?? ""}
                                onChange={(event) => {
                                    const value = event.target.value
                                    if (searchKey !== "all") {
                                        table.getColumn(searchKey)?.setFilterValue(value)
                                    } else {
                                        setGlobalFilter(value)
                                    }
                                }}
                                className="max-w-sm"
                            />
                        </div>
                    </div>
                ) : (
                    <div className="flex items-center py-4 w-full max-w-sm gap-2 opacity-0">
                        {/* Skeleton/Placeholder to maintain layout height during hydration */}
                        <div className="h-9 w-[130px] rounded-md bg-muted animate-pulse" />
                        <div className="h-9 w-full rounded-md bg-muted animate-pulse" />
                    </div>
                )}

                {/* View Options (Column Toggle) */}
                <DropdownMenu>
                    <DropdownMenuTrigger asChild>
                        <Button variant="outline" className="ml-auto hidden h-8 lg:flex">
                            <Settings2 className="mr-2 h-4 w-4" />
                            {t('common.view', 'View')}
                        </Button>
                    </DropdownMenuTrigger>
                    <DropdownMenuContent align="end" className="w-[150px]">
                        {table
                            .getAllColumns()
                            .filter(
                                (column) =>
                                    typeof column.accessorFn !== "undefined" && column.getCanHide()
                            )
                            .map((column) => {
                                return (
                                    <DropdownMenuCheckboxItem
                                        key={column.id}
                                        className="capitalize"
                                        checked={column.getIsVisible()}
                                        onCheckedChange={(value) => column.toggleVisibility(!!value)}
                                    >
                                        {t(`common.column.${column.id}`, column.id.replace(/_/g, " "))}
                                    </DropdownMenuCheckboxItem>
                                )
                            })}
                    </DropdownMenuContent>
                </DropdownMenu>
            </div>

            <div className="rounded-md border">
                <Table>
                    <TableHeader>
                        {table.getHeaderGroups().map((headerGroup) => (
                            <TableRow key={headerGroup.id}>
                                {headerGroup.headers.map((header) => {
                                    return (
                                        <TableHead key={header.id}>
                                            {header.isPlaceholder
                                                ? null
                                                : flexRender(
                                                    header.column.columnDef.header,
                                                    header.getContext()
                                                )}
                                        </TableHead>
                                    )
                                })}
                            </TableRow>
                        ))}
                    </TableHeader>
                    <TableBody>
                        {table.getRowModel().rows?.length ? (
                            table.getRowModel().rows.map((row) => (
                                <TableRow
                                    key={row.id}
                                    data-state={row.getIsSelected() && "selected"}
                                >
                                    {row.getVisibleCells().map((cell) => (
                                        <TableCell key={cell.id}>
                                            {flexRender(cell.column.columnDef.cell, cell.getContext())}
                                        </TableCell>
                                    ))}
                                </TableRow>
                            ))
                        ) : (
                            <TableRow>
                                <TableCell
                                    colSpan={columns.length}
                                    className="h-24 text-center"
                                >
                                    {t('common.no_results', 'No results.')}
                                </TableCell>
                            </TableRow>
                        )}
                    </TableBody>
                </Table>
            </div>

            {/* Pagination Controls */}
            <div className="flex items-center justify-end space-x-2 py-4">
                <Button
                    variant="outline"
                    size="sm"
                    onClick={() => table.previousPage()}
                    disabled={!table.getCanPreviousPage()}
                >
                    {t('common.previous', 'Previous')}
                </Button>
                <Button
                    variant="outline"
                    size="sm"
                    onClick={() => table.nextPage()}
                    disabled={!table.getCanNextPage()}
                >
                    {t('common.next', 'Next')}
                </Button>
            </div>
        </div>
    )
}
