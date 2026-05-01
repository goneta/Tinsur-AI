"use client";

import { useState, useEffect } from "react";
import { useForm } from "react-hook-form";
import { zodResolver } from "@hookform/resolvers/zod";
import * as z from "zod";
import { format } from "date-fns";
import { api } from "@/lib/api";
import { claimApi } from "@/lib/claim-api";
import { useLanguage } from "@/contexts/language-context";

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

// Schema for creating a claim
const claimSchema = z.object({
    policy_id: z.string().min(1, "Policy is required"),
    incident_date: z.string().min(1, "Incident date is required"),
    incident_description: z.string().min(10, "Description must be at least 10 characters"),
    incident_location: z.string().optional(),
    claim_amount: z.coerce.number().min(0, "Amount must be positive"),
    created_by: z.string().optional(),
    evidence_files: z.array(z.string()).optional(),
});

type ClaimFormData = z.infer<typeof claimSchema>;

interface ClaimFormDialogProps {
    open: boolean;
    onOpenChange: (open: boolean) => void;
    onSuccess: () => void;
}

export function ClaimFormDialog({
    open,
    onOpenChange,
    onSuccess,
}: ClaimFormDialogProps) {
    const { t } = useLanguage();
    const [loading, setLoading] = useState(false);
    const [error, setError] = useState("");
    const [policies, setPolicies] = useState<any[]>([]);
    const [employees, setEmployees] = useState<any[]>([]);

    const {
        register,
        handleSubmit,
        setValue,
        watch,
        reset,
        formState: { errors },
    } = useForm<ClaimFormData>({
        resolver: zodResolver(claimSchema),
        defaultValues: {
            incident_date: new Date().toISOString().split("T")[0],
        },
    });

    useEffect(() => {
        if (open) {
            const fetchData = async () => {
                try {
                    // Fetch policies (active ones ideally)
                    // We don't have a direct 'active policies' endpoint handy here, 
                    // so we list policies. In a real app we'd filter or search.
                    const [policiesRes, employeesRes] = await Promise.all([
                        api.get("/policies/"), // returns {policies: [...], total: ...}
                        api.get("/employees/") // returns [...]
                    ]);

                    if (policiesRes.data && policiesRes.data.policies) {
                        setPolicies(policiesRes.data.policies);
                    }
                    if (employeesRes.data) {
                        setEmployees(employeesRes.data);
                    }
                } catch (err) {
                    console.error("Failed to load data", err);
                }
            };
            fetchData();
        }
    }, [open]);

    const onSubmit = async (data: ClaimFormData) => {
        setLoading(true);
        setError("");
        try {
            await claimApi.createClaim(data as any);
            onSuccess();
            onOpenChange(false);
            reset();
        } catch (err: any) {
            console.error(err);
            setError(err.response?.data?.detail || "Failed to create claim");
        } finally {
            setLoading(false);
        }
    };

    return (
        <Dialog open={open} onOpenChange={onOpenChange}>
            <DialogContent className="sm:max-w-[600px]">
                <DialogHeader>
                    <DialogTitle>{t('claims.file_new', 'File New Claim')}</DialogTitle>
                    <DialogDescription>
                        {t('claims.file_new_desc', 'Record a new insurance claim for a policy.')}
                    </DialogDescription>
                </DialogHeader>

                <form onSubmit={handleSubmit(onSubmit)} className="space-y-4">
                    {error && (
                        <div className="bg-red-50 text-red-700 p-3 rounded-md text-sm">
                            {error}
                        </div>
                    )}

                    <div className="space-y-2">
                        <Label>{t('claims.policy', 'Policy')}</Label>
                        <Select
                            onValueChange={(val) => setValue("policy_id", val)}
                        >
                            <SelectTrigger>
                                <SelectValue placeholder={t('claims.select_policy', 'Select Policy')} />
                            </SelectTrigger>
                            <SelectContent>
                                {policies.map((p: any) => (
                                    <SelectItem key={p.id} value={p.id}>
                                        {p.policy_number} - {p.policy_type?.name || 'Policy'} ({(p.client?.first_name || p.client?.business_name)})
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
                            <Label>{t('claims.estimated_amount', 'Estimated Amount (XOF)')}</Label>
                            <Input type="number" {...register("claim_amount")} />
                        </div>
                    </div>

                    <div className="space-y-2">
                        <Label>{t('claims.location', 'Location')}</Label>
                        <Input {...register("incident_location")} placeholder="e.g. Abidjan, Cocody" />
                    </div>

                    <div className="space-y-2">
                        <Label>{t('claims.description', 'Description')}</Label>
                        <Textarea {...register("incident_description")} placeholder="Describe what happened..." />
                        {errors.incident_description && <p className="text-red-500 text-sm">{errors.incident_description.message}</p>}
                    </div>

                    <div className="space-y-2">
                        <Label>{t('claims.created_by', 'Created By (Agent)')}</Label>
                        <Select
                            onValueChange={(val) => setValue("created_by", val)}
                        >
                            <SelectTrigger>
                                <SelectValue placeholder={t('claims.select_agent', 'Select Agent')} />
                            </SelectTrigger>
                            <SelectContent>
                                {employees.map((emp: any) => (
                                    <SelectItem key={emp.id} value={emp.id}>
                                        {emp.first_name} {emp.last_name}
                                    </SelectItem>
                                ))}
                            </SelectContent>
                        </Select>
                    </div>

                    <div className="space-y-2">
                        <Label>{t('claims.damage_photos', 'Damage Photos / Evidence')}</Label>
                        <div className="flex gap-2">
                            <Input
                                placeholder={t('claims.paste_url', 'Paste image URL (Simulation)')}
                                onKeyDown={(e: any) => {
                                    if (e.key === 'Enter') {
                                        e.preventDefault();
                                        const url = e.target.value;
                                        if (url) {
                                            const current = watch("evidence_files") || [];
                                            setValue("evidence_files", [...current, url]);
                                            e.target.value = "";
                                        }
                                    }
                                }}
                            />
                            <Button type="button" variant="secondary">{t('btn.upload', 'Upload')}</Button>
                        </div>
                        <div className="flex flex-wrap gap-2 mt-2">
                            {(watch("evidence_files") || []).map((url: string, idx: number) => (
                                <div key={idx} className="relative w-16 h-16 border rounded bg-slate-50 overflow-hidden group">
                                    <img src={url} alt="Evidence" className="w-full h-full object-cover" />
                                    <button
                                        type="button"
                                        className="absolute inset-0 bg-black/40 text-white opacity-0 group-hover:opacity-100 flex items-center justify-center transition-opacity"
                                        onClick={() => {
                                            const current = watch("evidence_files") || [];
                                            setValue("evidence_files", current.filter((_, i) => i !== idx));
                                        }}
                                    >
                                        &times;
                                    </button>
                                </div>
                            ))}
                        </div>
                    </div>

                    <div className="flex justify-end gap-2 pt-4">
                        <Button type="button" variant="outline" onClick={() => onOpenChange(false)}>{t('btn.cancel', 'Cancel')}</Button>
                        <Button type="submit" disabled={loading}>
                            {loading ? t('btn.creating', 'Creating...') : t('claims.create_claim', 'Create Claim')}
                        </Button>
                    </div>
                </form>
            </DialogContent>
        </Dialog>
    );
}
