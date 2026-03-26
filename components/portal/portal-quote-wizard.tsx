"use client";

import { useState, useEffect } from "react";
import { useForm, FormProvider } from "react-hook-form";
import { QuoteAPI } from "@/lib/api/quotes";
import { portalApi } from "@/lib/portal-api";
import { PremiumPolicyType } from "@/lib/premium-policy-api";
import { PremiumPolicyCard } from "../quotes/premium-policy-card";
import { UniversalEntityCard } from "@/components/shared/universal-entity-card";
import { Button } from "@/components/ui/button";
import {
    Form,
    FormControl,
    FormField,
    FormItem,
    FormLabel,
    FormMessage
} from "@/components/ui/form";
import { Input } from "@/components/ui/input";
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select";
import { useToast } from "@/components/ui/use-toast";
import {
    Loader2, ArrowRight, ArrowLeft, Calculator, ShieldCheck,
    Car, GlassWater, Globe, UserCheck, Monitor, Key,
    HeartPulse, Briefcase, Baby, Lock, Sparkles, Fuel,
    Plane, AlertTriangle, Hotel, Scale, Wrench, KeyRound,
    Droplets, Plus, Minus, ChevronDown, ChevronUp, Check
} from "lucide-react";
import { formatCurrency } from "@/lib/utils";
import { RiskFactorForm } from "../quotes/risk-factor-form";
import {
    Dialog,
    DialogContent,
    DialogDescription,
    DialogHeader,
    DialogTitle,
    DialogFooter
} from "@/components/ui/dialog";
import {
    AlertDialog,
    AlertDialogAction,
    AlertDialogContent,
    AlertDialogDescription,
    AlertDialogFooter,
    AlertDialogHeader,
    AlertDialogTitle,
} from "@/components/ui/alert-dialog";
import { Label } from "@/components/ui/label";
import { Checkbox } from "@/components/ui/checkbox";
import { Badge } from "@/components/ui/badge";

interface WizardValues {
    policy_type_id: string;
    coverage_amount: number;
    duration_months: number;
    premium_frequency: string;
    risk_factors: Record<string, any>;
    selected_services: string[];
}

interface PortalQuoteWizardProps {
    open: boolean;
    onOpenChange: (open: boolean) => void;
    onSuccess?: () => void;
}

