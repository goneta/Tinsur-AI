"use client"

import { useEffect, useState, useCallback, useMemo } from "react"
import { useRouter } from "next/navigation"
import { Button } from "@/components/ui/button"
import { Badge } from "@/components/ui/badge"
import { Plus, Loader2, FileText } from "lucide-react"
import { EmptyState } from "@/components/ui/empty-state"
import { QuoteAPI } from "@/lib/api/quotes"
import { Quote } from "@/types/quote"
import { DataView } from "@/components/ui/data-view"
import { QuoteCard } from "@/components/quotes/quote-card"
import { columns as getColumns } from "./columns" // Import the factory
import { useToast } from "@/components/ui/use-toast"
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs"


import { premiumPolicyApi, PremiumPolicyType } from "@/lib/premium-policy-api"
import { useLanguage } from "@/contexts/language-context"

export default function QuotesPage() {
    const router = useRouter()
    const { toast } = useToast()
    const { t } = useLanguage()
    const [quotes, setQuotes] = useState<Quote[]>([])
    const [loading, setLoading] = useState(true)
    const [policyTypes, setPolicyTypes] = useState<Record<string, string>>({})
    const [premiumPolicyTypes, setPremiumPolicyTypes] = useState<Record<string, PremiumPolicyType>>({}) // Map id -> Object
    const [isMounted, setIsMounted] = useState(false)
    const [processingId, setProcessingId] = useState<string | null>(null)
    const [activeTab, setActiveTab] = useState("all")

    const fetchQuotes = async () => {
        setLoading(true)
        try {
            // Fetch all for client-side filtering
            const response = await QuoteAPI.list({ page_size: 1000 })
            setQuotes(response.quotes)

            // Fetch standard types
            const types = await QuoteAPI.listPolicyTypes()
            const typeMap: Record<string, string> = {}
            types.forEach(t => typeMap[t.id] = t.name)
            setPolicyTypes(typeMap)

            // Fetch Premium Policy Types (rich data)
            try {
                const premData = await premiumPolicyApi.getPolicyTypes()
                const premMap: Record<string, PremiumPolicyType> = {}
                if (premData && premData.premium_policy_types) {
                    premData.premium_policy_types.forEach(p => premMap[p.id] = p)
                }
                setPremiumPolicyTypes(premMap)
            } catch (err) {
                console.warn("Failed to fetch premium policies", err)
            }

        } catch (error) {
            toast({
                title: "Error",
                description: "Failed to load quotes",
                variant: "destructive",
            })
        } finally {
            setLoading(false)
        }
    }

    useEffect(() => {
        setIsMounted(true)
        fetchQuotes()
    }, [])

    // --- Action Handlers ---

    const handleDelete = useCallback(async (quote: Quote | string) => {
        const id = typeof quote === 'string' ? quote : quote.id
        if (!confirm(t("Are you sure you want to delete this quote?", "Are you sure you want to delete this quote?"))) return
        try {
            await QuoteAPI.delete(id)
            toast({ title: t("Success", "Success"), description: t("Quote deleted", "Quote deleted") })
            fetchQuotes()
        } catch (error) {
            toast({ title: t("Error", "Error"), description: t("Failed to delete quote", "Failed to delete quote"), variant: "destructive" })
        }
    }, [toast])

    const handleView = useCallback((id: string) => {
        router.push(`/dashboard/quotes/${id}`)
    }, [router])

    const handleSend = useCallback(async (quote: Quote) => {
        setProcessingId(quote.id)
        try {
            await QuoteAPI.send(quote.id)
            toast({ title: "Success", description: `Quote ${quote.quote_number} sent to client.` })
            fetchQuotes()
        } catch (error) {
            toast({ title: "Error", description: "Failed to send quote.", variant: "destructive" })
        } finally {
            setProcessingId(null)
        }
    }, [toast])

    const handleApprove = useCallback(async (quote: Quote) => {
        if (!confirm(`Approve quote ${quote.quote_number}? This will create an active policy.`)) return

        setProcessingId(quote.id)
        try {
            const result = await QuoteAPI.approve(quote.id)
            toast({
                title: "Quote Approved",
                description: `Policy ${result.policy_number} created successfully.`
            })
            fetchQuotes()
        } catch (error) {
            console.error(error)
            toast({ title: "Error", description: "Failed to approve quote.", variant: "destructive" })
        } finally {
            setProcessingId(null)
        }
    }, [toast])

    const handleReject = useCallback(async (quote: Quote) => {
        if (!confirm(`Reject quote ${quote.quote_number}?`)) return

        setProcessingId(quote.id)
        try {
            await QuoteAPI.reject(quote.id)
            toast({ title: "Quote Rejected", description: "Quote status updated." })
            fetchQuotes()
        } catch (error) {
            toast({ title: "Error", description: "Failed to reject quote.", variant: "destructive" })
        } finally {
            setProcessingId(null)
        }
    }, [toast])

    const handleArchive = useCallback(async (quote: Quote) => {
        if (!confirm(`Archive quote ${quote.quote_number}?`)) return

        setProcessingId(quote.id)
        try {
            await QuoteAPI.archive(quote.id)
            toast({ title: "Quote Archived", description: "Quote has been archived." })
            fetchQuotes()
        } catch (error) {
            console.log(error)
            toast({ title: "Error", description: "Failed to archive quote.", variant: "destructive" })
        } finally {
            setProcessingId(null)
        }
    }, [toast])

    const handleEdit = useCallback((quote: Quote) => {
        // Just mock for now or redirect
        toast({ title: "Edit", description: "Edit functionality coming soon." })
    }, [toast])


    // --- Filtering ---

    const filteredQuotes = useMemo(() => {
        if (activeTab === "all") return quotes
        return quotes.filter(q => q.status === activeTab)
    }, [quotes, activeTab])


    // --- Configuration ---

    // Adapter for legacy column delete signature 
    const onDeleteAdapter = (id: string) => handleDelete(id)

    const tableColumns = useMemo(() =>
        getColumns(handleView, onDeleteAdapter, handleSend, handleApprove, handleReject, handleArchive, policyTypes),
        [handleView, handleDelete, handleSend, handleApprove, handleReject, handleArchive, policyTypes]
    )


    const renderCard = useCallback((quote: Quote) => (
        <QuoteCard
            key={quote.id} // Enforce strict identity for individual state
            quote={quote}
            policyTypeName={policyTypes[quote.policy_type_id]}
            premiumPolicyType={premiumPolicyTypes[quote.policy_type_id]}
            onSend={handleSend}
            onApprove={handleApprove}
            onReject={handleReject}
            onArchive={handleArchive}
            onDelete={handleDelete}
            onEdit={handleEdit}
            loadingId={processingId}
        />
    ), [policyTypes, handleSend, handleApprove, handleReject, handleArchive, handleDelete, handleEdit, processingId])

    if (!isMounted) return null

    return (
        <div className="flex-1 space-y-4 p-8 pt-6">
            <div className="flex justify-between items-center">
                <div>
                    <h2 className="text-3xl font-bold tracking-tight">{t("Quotes", "Quotes")}</h2>
                    <p className="text-muted-foreground">{t("Manage insurance quotes and approvals", "Manage insurance quotes and approvals")}</p>
                </div>
                <Button onClick={() => router.push("/dashboard/quotes/new")}>
                    <Plus className="mr-2 h-4 w-4" /> {t("New Quote", "New Quote")}
                </Button>
            </div>

            <Tabs defaultValue="all" value={activeTab} onValueChange={setActiveTab} className="w-full">

            <div className="mt-3 flex flex-wrap items-center gap-2 text-xs font-bold uppercase tracking-widest text-muted-foreground">
                <span>{t("Lifecycle", "Lifecycle")}:</span>
                <Badge role="button" onClick={() => setActiveTab('draft')} variant="secondary" className="cursor-pointer">Draft</Badge>
                <Badge role="button" onClick={() => setActiveTab('draft_from_client')} variant="secondary" className="cursor-pointer">Draft (Client)</Badge>
                <span className="text-muted-foreground">?</span>
                <Badge role="button" onClick={() => setActiveTab('sent')} variant="default" className="cursor-pointer">Sent</Badge>
                <Badge role="button" onClick={() => setActiveTab('submitted')} variant="default" className="cursor-pointer">Submitted</Badge>
                <Badge role="button" onClick={() => setActiveTab('under_review')} variant="default" className="cursor-pointer">Under Review</Badge>
                <span className="text-muted-foreground">?</span>
                <Badge role="button" onClick={() => setActiveTab('accepted')} variant="default" className="cursor-pointer">Accepted</Badge>
                <span className="text-muted-foreground">?</span>
                <Badge role="button" onClick={() => setActiveTab('policy_created')} variant="default" className="cursor-pointer">Policy Created</Badge>
                <span className="text-muted-foreground">?</span>
                <Badge role="button" onClick={() => setActiveTab('archived')} variant="outline" className="cursor-pointer">Archived</Badge>
                <Badge role="button" onClick={() => setActiveTab('rejected')} variant="destructive" className="cursor-pointer">Rejected</Badge>
                <Badge role="button" onClick={() => setActiveTab('expired')} variant="destructive" className="cursor-pointer">Expired</Badge>
                <Button variant="ghost" size="sm" className="h-6 px-2 text-[10px]" onClick={() => setActiveTab('all')}>{t("Reset", "Reset")}</Button>
            </div>

                <TabsList>
                    <TabsTrigger value="all">{t("All Quotes", "All Quotes")}</TabsTrigger>
                    <TabsTrigger value="draft">{t("Draft", "Draft")}</TabsTrigger>
                    <TabsTrigger value="draft_from_client">{t("Draft (Client)", "Draft (Client)")}</TabsTrigger>
                    <TabsTrigger value="sent">{t("Sent", "Sent")}</TabsTrigger>
                    <TabsTrigger value="under_review">{t("Under Review", "Under Review")}</TabsTrigger>
                    <TabsTrigger value="accepted">{t("Accepted", "Accepted")}</TabsTrigger>
                    <TabsTrigger value="policy_created">{t("Policy Created", "Policy Created")}</TabsTrigger>
                    <TabsTrigger value="archived" className="text-red-500 data-[state=active]:text-red-600">{t("Archived", "Archived")}</TabsTrigger>
                </TabsList>

                <div className="mt-4">
                    {loading ? (
                        <div className="flex flex-col items-center justify-center py-20 gap-4">
                            <Loader2 className="h-8 w-8 animate-spin text-primary" />
                            <p className="text-muted-foreground">{t("Loading quotes...", "Loading quotes...")}</p>
                        </div>
                    ) : filteredQuotes.length === 0 ? (
                        <div className="py-10">
                            <EmptyState
                                title={t("No quotes found", "No quotes found")}
                                description={activeTab === 'all' ? t("You haven't generated any insurance quotes yet.", "You haven't generated any insurance quotes yet.") : `${t("No quotes found", "No quotes found")} '${activeTab}'.`}
                                icon={FileText}
                                action={activeTab === 'all' ? {
                                    label: t("Create First Quote", "Create First Quote"),
                                    onClick: () => router.push("/dashboard/quotes/new"),
                                    icon: Plus
                                } : undefined}
                            />
                        </div>
                    ) : (
                        <div className="animate-in fade-in-50 duration-500">
                            <DataView
                                columns={tableColumns}
                                data={filteredQuotes}
                                renderCard={renderCard}
                                defaultView="card"
                                getRowId={(row) => row.id}
                            />
                        </div>
                    )}
                </div>
            </Tabs>
        </div>
    )
}
