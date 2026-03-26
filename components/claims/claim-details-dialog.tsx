"use client"

import { useState } from "react"
import { format } from "date-fns"
import {
    Dialog,
    DialogContent,
    DialogDescription,
    DialogFooter,
    DialogHeader,
    DialogTitle,
} from "@/components/ui/dialog"
import { Button } from "@/components/ui/button"
import { Label } from "@/components/ui/label"
import { Separator } from "@/components/ui/separator"
import { Claim, claimApi } from "@/lib/claim-api"
import { ClaimStatusBadge } from "./claim-status-badge"
import { Badge } from "@/components/ui/badge"
import { ShieldAlert, AlertTriangle, CheckCircle2 } from "lucide-react"
import { cn } from "@/lib/utils"
import { useLanguage } from "@/contexts/language-context"

interface ClaimDetailsDialogProps {
    claim: Claim
    open: boolean
    onOpenChange: (open: boolean) => void
    onUpdate?: () => void
}

export function ClaimDetailsDialog({
    claim,
    open,
    onOpenChange,
    onUpdate
}: ClaimDetailsDialogProps) {
    const { t } = useLanguage()
    const [isUpdating, setIsUpdating] = useState(false)

    const handleStatusUpdate = async (newStatus: string) => {
        try {
            setIsUpdating(true)
            await claimApi.updateClaim(claim.id, { status: newStatus })
            if (onUpdate) onUpdate()
            onOpenChange(false)
        } catch (error) {
            console.error("Failed to update status:", error)
        } finally {
            setIsUpdating(false)
        }
    }

    return (
        <Dialog open={open} onOpenChange={onOpenChange}>
            <DialogContent className="sm:max-w-[600px]">
                <DialogHeader>
                    <div className="flex items-center justify-between">
                        <DialogTitle>{t('claim_details.title', 'Claim Details')} {claim.claim_number}</DialogTitle>
                        <ClaimStatusBadge status={claim.status} />
                    </div>
                    <DialogDescription>
                        Submitted on {format(new Date(claim.created_at), "PPP")}
                    </DialogDescription>
                </DialogHeader>

                <div className="grid gap-4 py-4 max-h-[60vh] overflow-y-auto">
                    <div className="grid grid-cols-2 gap-4">
                        <div>
                            <Label className="text-muted-foreground">{t('claim_details.incident_date', 'Incident Date')}</Label>
                            <div className="font-medium">{format(new Date(claim.incident_date), "PPP")}</div>
                        </div>
                        <div>
                            <Label className="text-muted-foreground">{t('claim_details.claim_amount', 'Claim Amount')}</Label>
                            <div className="font-medium">
                                {new Intl.NumberFormat("fr-SN", {
                                    style: "currency",
                                    currency: "XOF",
                                }).format(claim.claim_amount)}
                            </div>
                        </div>
                    </div>

                    <Separator />

                    <div>
                        <Label className="text-muted-foreground">{t('claim_details.description', 'Description')}</Label>
                        <div className="mt-1 text-sm">{claim.incident_description}</div>
                    </div>

                    {claim.incident_location && (
                        <div>
                            <Label className="text-muted-foreground">{t('claim_details.location', 'Location')}</Label>
                            <div className="mt-1 text-sm">{claim.incident_location}</div>
                        </div>
                    )}

                    {claim.evidence_files && claim.evidence_files.length > 0 && (
                        <div>
                            <Label className="text-muted-foreground">Evidence Files</Label>
                            <div className="flex flex-wrap gap-2 mt-2">
                                {claim.evidence_files.map((url, idx) => (
                                    <div key={idx} className="w-20 h-20 border rounded overflow-hidden">
                                        <img src={url} alt="Evidence" className="w-full h-full object-cover" />
                                    </div>
                                ))}
                            </div>
                        </div>
                    )}

                    <Separator />

                    {/* AI Assessment Section */}
                    <div className="bg-slate-50 p-4 rounded-lg border border-slate-200">
                        <div className="flex items-center justify-between mb-3">
                            <Label className="text-sm font-bold flex items-center gap-2">
                                <span className="p-1 bg-purple-100 text-purple-600 rounded">AI</span>
                                {t('claim_details.ai_assessment', 'AI Damage Assessment')}
                            </Label>
                            {!claim.ai_assessment && (
                                <Button
                                    size="sm"
                                    variant="secondary"
                                    onClick={async () => {
                                        try {
                                            setIsUpdating(true);
                                            await claimApi.analyzeClaimDamage(claim.id);
                                            if (onUpdate) onUpdate();
                                        } catch (e) {
                                            console.error("AI Analysis failed", e);
                                        } finally {
                                            setIsUpdating(false);
                                        }
                                    }}
                                    disabled={isUpdating || !claim.evidence_files?.length}
                                >
                                    {isUpdating ? "Analyzing..." : t('claim_details.run_ai_review', 'Run AI Review')}
                                </Button>
                            )}
                        </div>

                        {claim.ai_assessment ? (
                            <div className="space-y-3 animate-in fade-in slide-in-from-top-2">
                                <div className="flex gap-2">
                                    <Badge variant={
                                        claim.ai_assessment.severity === 'High' ? 'destructive' :
                                            claim.ai_assessment.severity === 'Medium' ? 'default' : 'secondary'
                                    }>
                                        Severity: {claim.ai_assessment.severity}
                                    </Badge>
                                    <Badge variant="outline">
                                        Confidence: {(claim.ai_assessment.confidence_score * 100).toFixed(0)}%
                                    </Badge>
                                </div>
                                <p className="text-sm text-slate-600 italic">
                                    "{claim.ai_assessment.damage_description}"
                                </p>
                                <div className="flex items-center justify-between pt-2 border-t border-slate-200 mt-2">
                                    <div>
                                        <span className="text-xs text-muted-foreground block uppercase">Suggested Estimate</span>
                                        <span className="font-bold text-lg">
                                            {new Intl.NumberFormat("fr-XOF", {
                                                style: "currency",
                                                currency: "XOF",
                                            }).format(claim.ai_assessment.suggested_estimate)}
                                        </span>
                                    </div>
                                    {claim.status === 'under_review' && !claim.approved_amount && (
                                        <Button
                                            size="sm"
                                            variant="ghost"
                                            className="text-purple-600 hover:text-purple-700 hover:bg-purple-50"
                                            onClick={async () => {
                                                try {
                                                    setIsUpdating(true);
                                                    await claimApi.updateClaim(claim.id, {
                                                        approved_amount: claim.ai_assessment!.suggested_estimate,
                                                        status: 'approved'
                                                    });
                                                    if (onUpdate) onUpdate();
                                                    onOpenChange(false);
                                                } catch (e) {
                                                    console.error("Failed to apply suggestion", e);
                                                } finally {
                                                    setIsUpdating(false);
                                                }
                                            }}
                                        >
                                            Apply Suggestion
                                        </Button>
                                    )}
                                </div>
                            </div>
                        ) : (
                            <p className="text-xs text-muted-foreground">
                                {claim.evidence_files?.length
                                    ? "No AI assessment performed yet."
                                    : t('claim_details.upload_photos_desc', "Upload photos to enable AI damage assessment.")}
                            </p>
                        )}
                    </div>

                    <Separator />

                    {/* Fraud Detection Section */}
                    <div className="bg-amber-50/50 p-4 rounded-lg border border-amber-100 mb-2">
                        <div className="flex items-center justify-between mb-3">
                            <Label className="text-sm font-bold flex items-center gap-2">
                                <ShieldAlert className="h-4 w-4 text-amber-600" />
                                {t('claim_details.fraud_review', 'Fraud & Risk Review')}
                            </Label>
                            <Button
                                size="sm"
                                variant="outline"
                                className="h-7 text-[10px] border-amber-200 text-amber-700 hover:bg-amber-100"
                                onClick={async (e) => {
                                    e.stopPropagation();
                                    try {
                                        setIsUpdating(true);
                                        await claimApi.analyzeClaimFraud(claim.id);
                                        if (onUpdate) onUpdate();
                                    } catch (e) {
                                        console.error("Fraud Check failed", e);
                                    } finally {
                                        setIsUpdating(false);
                                    }
                                }}
                                disabled={isUpdating}
                            >
                                {isUpdating ? "Scanning..." : t('claim_details.force_rescan', 'Force Re-scan')}
                            </Button>
                        </div>

                        {claim.fraud_score !== undefined ? (
                            <div className="space-y-4">
                                <div className="flex items-center gap-4">
                                    <div className="flex-1 h-2 bg-slate-200 rounded-full overflow-hidden">
                                        <div
                                            className={cn(
                                                "h-full transition-all duration-500",
                                                claim.fraud_score > 0.7 ? "bg-destructive" :
                                                    claim.fraud_score > 0.4 ? "bg-amber-500" : "bg-green-500"
                                            )}
                                            style={{ width: `${claim.fraud_score * 100}%` }}
                                        />
                                    </div>
                                    <span className={cn(
                                        "text-sm font-bold w-12",
                                        claim.fraud_score > 0.7 ? "text-destructive" :
                                            claim.fraud_score > 0.4 ? "text-amber-600" : "text-green-600"
                                    )}>
                                        {(claim.fraud_score * 100).toFixed(0)}%
                                    </span>
                                </div>

                                {claim.fraud_details?.risk_factors && claim.fraud_details.risk_factors.length > 0 ? (
                                    <div className="space-y-2">
                                        {claim.fraud_details.risk_factors.map((risk, i) => (
                                            <div key={i} className="flex gap-2 items-start bg-white p-2 rounded border border-amber-100 text-xs shadow-sm">
                                                <AlertTriangle className={cn(
                                                    "h-3 w-3 mt-0.5 shrink-0",
                                                    risk.severity === 'High' ? "text-destructive" : "text-amber-500"
                                                )} />
                                                <div className="flex-1">
                                                    <span className="font-semibold block">{risk.type.replace('_', ' ').toUpperCase()}</span>
                                                    <p className="text-muted-foreground font-normal">{risk.message}</p>
                                                </div>
                                            </div>
                                        ))}
                                    </div>
                                ) : (
                                    <p className="text-xs text-green-600 flex items-center gap-1">
                                        <CheckCircle2 className="h-3 w-3" /> No high-risk anomalies detected in recent scans.
                                    </p>
                                )}
                            </div>
                        ) : (
                            <p className="text-xs text-muted-foreground italic">
                                {t('claim_details.fraud_scan_desc', 'Fraud scan will run automatically during AI damage assessment.')}</p>
                        )}
                    </div>
                </div>

                <DialogFooter className="sm:justify-between">
                    <div className="flex gap-2">
                        {claim.status === 'submitted' && (
                            <>
                                <Button
                                    variant="outline"
                                    onClick={() => handleStatusUpdate('rejected')}
                                    disabled={isUpdating}
                                >
                                    Reject
                                </Button>
                                <Button
                                    onClick={() => handleStatusUpdate('under_review')}
                                    disabled={isUpdating}
                                >
                                    Start Review
                                </Button>
                            </>
                        )}
                        {claim.status === 'under_review' && (
                            <Button
                                className="bg-green-600 hover:bg-green-700"
                                onClick={() => handleStatusUpdate('approved')}
                                disabled={isUpdating}
                            >
                                Approve Claim
                            </Button>
                        )}
                        {claim.status === 'approved' && (
                            <Button
                                onClick={() => handleStatusUpdate('paid')}
                                disabled={isUpdating}
                            >
                                {t('claim_details.paid', 'Mark as Paid')}
                            </Button>
                        )}
                    </div>
                    <Button variant="ghost" onClick={() => onOpenChange(false)}>
                        {t('claim_details.close', 'Close')}
                    </Button>
                </DialogFooter>
            </DialogContent>
        </Dialog>
    )
}
