"use client";

import { useState, useEffect } from "react";
import { useForm } from "react-hook-form";
import { zodResolver } from "@hookform/resolvers/zod";
import * as z from "zod";
import { portalApi } from "@/lib/portal-api";
import { useAuth } from "@/lib/auth";
import { useLanguage } from '@/contexts/language-context';

import { Button } from "@/components/ui/button";
import {
    Dialog,
    DialogContent,
    DialogDescription,
    DialogHeader,
    DialogTitle,
} from "@/components/ui/dialog";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import {
    Select,
    SelectContent,
    SelectItem,
    SelectTrigger,
    SelectValue
} from "@/components/ui/select";
import { Textarea } from "@/components/ui/textarea";
import { useToast } from "@/components/ui/use-toast";
import { Loader2 } from "lucide-react";

const claimSchema = z.object({
    policy_id: z.string().min(1, "Policy is required"),
    incident_date: z.string().min(1, "Incident date is required"),
    incident_description: z.string().min(10, "Description must be at least 10 characters"),
    incident_location: z.string().optional(),
    claim_amount: z.coerce.number().min(0, "Amount must be positive"),
    evidence_files: z.array(z.string()).default([]),
});

type ClaimFormData = z.infer<typeof claimSchema>;

interface PortalClaimDialogProps {
    open: boolean;
    onOpenChange: (open: boolean) => void;
    onSuccess?: () => void;
    defaultPolicyId?: string;
}

export function PortalClaimDialog({
    open,
    onOpenChange,
    onSuccess,
    defaultPolicyId,
}: PortalClaimDialogProps) {
    const { t } = useLanguage();
    const { toast } = useToast();
    const [loading, setLoading] = useState(false);
    const [fetchingPolicies, setFetchingPolicies] = useState(false);
    const [policies, setPolicies] = useState<any[]>([]);

    const {
        register,
        handleSubmit,
        setValue,
        watch,
        reset,
        formState: { errors },
    } = useForm<ClaimFormData>({
        resolver: zodResolver(claimSchema) as any,
        defaultValues: {
            incident_date: new Date().toISOString().split("T")[0],
            evidence_files: [],
        },
    });

    useEffect(() => {
        if (open) {
            const fetchPolicies = async () => {
                setFetchingPolicies(true);
                try {
                    const data = await portalApi.getMyPolicies();
                    setPolicies(data || []);

                    // Set default policy if provided
                    if (defaultPolicyId) {
                        setValue("policy_id", defaultPolicyId);
                    } else if (data && data.length > 0) {
                        // Or default to first one if not set
                        // setValue("policy_id", data[0].id);
                    }
                } catch (err) {
                    console.error("Failed to load policies", err);
                    toast({
                        variant: "destructive",
                        title: t('common.error', "Error"),
                        description: t('claims.load_error', "Failed to load your policies."),
                    });
                } finally {
                    setFetchingPolicies(false);
                }
            };
            fetchPolicies();
        }
    }, [open, toast, defaultPolicyId, setValue]);

    const onSubmit = async (data: ClaimFormData) => {
        setLoading(true);
        try {
            await portalApi.createClaim(data);
            await portalApi.createClaim(data);
            toast({
                title: t('claims.submitted', "Claim Submitted"),
                description: t('claims.submitted_desc', "Your claim has been filed successfully and is under review."),
            });
            if (onSuccess) onSuccess();
            onOpenChange(false);
            reset();
        } catch (err: any) {
            console.error(err);
            toast({
                variant: "destructive",
                title: t('claims.submit_failed', "Submission Failed"),
                description: err.response?.data?.detail || t('claims.fail_generic', "Failed to file claim"),
            });
        } finally {
            setLoading(false);
        }
    };

    return (
        <Dialog open={open} onOpenChange={onOpenChange}>
            <DialogContent className="sm:max-w-[600px]">
                <DialogHeader>
                    <DialogTitle>{t('claims.file_claim', 'File a Claim')}</DialogTitle>
                    <DialogDescription>
                        {t('claims.provide_details', 'Please provide details about the incident. Our team will review it shortly.')}
                    </DialogDescription>
                </DialogHeader>

                <form onSubmit={handleSubmit(onSubmit as any)} className="space-y-4 pt-4">
                    <div className="space-y-2">
                        <Label>{t('claims.select_policy', 'Select Covered Policy')}</Label>
                        <Select
                            disabled={fetchingPolicies}
                            onValueChange={(val) => setValue("policy_id", val)}
                            value={watch("policy_id")}
                        >
                            <SelectTrigger>
                                <SelectValue placeholder={fetchingPolicies ? t('common.loading_policies', "Loading policies...") : t('claims.select_policy_placeholder', "Select Policy")} />
                            </SelectTrigger>
                            <SelectContent>
                                {policies.map((p: any) => (
                                    <SelectItem key={p.id} value={p.id}>
                                        {p.policy_number} - {p.policy_type?.name || 'Policy'}
                                    </SelectItem>
                                ))}
                            </SelectContent>
                        </Select>
                        {errors.policy_id && <p className="text-red-500 text-sm">{errors.policy_id.message}</p>}
                    </div>

                    <div className="grid grid-cols-2 gap-4">
                        <div className="space-y-2">
                            <Label>{t('claims.incident_date', 'Incident Date')}</Label>
                            <Input type="date" {...register("incident_date")} />
                        </div>
                        <div className="space-y-2">
                            <Label>{t('claims.estimated_amount', 'Estimated Claim Amount (XOF)')}</Label>
                            <Input type="number" {...register("claim_amount")} />
                        </div>
                    </div>

                    <div className="space-y-2">
                        <Label>{t('claims.incident_location', 'Incident Location')}</Label>
                        <Input {...register("incident_location")} placeholder={t('claims.location_placeholder', "e.g. Abidjan, Plateau")} />
                    </div>

                    <div className="space-y-2">
                        <Label>{t('claims.incident_desc', 'Description of Incident')}</Label>
                        <Textarea {...register("incident_description")} placeholder={t('claims.desc_placeholder', "Describe exactly what happened...")} />
                        {errors.incident_description && <p className="text-red-500 text-sm">{errors.incident_description.message}</p>}
                    </div>

                    <div className="space-y-2">
                        <Label>{t('claims.evidence', 'Claim Evidence (Photos/Docs)')}</Label>
                        <div className="flex gap-2">
                            <Input
                                placeholder={t('claims.evidence_url', "URL of evidence (Demo only)")}
                                onKeyDown={(e: any) => {
                                    if (e.key === 'Enter') {
                                        // ... existing code ...
                                    }
                                }}
                            />
                        </div>
                        {/* ... existing code ... */}
                    </div>

                    <div className="flex justify-end gap-2 pt-4">
                        <Button type="button" variant="outline" onClick={() => onOpenChange(false)}>{t('common.cancel', 'Cancel')}</Button>
                        <Button type="submit" disabled={loading}>
                            {loading ? <Loader2 className="h-4 w-4 animate-spin mr-2" /> : null}
                            {loading ? t('common.submitting', "Submitting...") : t('claims.submit_btn', "Submit Claim")}
                        </Button>
                    </div>
                </form>
            </DialogContent>
        </Dialog>
    );
}
