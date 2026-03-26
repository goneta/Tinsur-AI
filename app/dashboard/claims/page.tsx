"use client"

import { useState, useEffect, useCallback, useMemo } from "react"
import { claimApi } from "@/lib/claim-api"
import { useLanguage } from "@/contexts/language-context"
import { Claim } from "@/types/claim"
import { DataTable } from "@/components/ui/data-table"
import { columns } from "./columns"
import { ClaimDetailsDialog } from "@/components/claims/claim-details-dialog"
import { ClipboardList } from "lucide-react"
import { EmptyState } from "@/components/ui/empty-state"
import { Button } from "@/components/ui/button"
import { Plus } from "lucide-react"
import { ClaimFormDialog } from "@/components/claims/claim-form-dialog"

export default function ClaimsPage() {
    const { t, formatPrice } = useLanguage()
    const [claims, setClaims] = useState<Claim[]>([])
    const [isLoading, setIsLoading] = useState(true)
    const [selectedClaim, setSelectedClaim] = useState<Claim | null>(null)
    const [detailsOpen, setDetailsOpen] = useState(false)
    const [createOpen, setCreateOpen] = useState(false)

    async function loadClaims() {
        try {
            setIsLoading(true)
            // Fetch all claims for client-side filtering
            const data = await claimApi.getClaims({ limit: 1000 })
            // Ensure data fits the type, the API might allow undefined params for getClaims
            // Based on claim-api.ts, getClaims returns Claim[]
            setClaims(data)
        } catch (error) {
            console.error("Failed to load claims:", error)
        } finally {
            setIsLoading(false)
        }
    }

    useEffect(() => {
        loadClaims()
    }, [])

    const handleViewDetails = useCallback((claim: Claim) => {
        setSelectedClaim(claim)
        setDetailsOpen(true)
    }, [])

    const tableColumns = useMemo(() => columns(handleViewDetails, t, formatPrice), [handleViewDetails, t, formatPrice])

    return (
        <div className="flex flex-col gap-6 p-8">
            <div className="flex items-center justify-between">
                <div>
                    <h1 className="text-3xl font-bold tracking-tight">{t('claims.title', 'Claims Management')}</h1>
                    <p className="text-muted-foreground mt-2">
                        {t('claims.subtitle', 'View and process insurance claims.')}
                    </p>
                </div>
                <Button onClick={() => setCreateOpen(true)}>
                    <Plus className="mr-2 h-4 w-4" /> {t('claims.new_claim', 'New Claim')}
                </Button>
            </div>

            {isLoading ? (
                <div className="p-8 text-center text-muted-foreground">{t('common.loading', 'Loading claims...')}</div>
            ) : claims.length === 0 ? (
                <EmptyState
                    title={t('claims.no_claims', 'No claims to process')}
                    description={t('claims.no_claims_desc', 'There are currently no insurance claims in the system. When clients submit claims, they will appear here for review.')}
                    icon={ClipboardList}
                    action={{
                        label: t('claims.create_first', 'Create First Claim'),
                        onClick: () => setCreateOpen(true),
                        icon: Plus
                    }}
                />
            ) : (
                <div className="rounded-md border bg-white p-4">
                    <DataTable
                        columns={tableColumns}
                        data={claims}
                    />
                </div>
            )}

            {selectedClaim && (
                <ClaimDetailsDialog
                    claim={selectedClaim}
                    open={detailsOpen}
                    onOpenChange={setDetailsOpen}
                    onUpdate={loadClaims}
                />
            )}

            <ClaimFormDialog
                open={createOpen}
                onOpenChange={setCreateOpen}
                onSuccess={() => {
                    loadClaims()
                    setCreateOpen(false)
                }}
            />
        </div>
    )
}
