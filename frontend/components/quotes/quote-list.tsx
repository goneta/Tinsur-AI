import { Quote } from "@/types/quote"
import { DataTable } from "@/components/ui/data-table"
import { useMemo } from "react"
import { columns } from "@/app/dashboard/quotes/columns"

interface QuoteListProps {
    quotes: Quote[]
    policyTypes: Record<string, string>
    onView: (id: string) => void
    onDelete: (id: string) => void
    onSend: (quote: Quote) => void
    onApprove: (quote: Quote) => void
    onReject: (quote: Quote) => void
}

export function QuoteList({
    quotes,
    policyTypes,
    onView,
    onDelete,
    onSend,
    onApprove,
    onReject
}: QuoteListProps) {

    const tableColumns = useMemo(() =>
        columns(onView, onDelete, onSend, onApprove, onReject, policyTypes),
        [onView, onDelete, onSend, onApprove, onReject, policyTypes]
    )

    return (
        <div className="rounded-md border bg-white p-4">
            <DataTable
                columns={tableColumns}
                data={quotes}
            />
        </div>
    )
}