export function PortalQuoteWizard({ open, onOpenChange, onSuccess }: PortalQuoteWizardProps) {
    const { toast } = useToast();
    const [step, setStep] = useState(1);
    const [loading, setLoading] = useState(false);
    const [showAllServices, setShowAllServices] = useState(false);

    // Matching State
    const [eligiblePolicies, setEligiblePolicies] = useState<PremiumPolicyType[]>([]);
    const [recommendedPolicyId, setRecommendedPolicyId] = useState<string | null>(null);
    const [selectedPolicy, setSelectedPolicy] = useState<PremiumPolicyType | null>(null);

    const [calculation, setCalculation] = useState<any | null>(null);

    // Errors
    const [noPolicyOpen, setNoPolicyOpen] = useState(false);
    const [noPolicyMessage, setNoPolicyMessage] = useState("");
    const [missingInfoOpen, setMissingInfoOpen] = useState(false);
    const [missingFields, setMissingFields] = useState<string[]>([]);

    const methods = useForm<WizardValues>({
        defaultValues: {
            duration_months: 12,
            premium_frequency: "annual",
            risk_factors: {},
            selected_services: []
        }
    });

    const { handleSubmit, reset, setValue, watch, getValues } = methods;

    // Reset and Match on Open
    useEffect(() => {
        if (open) {
            setStep(1);
            setCalculation(null);
            setSelectedPolicy(null);
            reset();
            checkEligibility();
        }
    }, [open]);

    const checkEligibility = async () => {
        setLoading(true);
        try {
            // No clientID needed for portal user
            const result = await QuoteAPI.matchPolicies();

            if (result.status === "success") {
                setEligiblePolicies(result.data);
                setRecommendedPolicyId(result.recommended_id);
                // Remain on Step 1 (Policy Selection)
            } else if (result.status === "no_policies") {
                setNoPolicyMessage(result.message);
                setNoPolicyOpen(true);
            } else if (result.status === "missing_info") {
                setMissingFields(result.missing_fields || []);
                setMissingInfoOpen(true);
            }
        } catch (e: any) {
            const detail = e.response?.data?.detail;
            if (detail?.code === "NO_PREMIUM_POLICIES") {
                setNoPolicyMessage(detail.message);
                setNoPolicyOpen(true);
            } else if (detail?.code === "MISSING_CLIENT_INFO") {
                setMissingFields(detail.missing_fields || []);
                setMissingInfoOpen(true);
            } else {
                toast({ title: "Error", description: "Failed to check eligibility", variant: "destructive" });
            }
        } finally {
            setLoading(false);
        }
    }

    const handlePolicySelect = (policy: PremiumPolicyType) => {
        setSelectedPolicy(policy);
        setValue("policy_type_id", policy.id);
        setStep(2);
    };

    const onCalculate = async (data: WizardValues) => {
        setLoading(true);
        try {
            const result = await portalApi.calculateQuote(data);
            setCalculation(result);
            setStep(3);
        } catch (e: any) {
            toast({
                title: "Calculation Failed",
                description: e.response?.data?.detail || "Could not calculate premium.",
                variant: "destructive"
            });
        } finally {
            setLoading(false);
        }
    };

    const onCreate = async () => {
        setLoading(true);
        const data = methods.getValues();
        try {
            await portalApi.createQuote({
                ...data,
                details: { ...data.risk_factors, final_premium: calculation?.total_installment_price },
                discount_percent: 0
            });
            toast({ title: "Quote Saved", description: "Your quote has been saved. We will contact you shortly." });
            if (onSuccess) onSuccess();
            onOpenChange(false);
        } catch (e: any) {
            toast({
                title: "Error",
                description: e.response?.data?.detail || "Failed to save quote",
                variant: "destructive"
            });
        } finally {
            setLoading(false);
        }
    };

    return (
        <Dialog open={open} onOpenChange={onOpenChange}>
            <DialogContent className="sm:max-w-[800px] max-h-[90vh] overflow-y-auto">
                <DialogHeader>
                    <DialogTitle>Get a Quote</DialogTitle>
                    <DialogDescription>
                        {step === 1 && "Start by selecting the best policy for you."}
                        {step === 2 && "Customize your coverage."}
                        {step === 3 && "Review your estimated premium."}
                    </DialogDescription>
                </DialogHeader>

                <div className="py-2">
                    {loading && step === 1 && !eligiblePolicies.length ? (
                        <div className="flex justify-center py-20">
                            <Loader2 className="h-8 w-8 animate-spin text-primary" />
                        </div>
                    ) : (
                        <div className="space-y-6">

                            {/* STEP 1: POLICY SELECTION */}
                            {step === 1 && (
                                <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                                    {eligiblePolicies.map(policy => (
                                        <PremiumPolicyCard
                                            key={policy.id}
                                            policy={policy}
                                            onSelect={handlePolicySelect}
                                            isRecommended={policy.id === recommendedPolicyId}
                                            isSelected={selectedPolicy?.id === policy.id}
                                        />
                                    ))}
                                </div>
                            )}

                            {/* STEP 2: CONFIGURE */}
                            {step === 2 && selectedPolicy && (
                                <FormProvider {...methods}>
                                    <form className="space-y-6">
                                        <div className="flex items-center gap-2 p-2 bg-muted/50 rounded-md">
                                            <Badge variant="outline" className="bg-background">Selected Policy</Badge>
                                            <span className="font-medium">{selectedPolicy.name}</span>
                                            <Button type="button" variant="ghost" size="sm" className="ml-auto h-6" onClick={() => setStep(1)}>Change</Button>
                                        </div>

                                        <div className="grid grid-cols-2 gap-4">
                                            <FormField
                                                control={methods.control}
                                                name="coverage_amount"
                                                rules={{ required: "Required", min: 0 }}
                                                render={({ field }) => (
                                                    <FormItem>
                                                        <FormLabel>Coverage Amount (XOF)</FormLabel>
                                                        <FormControl>
                                                            <Input type="number" {...field} onChange={e => field.onChange(parseFloat(e.target.value))} />
                                                        </FormControl>
                                                        <FormMessage />
                                                    </FormItem>
                                                )}
                                            />
                                            <FormField
                                                control={methods.control}
                                                name="duration_months"
                                                rules={{ required: "Required", min: 1 }}
                                                render={({ field }) => (
                                                    <FormItem>
                                                        <FormLabel>Duration (Months)</FormLabel>
                                                        <FormControl>
                                                            <Input type="number" {...field} onChange={e => field.onChange(parseInt(e.target.value))} />
                                                        </FormControl>
                                                        <FormMessage />
                                                    </FormItem>
                                                )}
                                            />
                                        </div>

                                        <FormField
                                            control={methods.control}
                                            name="premium_frequency"
                                            render={({ field }) => (
                                                <FormItem>
                                                    <FormLabel>Payment Frequency</FormLabel>
                                                    <Select onValueChange={field.onChange} defaultValue={field.value}>
                                                        <FormControl>
                                                            <SelectTrigger>
                                                                <SelectValue placeholder="Select frequency" />
                                                            </SelectTrigger>
                                                        </FormControl>
                                                        <SelectContent>
                                                            <SelectItem value="monthly">Monthly</SelectItem>
                                                            <SelectItem value="quarterly">Quarterly</SelectItem>
                                                            <SelectItem value="semi-annual">Semi-Annual</SelectItem>
                                                            <SelectItem value="annual">Annual</SelectItem>
                                                        </SelectContent>
                                                    </Select>
                                                    <FormMessage />
                                                </FormItem>
                                            )}
                                        />

                                        <RiskFactorForm policyTypeCode={selectedPolicy.code || ''} />

                                        {selectedPolicy.services && selectedPolicy.services.length > 0 && (
                                            <div className="space-y-6 pt-6 border-t">
                                                <div className="flex items-center justify-between">
                                                    <h4 className="text-lg font-black uppercase tracking-tight text-gray-900">Premium Services</h4>
                                                    <Badge className="bg-[#00539F] text-white px-3 py-1 rounded-full text-[10px] font-black uppercase">Optional Add-ons</Badge>
                                                </div>

                                                <div className="grid grid-cols-1 gap-4">
                                                    {selectedPolicy.services
                                                        .slice(0, showAllServices ? undefined : 4)
                                                        .map((service) => {
                                                            const Icon = ({
                                                                ShieldCheck, Car, GlassWater, Globe, UserCheck, Monitor, Key,
                                                                HeartPulse, Briefcase, Baby, Lock, Sparkles, Fuel,
                                                                Plane, AlertTriangle, Hotel, Scale, Wrench, KeyRound, Droplets
                                                            } as any)[service.icon_name || "ShieldCheck"] || ShieldCheck;

                                                            const isChecked = watch("selected_services")?.includes(service.id);

                                                            return (
                                                                <FormField
                                                                    key={service.id}
                                                                    control={methods.control}
                                                                    name="selected_services"
                                                                    render={({ field }) => (
                                                                        <FormItem
                                                                            className={`
                                                                                flex flex-row items-center space-x-4 space-y-0 rounded-2xl border-2 p-5 transition-all cursor-pointer
                                                                                ${isChecked ? 'border-[#00539F] bg-blue-50/50 shadow-md' : 'border-gray-100 bg-white hover:border-gray-300'}
                                                                            `}
                                                                            onClick={() => {
                                                                                const current = field.value || [];
                                                                                const next = current.includes(service.id)
                                                                                    ? current.filter((v: string) => v !== service.id)
                                                                                    : [...current, service.id];
                                                                                field.onChange(next);
                                                                            }}
                                                                        >
                                                                            <FormControl>
                                                                                <Checkbox
                                                                                    checked={isChecked}
                                                                                    onCheckedChange={(checked) => {
                                                                                        return checked
                                                                                            ? field.onChange([...(field.value || []), service.id])
                                                                                            : field.onChange((field.value || []).filter((value: string) => value !== service.id));
                                                                                    }}
                                                                                    className="h-6 w-6 rounded-md border-2"
                                                                                />
                                                                            </FormControl>

                                                                            <div className="flex items-center gap-4 flex-1">
                                                                                <div className={`p-3 rounded-xl ${isChecked ? 'bg-[#00539F] text-white' : 'bg-gray-100 text-gray-500'}`}>
                                                                                    <Icon className="h-6 w-6" />
                                                                                </div>
                                                                                <div className="space-y-1">
                                                                                    <FormLabel className="text-base font-black text-gray-900 cursor-pointer">
                                                                                        {service.name_fr || service.name_en}
                                                                                    </FormLabel>
                                                                                    <p className="text-sm font-bold text-gray-400 uppercase tracking-tighter">
                                                                                        {service.category || 'Protection'}
                                                                                    </p>
                                                                                </div>
                                                                            </div>

                                                                            <div className="text-right">
                                                                                <div className="text-lg font-black text-[#00539F]">
                                                                                    +{formatCurrency(service.default_price || 0)}
                                                                                </div>
                                                                                <div className="text-[10px] font-bold text-gray-400 uppercase">per month</div>
                                                                            </div>
                                                                        </FormItem>
                                                                    )}
                                                                />
                                                            );
                                                        })}
                                                </div>

                                                {selectedPolicy.services.length > 4 && (
                                                    <Button
                                                        type="button"
                                                        variant="ghost"
                                                        className="w-full h-14 border-2 border-dashed border-gray-200 rounded-2xl text-gray-500 font-black uppercase tracking-widest hover:bg-gray-50"
                                                        onClick={() => setShowAllServices(!showAllServices)}
                                                    >
                                                        {showAllServices ? (
                                                            <><Minus className="mr-2 h-5 w-5" /> Show less features</>
                                                        ) : (
                                                            <><Plus className="mr-2 h-5 w-5" /> Add more features ({selectedPolicy.services.length - 4})</>
                                                        )}
                                                    </Button>
                                                )}
                                            </div>
                                        )}
                                    </form>
                                </FormProvider>
                            )}

                            {/* STEP 3: REVIEW & BREAKDOWN */}
                            {step === 3 && calculation && (
                                <div className="space-y-8 flex justify-center">
                                    <div className="w-full max-w-md">
                                        <UniversalEntityCard
                                            header={{
                                                title: selectedPolicy?.name || 'Quote',
                                                subtitle: 'Quote Summary',
                                                status: 'draft',
                                                icon: ShieldCheck,
                                                badgeText: `Duration: ${getValues('duration_months')} Months`
                                            }}
                                            items={selectedPolicy?.services?.filter(s => watch("selected_services")?.includes(s.id)).map(s => ({
                                                id: s.id,
                                                label: s.name_fr || s.name_en,
                                                price: s.default_price,
                                                checked: true,
                                                disabled: true
                                            })) || []}
                                            financials={[
                                                { label: 'Base Rate', amount: formatCurrency(calculation.base_premium) },
                                                { label: 'Risk Adjustment', amount: `+${formatCurrency(calculation.risk_adjustment || 0)}` },
                                                { label: 'Govt Tax (TVA)', amount: formatCurrency(calculation.tax_amount || 0) },
                                                { label: 'Company Admin Fee', amount: formatCurrency(calculation.arrangement_fee || 0) },
                                                { label: `Total / ${getValues('premium_frequency')}`, amount: formatCurrency(calculation.total_installment_price), isTotal: true }
                                            ]}
                                            footer={{
                                                validUntil: '30 Days from now',
                                                createdAt: 'Today'
                                            }}
                                        />
                                        <div className="text-[10px] text-gray-400 text-center font-bold uppercase tracking-widest px-12 mt-6">
                                            This quote is valid for 30 days. Final premium subject to full underwriting and documentation review.
                                        </div>
                                    </div>
                                </div>
                            )}

                        </div>
                    )}
                </div>

                <DialogFooter>
                    {step === 2 && (
                        <Button variant="outline" onClick={() => setStep(1)} className="mr-auto">Back</Button>
                    )}
                    {step === 3 && (
                        <Button variant="outline" onClick={() => setStep(2)} className="mr-auto">Back</Button>
                    )}

                    {step === 2 && (
                        <Button onClick={handleSubmit(onCalculate)} disabled={loading}>
                            {loading ? <Loader2 className="mr-2 h-4 w-4 animate-spin" /> : <Calculator className="mr-2 h-4 w-4" />}
                            Calculate Quote
                        </Button>
                    )}
                    {step === 3 && (
                        <Button onClick={onCreate} disabled={loading} className="bg-[#00539F] hover:bg-[#004380] text-white rounded-xl font-bold px-8">
                            {loading ? <Loader2 className="mr-2 h-4 w-4 animate-spin" /> : "Create Quote"}
                        </Button>
                    )}
                </DialogFooter>
            </DialogContent>

            {/* ERROR DIALOGS */}
            <AlertDialog open={noPolicyOpen} onOpenChange={setNoPolicyOpen}>
                <AlertDialogContent>
                    <AlertDialogHeader>
                        <AlertDialogTitle>No Eligible Policies</AlertDialogTitle>
                        <AlertDialogDescription>
                            {noPolicyMessage || "We currently have no premium policies available depending on your profile."}
                        </AlertDialogDescription>
                    </AlertDialogHeader>
                    <AlertDialogFooter>
                        <AlertDialogAction onClick={() => { setNoPolicyOpen(false); onOpenChange(false); }}>Close</AlertDialogAction>
                    </AlertDialogFooter>
                </AlertDialogContent>
            </AlertDialog>

            <AlertDialog open={missingInfoOpen} onOpenChange={setMissingInfoOpen}>
                <AlertDialogContent>
                    <AlertDialogHeader>
                        <AlertDialogTitle>Profile Incomplete</AlertDialogTitle>
                        <AlertDialogDescription>
                            To get a personalized quote, we need a bit more information:
                            <ul className="list-disc pl-5 mt-2 font-medium text-foreground">
                                {missingFields.map(field => (
                                    <li key={field}>{field}</li>
                                ))}
                            </ul>
                            Please update your profile in settings.
                        </AlertDialogDescription>
                    </AlertDialogHeader>
                    <AlertDialogFooter>
                        <AlertDialogAction onClick={() => { setMissingInfoOpen(false); onOpenChange(false); }}>Go to Profile</AlertDialogAction>
                    </AlertDialogFooter>
                </AlertDialogContent>
            </AlertDialog>
        </Dialog >
    );
}

