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
import { Settings2, LayoutGrid, List } from "lucide-react"

import {
    Select,
    SelectContent,
    SelectItem,
    SelectTrigger,
    SelectValue,
} from "@/components/ui/select"
import { useLanguage } from '@/contexts/language-context';

interface DataViewProps<TData, TValue> {
    columns: ColumnDef<TData, TValue>[]
    data: TData[]
    renderCard: (item: TData) => React.ReactNode
    defaultView?: 'list' | 'card'
    activeFilters?: {
        key: string
        value: string
    }[]
    getRowId?: (originalRow: TData, index: number, parent?: any) => string
}

export function DataView<TData, TValue>({
    columns,
    data,
    renderCard,
    defaultView = 'list',
    activeFilters,
    getRowId,
}: DataViewProps<TData, TValue>) {
    const { t } = useLanguage();
    const [sorting, setSorting] = React.useState<SortingState>([])
    const [columnFilters, setColumnFilters] = React.useState<ColumnFiltersState>([])
    const [columnVisibility, setColumnVisibility] = React.useState<VisibilityState>({})
    const [globalFilter, setGlobalFilter] = React.useState("")
    const [searchKey, setSearchKey] = React.useState<string>("all")
    const [viewMode, setViewMode] = React.useState<'list' | 'card'>(defaultView)
    const [mounted, setMounted] = React.useState(false)

    React.useEffect(() => {
        setMounted(true)
    }, [])

    const aggressiveFilter = (row: any, columnId: string, filterValue: string) => {
        const itemValue = row.getValue(columnId)
        if (itemValue == null) return false

        const filterStr = String(filterValue).toLowerCase()
        const itemStr = String(itemValue).toLowerCase()

        if (itemStr.includes(filterStr)) return true

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
        },
        getRowId,
    })

    if (!mounted) return null

    return (
        <div className="space-y-4">
            <div className="flex items-center justify-between">
                <div className="flex items-center gap-2 flex-1">
                    {/* Search & Filter Controls */}
                    <div className="flex items-center w-full max-w-sm gap-2">
                        <Select
                            value={searchKey}
                            onValueChange={(value) => {
                                if (value === "all") {
                                    setSearchKey("all")
                                    table.resetColumnFilters()
                                    if (globalFilter) table.setGlobalFilter(globalFilter)
                                } else {
                                    setSearchKey(value)
                                    table.setGlobalFilter("")
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
                                : t('common.search', 'Search...')}
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

                {/* View Switcher & Column Toggle */}
                <div className="flex items-center gap-2">
                    <div className="flex bg-muted p-1 rounded-lg">
                        <Button
                            variant={viewMode === 'card' ? 'secondary' : 'ghost'}
                            size="sm"
                            className="px-3 h-8"
                            onClick={() => setViewMode('card')}
                        >
                            <LayoutGrid className="h-4 w-4 mr-2" />
                            {t('common.view_card', 'Card')}
                        </Button>
                        <Button
                            variant={viewMode === 'list' ? 'secondary' : 'ghost'}
                            size="sm"
                            className="px-3 h-8"
                            onClick={() => setViewMode('list')}
                        >
                            <List className="h-4 w-4 mr-2" />
                            {t('common.view_list', 'List')}
                        </Button>
                    </div>

                    <DropdownMenu>
                        <DropdownMenuTrigger asChild>
                            <Button variant="outline" className="hidden h-8 lg:flex">
                                <Settings2 className="mr-2 h-4 w-4" />
                                {t('common.view', 'View')}
                            </Button>
                        </DropdownMenuTrigger>
                        <DropdownMenuContent align="end" className="w-[150px]">
                            {table
                                .getAllColumns()
                                .filter((column) => typeof column.accessorFn !== "undefined" && column.getCanHide())
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
            </div>

            {/* Content Area */}
            <div key={viewMode} className="transition-all duration-200">
                {viewMode === 'card' ? (
                    <div className="grid gap-6 md:grid-cols-2 lg:grid-cols-3">
                        {table.getRowModel().rows.map((row) => (
                            <React.Fragment key={row.id}>
                                {renderCard(row.original)}
                            </React.Fragment>
                        ))}
                        {table.getRowModel().rows.length === 0 && (
                            <div className="col-span-full text-center py-10 text-muted-foreground">
                                {t('common.no_results', 'No results found.')}
                            </div>
                        )}
                    </div>
                ) : (
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
                )}
            </div>

            {/* Pagination is shared for both views! */}
            <div className="flex items-center justify-end space-x-2 py-4">
                <div className="flex-1 text-sm text-muted-foreground">
                    {t('common.page_of', `Page ${table.getState().pagination.pageIndex + 1} of ${table.getPageCount()}`).replace('{0}', String(table.getState().pagination.pageIndex + 1)).replace('{1}', String(table.getPageCount()))}
                </div>
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
