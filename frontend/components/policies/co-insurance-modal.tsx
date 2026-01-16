
"use client"

import * as React from "react"
import { Check, ChevronsUpDown } from "lucide-react"

import { cn } from "@/lib/utils"
import { Button } from "@/components/ui/button"
import {
    Dialog,
    DialogContent,
    DialogDescription,
    DialogHeader,
    DialogTitle,
} from "@/components/ui/dialog"
import { Input } from "@/components/ui/input"
import { Label } from "@/components/ui/label"
import { companyApi, Company } from "@/lib/company-api"
import { coInsuranceApi } from "@/lib/co-insurance-api"

interface CoInsuranceModalProps {
    open: boolean
    onOpenChange: (open: boolean) => void
    policyId: string
    onSuccess: () => void
}

export function CoInsuranceModal({
    open,
    onOpenChange,
    policyId,
    onSuccess
}: CoInsuranceModalProps) {
    const [companies, setCompanies] = React.useState<Company[]>([])
    const [selectedCompany, setSelectedCompany] = React.useState<string>("")
    const [sharePercentage, setSharePercentage] = React.useState<string>("10.0")
    const [feePercentage, setFeePercentage] = React.useState<string>("0.0")
    const [notes, setNotes] = React.useState("")
    const [loading, setLoading] = React.useState(false)
    const [search, setSearch] = React.useState("")

    React.useEffect(() => {
        const loadCompanies = async () => {
            try {
                const data = await companyApi.getCompanies(search)
                setCompanies(data)
            } catch (error) {
                console.error("Failed to load companies", error)
            }
        }
        if (open) {
            loadCompanies()
        }
    }, [open, search])

    const handleSave = async () => {
        if (!selectedCompany || !sharePercentage) return

        setLoading(true)
        try {
            await coInsuranceApi.addShare(policyId, {
                company_id: selectedCompany,
                share_percentage: parseFloat(sharePercentage),
                fee_percentage: parseFloat(feePercentage),
                notes
            })
            onSuccess()
            onOpenChange(false)
            // Reset
            setSelectedCompany("")
            setSharePercentage("10.0")
            setFeePercentage("0.0")
            setNotes("")
        } catch (error) {
            console.error("Failed to add share", error)
        } finally {
            setLoading(false)
        }
    }

    return (
        <Dialog open={open} onOpenChange={onOpenChange}>
            <DialogContent className="sm:max-w-[425px]">
                <DialogHeader>
                    <DialogTitle>Add Co-insurance Participant</DialogTitle>
                    <DialogDescription>
                        Assign a portion of this policy risk to another company.
                    </DialogDescription>
                </DialogHeader>
                <div className="grid gap-4 py-4">
                    <div className="grid gap-2">
                        <Label htmlFor="company">Select Insurance Company</Label>
                        <select
                            id="company"
                            className="flex h-10 w-full rounded-md border border-input bg-background px-3 py-2 text-sm ring-offset-background focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring focus-visible:ring-offset-2 disabled:cursor-not-allowed disabled:opacity-50"
                            value={selectedCompany}
                            onChange={(e) => setSelectedCompany(e.target.value)}
                        >
                            <option value="">Select a company...</option>
                            {companies.map((c) => (
                                <option key={c.id} value={c.id}>{c.name}</option>
                            ))}
                        </select>
                    </div>

                    <div className="grid grid-cols-2 gap-4">
                        <div className="grid gap-2">
                            <Label htmlFor="share">Share Percentage (%)</Label>
                            <Input
                                id="share"
                                type="number"
                                value={sharePercentage}
                                onChange={(e) => setSharePercentage(e.target.value)}
                                step="any"
                            />
                        </div>
                        <div className="grid gap-2">
                            <Label htmlFor="fee">Management Fee (%)</Label>
                            <Input
                                id="fee"
                                type="number"
                                value={feePercentage}
                                onChange={(e) => setFeePercentage(e.target.value)}
                                step="any"
                            />
                        </div>
                    </div>

                    <div className="grid gap-2">
                        <Label htmlFor="notes">Internal Notes</Label>
                        <Input
                            id="notes"
                            value={notes}
                            onChange={(e) => setNotes(e.target.value)}
                            placeholder="Optional notes about this agreement"
                        />
                    </div>
                </div>
                <div className="flex justify-end gap-3 mt-4">
                    <Button variant="outline" onClick={() => onOpenChange(false)}>Cancel</Button>
                    <Button onClick={handleSave} disabled={loading || !selectedCompany}>
                        {loading ? "Adding..." : "Add Participant"}
                    </Button>
                </div>
            </DialogContent>
        </Dialog>
    )
}
