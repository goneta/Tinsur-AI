"use client"

import { useEffect, useState } from "react"
import { format } from "date-fns"
import { MoreHorizontal, FileText, Activity } from "lucide-react"

import {
    Table,
    TableBody,
    TableCell,
    TableHead,
    TableHeader,
    TableRow,
} from "@/components/ui/table"
import {
    DropdownMenu,
    DropdownMenuContent,
    DropdownMenuItem,
    DropdownMenuLabel,
    DropdownMenuSeparator,
    DropdownMenuTrigger,
} from "@/components/ui/dropdown-menu"
import { Button } from "@/components/ui/button"
import { claimApi, Claim } from "@/lib/claim-api"
import { ClaimStatusBadge } from "./claim-status-badge"
import { ClaimDetailsDialog } from "./claim-details-dialog"

export function ClaimsTable() {
    const [claims, setClaims] = useState<Claim[]>([])
    const [isLoading, setIsLoading] = useState(true)
    const [selectedClaim, setSelectedClaim] = useState<Claim | null>(null)
    const [detailsOpen, setDetailsOpen] = useState(false)

    useEffect(() => {
        loadClaims()
    }, [])

    async function loadClaims() {
        try {
            setIsLoading(true)
            const data = await claimApi.getClaims()
            setClaims(data)
        } catch (error) {
            console.error("Failed to load claims:", error)
        } finally {
            setIsLoading(false)
        }
    }

    if (isLoading) {
        return <div className="p-8 text-center text-muted-foreground">Loading claims...</div>
    }

    if (claims.length === 0) {
        return (
            <div className="flex flex-col items-center justify-center p-8 text-center border rounded-md bg-white">
                <Activity className="h-10 w-10 text-muted-foreground mb-4" />
                <h3 className="text-lg font-medium">No claims found</h3>
                <p className="text-sm text-muted-foreground mt-1">
                    No claims have been submitted yet.
                </p>
            </div>
        )
    }

    return (
        <div className="rounded-md border bg-white">
            <Table>
                <TableHeader>
                    <TableRow>
                        <TableHead>Claim Number</TableHead>
                        <TableHead>Incident Date</TableHead>
                        <TableHead>Description</TableHead>
                        <TableHead>Amount</TableHead>
                        <TableHead>Status</TableHead>
                        <TableHead className="text-right">Actions</TableHead>
                    </TableRow>
                </TableHeader>
                <TableBody>
                    {claims.map((claim) => (
                        <TableRow key={claim.id}>
                            <TableCell className="font-medium">{claim.claim_number}</TableCell>
                            <TableCell>{format(new Date(claim.incident_date), "MMM d, yyyy")}</TableCell>
                            <TableCell className="max-w-[300px] truncate" title={claim.incident_description}>
                                {claim.incident_description}
                            </TableCell>
                            <TableCell>
                                {new Intl.NumberFormat("fr-SN", {
                                    style: "currency",
                                    currency: "XOF",
                                }).format(claim.claim_amount)}
                            </TableCell>
                            <TableCell>
                                <ClaimStatusBadge status={claim.status} />
                            </TableCell>
                            <TableCell className="text-right">
                                <DropdownMenu>
                                    <DropdownMenuTrigger asChild>
                                        <Button variant="ghost" className="h-8 w-8 p-0">
                                            <span className="sr-only">Open menu</span>
                                            <MoreHorizontal className="h-4 w-4" />
                                        </Button>
                                    </DropdownMenuTrigger>
                                    <DropdownMenuContent align="end">
                                        <DropdownMenuLabel>Actions</DropdownMenuLabel>
                                        <DropdownMenuItem
                                            onClick={() => navigator.clipboard.writeText(claim.claim_number)}
                                        >
                                            Copy Claim Number
                                        </DropdownMenuItem>
                                        <DropdownMenuSeparator />
                                        <DropdownMenuItem
                                            onClick={() => {
                                                setSelectedClaim(claim)
                                                setDetailsOpen(true)
                                            }}
                                        >
                                            View Details
                                        </DropdownMenuItem>
                                        <DropdownMenuItem>Update Status</DropdownMenuItem>
                                    </DropdownMenuContent>
                                </DropdownMenu>
                            </TableCell>
                        </TableRow>
                    ))}
                </TableBody>
            </Table>

            {selectedClaim && (
                <ClaimDetailsDialog
                    claim={selectedClaim}
                    open={detailsOpen}
                    onOpenChange={setDetailsOpen}
                    onUpdate={loadClaims}
                />
            )}
        </div>
    )
}
