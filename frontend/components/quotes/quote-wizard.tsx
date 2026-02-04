"use client";

import { useState, useEffect, useMemo } from "react";
import { useRouter } from "next/navigation";
import { useForm, FormProvider } from "react-hook-form";
import { QuoteAPI } from "@/lib/api/quotes";
import { clientApi } from "@/lib/client-api";
import { QuoteCalculationResponse } from "@/types/quote";
import { PremiumPolicyType } from "@/lib/premium-policy-api";
import { RiskFactorForm } from "./risk-factor-form";
import { PremiumPolicyCard } from "./premium-policy-card";
import { quoteElementApi, QuoteElement } from "@/lib/quote-element-api";
import { policyServiceApi, PolicyService } from "@/lib/policy-service-api";
import { Checkbox } from "@/components/ui/checkbox";
import { RadioGroup, RadioGroupItem } from "@/components/ui/radio-group";
import { Label } from "@/components/ui/label";
import { Button } from "@/components/ui/button";
import { useLanguage } from "@/contexts/language-context";
import {
    Form,
    FormControl,
    FormDescription,
    FormField,
    FormItem,
    FormLabel,
    FormMessage
} from "@/components/ui/form";
import { Input } from "@/components/ui/input";
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select";
import { Card, CardContent, CardDescription, CardFooter, CardHeader, CardTitle } from "@/components/ui/card";
import { useToast } from "@/components/ui/use-toast";
import {
    Loader2,
    ArrowRight,
    ArrowLeft,
    Calculator,
    Save,
    Search,
    Check,
    AlertTriangle,
    ChevronRight,
    ShieldCheck,
    Car,
    User,
    Users,
    Info,
    PlusCircle,
    Clock,
    CreditCard,
    TrendingUp,
    Wallet,
    Percent,
    Settings,
    FileText,
    CheckCircle2
} from "lucide-react";
import { formatCurrency } from "@/lib/utils";
import {
    AlertDialog,
    AlertDialogAction,
    AlertDialogCancel,
    AlertDialogContent,
    AlertDialogDescription,
    AlertDialogFooter,
    AlertDialogHeader,
    AlertDialogTitle,
} from "@/components/ui/alert-dialog";
import { Badge } from "@/components/ui/badge";
import { ScrollArea } from "@/components/ui/scroll-area";
import { getCompanySettings } from "@/lib/settings-api";
import { CompanySettings } from "@/types/settings";

const FEATURES_MAP: Record<string, { en: string; fr: string; price: number }> = {
    "comprehensive": { en: "Comprehensive cover", fr: "Couverture tous risques", price: 0.00 },
    "small_courtesy": { en: "Small courtesy car", fr: "Véhicule de courtoisie (petit modèle)", price: 2.50 },
    "upgraded_courtesy": { en: "Upgraded courtesy car", fr: "Véhicule de courtoisie amélioré", price: 5.00 },
    "eu_cover": { en: "90-day comprehensive EU cover", fr: "Couverture tous risques dans l’UE pendant 90 jours", price: 3.00 },
    "windscreen": { en: "Windscreen cover", fr: "Garantie bris de glace", price: 1.50 },
    "uninsured_driver": { en: "Uninsured driver promise", fr: "Garantie conducteur non assuré", price: 2.00 },
    "loss_keys": { en: "Loss of keys", fr: "Perte de clés", price: 1.20 },
    "claims_portal": { en: "Claims portal access", fr: "Accès au portail de déclaration de sinistre", price: 0.00 },
    "personal_accident": { en: "Personal accident cover", fr: "Garantie individuelle accident", price: 4.00 },
    "personal_belongings": { en: "Personal belongings cover", fr: "Garantie effets personnels", price: 2.50 },
    "mfr_audio": { en: "Manufacturer-fitted audio equipment / sat nav", fr: "Équipement audio / GPS monté par le constructeur", price: 1.50 },
    "audio_equip": { en: "Audio equipment / sat nav", fr: "Équipement audio / GPS", price: 2.00 },
    "driving_other": { en: "Driving other cars (conditional)", fr: "Conduite d’autres véhicules (sous conditions)", price: 3.50 },
    "car_seats": { en: "Car seats cover", fr: "Garantie sièges auto", price: 1.80 },
    "theft_keys": { en: "Theft of keys", fr: "Vol de clés", price: 1.50 },
    "new_car_replace": { en: "New car replacement", fr: "Remplacement du véhicule neuf", price: 6.00 },
    "misfuelling": { en: "Misfuelling cover", fr: "Garantie erreur de carburant", price: 1.20 },
    "onward_travel": { en: "Onward travel", fr: "Garantie poursuite du voyage", price: 2.20 },
    "vandalism": { en: "Vandalism promise", fr: "Garantie vandalisme", price: 2.50 },
    "hotel_expenses": { en: "Hotel expenses", fr: "Frais d’hébergement", price: 1.50 }
};

// Types
interface WizardValues {
    client_id: string;
    vehicle_id: string;
    driver_ids: string[];
    policy_type_id: string; // ID of the PremiumPolicyType
    coverage_amount: number;
    duration_months: number;
    premium_frequency: string;
    risk_factors: Record<string, any>;
    discount_percent: number;
    created_by: string;
    ncd_protected: boolean;
    start_date: string;
    selected_services: string[];
    excess_details: {
        mandatory: number;
        voluntary: number;
        accidental_damage: number;
        fire_theft: number;
        theft_keys: number;
        replacement_locks: number;
    };
}

export function QuoteWizard() {
    const router = useRouter();
    const { toast } = useToast();
    const { t, language } = useLanguage();
    const [step, setStep] = useState(1);
    const [loading, setLoading] = useState(false);
    const [clients, setClients] = useState<any[]>([]);
    const [filteredClients, setFilteredClients] = useState<any[]>([]);
    const [clientSearch, setClientSearch] = useState("");

    // Policy Matching State
    const [eligiblePolicies, setEligiblePolicies] = useState<PremiumPolicyType[]>([]);
    const [recommendedPolicyId, setRecommendedPolicyId] = useState<string | null>(null);
    const [selectedPolicy, setSelectedPolicy] = useState<PremiumPolicyType | null>(null);
    const [companySettings, setCompanySettings] = useState<CompanySettings | null>(null);

    // Calculation State
    const [calculation, setCalculation] = useState<QuoteCalculationResponse | null>(null);

    // Error States
    const [missingInfoOpen, setMissingInfoOpen] = useState(false);
    const [missingFields, setMissingFields] = useState<string[]>([]);
    const [noPolicyOpen, setNoPolicyOpen] = useState(false);
    const [noPolicyMessage, setNoPolicyMessage] = useState("");

    // Configurable Elements State
    const [quoteElements, setQuoteElements] = useState<QuoteElement[]>([]);
    const [selectedBaseRateId, setSelectedBaseRateId] = useState<string | null>(null);
    const [selectedMultipliers, setSelectedMultipliers] = useState<string[]>([]);
    const [selectedFees, setSelectedFees] = useState<string[]>([]);
    const [selectedTaxes, setSelectedTaxes] = useState<string[]>([]);
    const [selectedDiscounts, setSelectedDiscounts] = useState<string[]>([]);

    // New Redesign States
    const [selectedClient, setSelectedClient] = useState<any | null>(null);
    const [clientVehicles, setClientVehicles] = useState<any[]>([]);
    const [clientDrivers, setClientDrivers] = useState<any[]>([]);
    const [showAllServices, setShowAllServices] = useState(false);
    const [allServices, setAllServices] = useState<PolicyService[]>([]);

    const methods = useForm<WizardValues>({
        defaultValues: {
            client_id: "",
            policy_type_id: "",
            vehicle_id: "",
            driver_ids: [],
            duration_months: 12,
            premium_frequency: "annual",
            discount_percent: 0,
            coverage_amount: 5000000,
            risk_factors: {},
            selected_services: [],
            ncd_protected: true,
            start_date: new Date().toISOString().split('T')[0],
            excess_details: {
                mandatory: 250,
                voluntary: 250,
                accidental_damage: 200,
                fire_theft: 200,
                theft_keys: 75,
                replacement_locks: 150
            }
        }
    });

    const { register, watch, setValue, handleSubmit, control, formState: { errors } } = methods;
    const clientId = watch("client_id");

    const wrapperFormatCurrency = (amount: number) => {
        const currency = companySettings?.currency || "GBP";
        const localeMap: Record<string, string> = {
            'en': 'en-GB',
            'fr': 'fr-FR',
            'es': 'es-ES'
        };
        const locale = localeMap[language] || 'en-GB';
        return formatCurrency(amount, currency, locale);
    };

    const handleCalculate = () => {
        onCalculate(methods.getValues());
    };

    // Load Clients on Mount
    useEffect(() => {
        async function loadClients() {
            try {
                const clientList = await clientApi.getClients({ limit: 100 });
                if (Array.isArray(clientList)) {
                    setClients(clientList);
                    setFilteredClients(clientList);
                }
            } catch (e) {
                toast({ title: "Error", description: "Failed to load clients", variant: "destructive" });
            }
        }
        async function loadElements() {
            try {
                const elements = await quoteElementApi.list({ active_only: true });
                setQuoteElements(elements);

                // Set Defaults
                const coverageOptions = elements.filter(e => e.category === 'coverage_amount');
                if (coverageOptions.length > 0) {
                    setValue("coverage_amount", parseFloat(coverageOptions[0].value.toString()));
                }

                const baseRateOptions = elements.filter(e => e.category === 'base_rate');
                if (baseRateOptions.length > 0) {
                    setSelectedBaseRateId(baseRateOptions[0].id);
                }

                // Default Risk Multipliers (optional - maybe don't auto select risks)
                // Default Taxes (optional - maybe auto select VAT?)
                const taxOptions = elements.filter(e => e.category === 'government_tax' && e.name.includes('VAT'));
                if (taxOptions.length > 0) {
                    setSelectedTaxes([taxOptions[0].id]);
                }
            } catch (e) {
                console.error("Failed to load quote elements", e);
            }
        }
        async function loadCompanySettings() {
            try {
                const settings = await getCompanySettings();
                setCompanySettings(settings);
            } catch (e) {
                console.error("Failed to load company settings", e);
            }
        }
        async function loadAllServices() {
            try {
                const services = await policyServiceApi.getAll();
                setAllServices(services);
            } catch (e) {
                console.error("Failed to load services", e);
            }
        }
        loadClients();
        loadElements();
        loadCompanySettings();
        loadAllServices();
        loadCompanySettings();
    }, [setValue]);

    // Filter Clients
    useEffect(() => {
        if (!clientSearch) {
            setFilteredClients(clients);
        } else {
            const lower = clientSearch.toLowerCase();
            setFilteredClients(clients.filter(c =>
                c.first_name?.toLowerCase().includes(lower) ||
                c.last_name?.toLowerCase().includes(lower) ||
                c.email?.toLowerCase().includes(lower)
            ));
        }
    }, [clientSearch, clients]);

    // Step 1 -> Step 2: Select Vehicle
    const handleClientSelect = async (selectedId: string) => {
        setLoading(true);
        setValue("client_id", selectedId);

        try {
            // Fetch client details
            const client = await clientApi.getClient(selectedId);
            setSelectedClient(client);

            // Fetch vehicles if any
            if (client.automobile_details && client.automobile_details.length > 0) {
                const vehicle = client.automobile_details[0];
                setClientVehicles([{
                    ...vehicle,
                    id: vehicle.id || 'v1',
                    make: vehicle.vehicle_make,
                    model: vehicle.vehicle_model,
                    registrationNumber: vehicle.vehicle_registration,
                    vehicleType: 'Manual', // Default
                    usage: vehicle.vehicle_usage || 'Domestic',
                    mileage: vehicle.vehicle_mileage?.toString() || '0',
                    imageUrl: 'https://images.unsplash.com/photo-1541899481282-d53bffe3c35d?auto=format&fit=crop&q=80&w=400' // Mock image
                }]);
            } else {
                setClientVehicles([]);
            }

            // Drivers - select current client as main driver by default
            setClientDrivers([{
                id: client.id,
                fullName: `${client.first_name} ${client.last_name}`,
                phoneNumber: client.phone || '',
                address: client.address || '',
                licenseNumber: client.driving_licence_number || '',
                photoUrl: client.profile_picture || `https://api.dicebear.com/7.x/avataaars/svg?seed=${client.first_name}`
            }]);

            setValue("driver_ids", [client.id]);

            // Policy matching
            const result = await QuoteAPI.matchPolicies(selectedId);
            if (result.status === "success") {
                setEligiblePolicies(result.data);
                setRecommendedPolicyId(result.recommended_id);
                setStep(2); // Move to Select Vehicle
            } else if (result.status === "no_policies") {
                setNoPolicyMessage(result.message);
                setNoPolicyOpen(true);
            } else if (result.status === "missing_info") {
                setMissingFields(result.missing_fields || []);
                setMissingInfoOpen(true);
            }
        } catch (e: any) {
            console.error("Error in handleClientSelect:", e);
            const detail = e.response?.data?.detail;
            toast({ title: "Error", description: detail?.message || "Failed to load client data", variant: "destructive" });
        } finally {
            setLoading(false);
        }
    };

    // Step 2 -> Step 3: Policy Selected
    const handlePolicySelect = (policy: PremiumPolicyType) => {
        setSelectedPolicy(policy);
        setValue("policy_type_id", policy.id);
        setStep(6);
    };

    // Calculate Premium
    const onCalculate = async (data: WizardValues) => {
        setLoading(true);

        let contextData = { ...data.risk_factors };
        const client = clients.find(c => c.id === data.client_id);
        if (client) {
            contextData = {
                ...contextData,
                ...client,
                age: client.age || 30 // Fallback
            };
        }

        try {
            const result = await QuoteAPI.calculate({
                client_id: data.client_id,
                policy_type_id: data.policy_type_id,
                coverage_amount: data.coverage_amount,
                premium_frequency: data.premium_frequency,
                duration_months: data.duration_months,
                risk_factors: contextData,
                selected_services: data.selected_services,
                financial_overrides: {
                    base_rate: selectedBaseRateId ? quoteElements.find(e => e.id === selectedBaseRateId)?.value : undefined,
                    risk_multiplier: selectedMultipliers.map(id => quoteElements.find(e => e.id === id)?.value).filter(Boolean),
                    fixed_fee: selectedFees.map(id => quoteElements.find(e => e.id === id)?.value).filter(Boolean),
                    company_discount: selectedDiscounts.map(id => quoteElements.find(e => e.id === id)?.value).filter(Boolean),
                    admin_discount_percent: data.discount_percent
                }
            });
            setCalculation(result);
        } catch (e) {
            toast({ title: "Calculation Failed", description: "Could not calculate premium.", variant: "destructive" });
        } finally {
            setLoading(false);
        }
    };

    // Auto-Calculate Effect
    const coverage = watch("coverage_amount");
    const duration = watch("duration_months");
    const frequency = watch("premium_frequency");

    useEffect(() => {
        if ((step === 3 || step === 4 || step === 8) && selectedPolicy) {
            // Debounce slightly to avoid rapid-fire API calls during typing
            const timer = setTimeout(() => {
                const data = methods.getValues();
                onCalculate(data);
            }, 500);
            return () => clearTimeout(timer);
        }
    }, [
        step,
        selectedPolicy,
        selectedBaseRateId,
        selectedMultipliers,
        selectedFees,
        selectedTaxes,
        selectedDiscounts,
        coverage,
        duration,
        frequency,
        watch("discount_percent")
    ]);

    const onCreate = async (status: 'draft' | 'sent', e?: React.MouseEvent) => {
        if (e) {
            e.preventDefault();
            e.stopPropagation();
        }
        if (!calculation || !selectedPolicy) return;
        setLoading(true);
        try {
            console.log("Submitting quote creation...");
            const data = methods.getValues();


            // Construct a clean payload matching QuoteCreate schema
            // Explicitly excluding 'risk_factors' property which is not in QuoteCreate
            const payload: any = {
                client_id: data.client_id,
                policy_type_id: selectedPolicy.id,
                coverage_amount: data.coverage_amount,
                premium_frequency: data.premium_frequency,
                duration_months: data.duration_months,
                discount_percent: data.discount_percent || 0,
                excess: (data.excess_details?.mandatory || 0) + (data.excess_details?.voluntary || 0),
                included_services: data.selected_services || [],
                details: {
                    ...data.risk_factors,
                    excess_details: data.excess_details,
                    final_premium: calculation.final_premium,
                    ncd_protected: data.ncd_protected,
                    start_date: data.start_date,
                    vehicle_id: data.vehicle_id,
                    driver_ids: data.driver_ids
                },
                financial_overrides: {
                    base_rate: selectedBaseRateId ? quoteElements.find(e => e.id === selectedBaseRateId)?.value ?? null : null,
                    risk_multiplier: selectedMultipliers.map(id => quoteElements.find(e => e.id === id)?.value).filter(v => v !== undefined && v !== null),
                    fixed_fee: selectedFees.map(id => quoteElements.find(e => e.id === id)?.value).filter(v => v !== undefined && v !== null),
                    // government_tax: selectedTaxes.map(id => quoteElements.find(e => e.id === id)?.value).filter(v => v !== undefined && v !== null), // REMOVED to enforce company settings
                    company_discount: selectedDiscounts.map(id => quoteElements.find(e => e.id === id)?.value).filter(v => v !== undefined && v !== null)
                }
            };

            // Only add created_by if it exists (though backend handles optional)
            // if (data.created_by) payload.created_by = data.created_by;
            console.log("Payload:", payload);

            await QuoteAPI.create(payload);

            toast({ title: "Success", description: `Quote ${status === 'draft' ? 'saved' : 'created'} successfully` });
            router.push('/dashboard/quotes');
            // router.refresh(); // Removed to prevent potential race/reload issues
        } catch (e: any) {
            console.error("Quote Creation Error:", e);
            toast({ title: "Error", description: e.message || "Failed to create quote", variant: "destructive" });
        } finally {
            setLoading(false);
        }
    };

    const calculatedValues = useMemo(() => {
        if (!calculation) return null;

        return {
            base: calculation.base_premium,
            totalRisk: calculation.risk_adjustment,
            totalFees: calculation.extra_fee,
            totalDiscount: calculation.discount_amount,
            subtotal: calculation.final_premium - calculation.tax_amount,
            totalTax: calculation.tax_amount,
            adminFee: calculation.admin_fee,
            finalPremium: calculation.final_premium
        };
    }, [calculation]);

    return (
        <Card className="w-full max-w-5xl mx-auto min-h-[700px] flex flex-col border-none shadow-2xl rounded-[40px] overflow-hidden">
            <CardHeader className="bg-slate-50 border-b p-8">
                <div className="flex justify-between items-center mb-6">
                    <div>
                        <CardTitle className="text-3xl font-black text-slate-900">
                            {step === 1 && t('quote.wizard.select_client_title')}
                            {step === 2 && "Select Vehicle"}
                            {step === 3 && "Add Drivers"}
                            {step === 4 && "Policy Preferences"}
                            {step === 5 && "Choose Coverage"}
                            {step === 6 && "Optional Extras"}
                            {step === 7 && "Excess Breakdown"}
                            {step === 8 && "Final Review"}
                        </CardTitle>
                        <CardDescription className="text-lg font-medium text-slate-500 mt-1">
                            {step === 1 && t('quote.wizard.select_client_desc')}
                            {step === 2 && "Choose the vehicle to be insured."}
                            {step === 3 && "Manage main and additional drivers."}
                            {step === 4 && "Configure NCD, start date and frequency."}
                            {step === 5 && "Compare and select the best policy."}
                            {step === 6 && "Enhance the policy with extra services."}
                            {step === 7 && "Review detailed excess information."}
                            {step === 8 && "Final premium breakdown and confirmation."}
                        </CardDescription>
                    </div>
                    <div className="flex items-center gap-2">
                        <Badge className="bg-[#00539F] text-white px-4 py-1.5 rounded-full font-bold text-sm">
                            Step {step} of 8
                        </Badge>
                    </div>
                </div>

                {/* Step Indicator */}
                <div className="flex items-center gap-2 overflow-x-auto pb-2 no-scrollbar">
                    {[1, 2, 3, 4, 5, 6, 7, 8].map((s) => (
                        <div key={s} className="flex items-center gap-2 flex-shrink-0">
                            <div className={`h-2.5 w-12 rounded-full transition-all duration-500 ${step >= s ? 'bg-[#00539F]' : 'bg-slate-200'}`} />
                            {s < 8 && <ChevronRight className="h-4 w-4 text-slate-300" />}
                        </div>
                    ))}
                </div>
            </CardHeader>
            <CardContent className="flex-1">
                <FormProvider {...methods}>
                    <form className="space-y-6 h-full flex flex-col">

                        {/* STEP 1: CLIENT SELECTION */}
                        {step === 1 && (
                            <div className="space-y-6 animate-in fade-in duration-500">
                                <div className="space-y-2">
                                    <Label className="text-sm font-black uppercase tracking-widest text-[#00539F]">{t('quote.wizard.find_client')}</Label>
                                    <div className="relative group">
                                        <Search className="absolute left-4 top-1/2 -translate-y-1/2 h-5 w-5 text-slate-400 group-focus-within:text-[#00539F] transition-colors" />
                                        <Input
                                            placeholder={t('quote.wizard.search_client_placeholder')}
                                            className="pl-12 h-14 rounded-2xl border-slate-200 focus:ring-[#00539F]/20 text-lg shadow-sm"
                                            value={clientSearch}
                                            onChange={(e) => setClientSearch(e.target.value)}
                                        />
                                    </div>
                                </div>

                                <ScrollArea className="h-[450px] pr-4">
                                    {filteredClients.length === 0 ? (
                                        <div className="flex flex-col items-center justify-center py-20 text-slate-400 bg-slate-50 rounded-[30px] border border-dashed border-slate-200">
                                            <Users className="h-12 w-12 mb-4 opacity-20" />
                                            <p className="font-bold text-lg">{t('quote.wizard.no_clients')}</p>
                                        </div>
                                    ) : (
                                        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                                            {filteredClients.map(client => (
                                                <div
                                                    key={client.id}
                                                    onClick={() => handleClientSelect(client.id)}
                                                    className="group flex flex-col gap-4 p-6 rounded-[30px] border-2 border-slate-100 hover:border-[#00539F] hover:bg-blue-50/50 cursor-pointer transition-all duration-300 shadow-sm hover:shadow-md relative overflow-hidden bg-white"
                                                >
                                                    <div className="flex items-center gap-4">
                                                        <div className="h-14 w-14 rounded-2xl bg-slate-100 flex items-center justify-center font-black text-slate-400 group-hover:bg-[#00539F] group-hover:text-white transition-all text-xl">
                                                            {client.first_name?.[0] || client.business_name?.[0] || "?"}
                                                        </div>
                                                        <div className="flex-1 min-w-0">
                                                            <div className="font-black text-slate-900 group-hover:text-[#00539F] transition-colors truncate text-lg">
                                                                {client.first_name} {client.last_name}
                                                            </div>
                                                            <div className="text-sm font-medium text-slate-500 truncate">{client.email}</div>
                                                        </div>
                                                        <ChevronRight className="h-6 w-6 text-slate-300 group-hover:text-[#00539F] group-hover:translate-x-1 transition-all" />
                                                    </div>
                                                </div>
                                            ))}
                                        </div>
                                    )}
                                </ScrollArea>
                            </div>
                        )}

                        {/* STEP 2: VEHICLE SELECTION */}
                        {step === 2 && selectedClient && (
                            <div className="space-y-8 animate-in fade-in slide-in-from-bottom-4 duration-500">
                                <div className="flex items-center justify-between">
                                    <h3 className="text-2xl font-black text-slate-900">Select Vehicle</h3>
                                    <Button type="button" variant="outline" className="rounded-xl border-slate-200 font-bold" onClick={() => setStep(1)}>Change Client</Button>
                                </div>

                                {clientVehicles.length === 0 ? (
                                    <Card className="rounded-[40px] p-12 text-center border-dashed border-2 border-slate-200 bg-slate-50/50">
                                        <Car className="h-16 w-16 mx-auto text-slate-300 mb-6" />
                                        <h3 className="text-xl font-black text-gray-900 mb-2">No vehicles found</h3>
                                        <p className="text-slate-500 font-medium mb-8">This client doesn't have any vehicles registered. Please add one in their profile first.</p>
                                        <Button type="button" className="bg-[#00539F] text-white rounded-2xl px-8 h-12 font-bold shadow-lg" onClick={() => window.open(`/dashboard/clients/${selectedClient.id}`, '_blank')}>
                                            Go to Client Profile
                                        </Button>
                                    </Card>
                                ) : (
                                    <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                                        {clientVehicles.map((vehicle) => (
                                            <div
                                                key={vehicle.id}
                                                onClick={() => {
                                                    setValue("vehicle_id", vehicle.id);
                                                    setStep(3);
                                                }}
                                                className={`group relative rounded-[40px] overflow-hidden border-2 transition-all p-6 cursor-pointer bg-white ${watch("vehicle_id") === vehicle.id ? 'border-[#00539F] shadow-xl bg-blue-50/20' : 'border-slate-100 hover:border-slate-200 shadow-md'}`}
                                            >
                                                <div className="flex gap-6">
                                                    <div className="h-32 w-44 rounded-[30px] overflow-hidden bg-slate-100 flex-shrink-0">
                                                        <img src={vehicle.imageUrl} className="w-full h-full object-cover group-hover:scale-110 transition-transform duration-500" alt={vehicle.make} />
                                                    </div>
                                                    <div className="flex-1 flex flex-col justify-between py-2">
                                                        <div>
                                                            <h4 className="text-xl font-black text-slate-900">{vehicle.make} {vehicle.model}</h4>
                                                            <div className="flex items-center gap-2 mt-2">
                                                                <Badge className="bg-slate-100 text-slate-600 border-none font-black text-[10px] tracking-widest px-3">{vehicle.registrationNumber}</Badge>
                                                                <span className="text-slate-300 text-xs font-bold">•</span>
                                                                <span className="text-slate-500 text-xs font-bold font-mono">{vehicle.vehicleType}</span>
                                                            </div>
                                                        </div>
                                                        <div className="flex items-center gap-1.5 text-[#00539F] font-black text-sm">
                                                            Select this vehicle <ChevronRight className="h-4 w-4" />
                                                        </div>
                                                    </div>
                                                </div>
                                            </div>
                                        ))}
                                    </div>
                                )}
                            </div>
                        )}

                        {/* STEP 3: ADD DRIVERS */}
                        {step === 3 && selectedClient && (
                            <div className="space-y-8 animate-in fade-in slide-in-from-bottom-4 duration-500">
                                <div className="flex items-center justify-between">
                                    <h3 className="text-2xl font-black text-slate-900">Manage Drivers</h3>
                                    <p className="text-slate-500 font-bold">Select the main driver and any additional named drivers.</p>
                                </div>

                                <div className="space-y-6">
                                    <div className="space-y-4">
                                        <Label className="text-xs font-black uppercase tracking-widest text-slate-400">Default Drivers</Label>
                                        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                                            {clientDrivers.map((driver) => {
                                                const isSelected = watch("driver_ids")?.includes(driver.id);
                                                return (
                                                    <div
                                                        key={driver.id}
                                                        onClick={() => {
                                                            const current = watch("driver_ids") || [];
                                                            if (current.includes(driver.id)) {
                                                                if (current.length > 1) {
                                                                    setValue("driver_ids", current.filter(id => id !== driver.id));
                                                                }
                                                            } else {
                                                                setValue("driver_ids", [...current, driver.id]);
                                                            }
                                                        }}
                                                        className={`p-6 rounded-[30px] border-2 cursor-pointer transition-all flex items-center justify-between bg-white ${isSelected ? 'border-[#00539F] bg-blue-50/50 shadow-lg scale-[1.02]' : 'border-slate-100 hover:border-slate-200'}`}
                                                    >
                                                        <div className="flex items-center gap-4">
                                                            <div className="h-14 w-14 rounded-2xl overflow-hidden bg-slate-100 border-2 border-white shadow-sm">
                                                                <img src={driver.photoUrl} alt={driver.fullName} className="w-full h-full object-cover" />
                                                            </div>
                                                            <div>
                                                                <span className="font-black text-slate-900 block">{driver.fullName}</span>
                                                                <span className="text-xs font-bold text-slate-400 uppercase tracking-wider">{driver.licenseNumber}</span>
                                                            </div>
                                                        </div>
                                                        {isSelected && <Check className="h-6 w-6 text-[#00539F]" />}
                                                    </div>
                                                );
                                            })}
                                        </div>
                                    </div>

                                    <div className="p-8 border-2 border-dashed border-slate-100 rounded-[40px] text-center bg-slate-50/30">
                                        <Users className="h-10 w-10 mx-auto text-slate-300 mb-2" />
                                        <p className="text-slate-400 font-bold uppercase text-xs tracking-widest">Additional drivers can be added via Client profile</p>
                                    </div>

                                    <Button type="button" onClick={() => setStep(4)} className="w-full bg-[#00539F] hover:bg-[#004380] text-white rounded-[20px] h-16 text-xl font-black shadow-xl scale-100 active:scale-95 transition-all">
                                        Next Component: Policy Details <ChevronRight className="ml-2 h-6 w-6" />
                                    </Button>
                                    <Button type="button" onClick={() => setStep(2)} variant="link" className="w-full text-slate-400 font-bold uppercase tracking-widest text-xs h-8">Go Back</Button>
                                </div>
                            </div>
                        )}

                        {/* STEP 4: POLICY PREFERENCES */}
                        {step === 4 && (
                            <div className="space-y-10 animate-in fade-in slide-in-from-bottom-4 duration-500">
                                <div className="flex items-center justify-between">
                                    <h3 className="text-2xl font-black text-slate-900">Policy Preferences</h3>
                                    <Badge className="bg-blue-50 text-[#00539F] border-none px-4 py-1.5 rounded-full font-bold">Auto-matching step</Badge>
                                </div>

                                <div className="grid grid-cols-1 md:grid-cols-2 gap-8">
                                    <Card className="p-10 rounded-[40px] border-none bg-blue-50/50 space-y-8 shadow-inner">
                                        <div className="space-y-6">
                                            <div className="flex items-center gap-4">
                                                <div className="h-12 w-12 bg-white rounded-2xl flex items-center justify-center flex-shrink-0 shadow-md">
                                                    <ShieldCheck className="h-6 w-6 text-[#00539F]" />
                                                </div>
                                                <div>
                                                    <Label className="text-lg font-black text-slate-900">No Claims Discount</Label>
                                                    <p className="text-xs font-bold text-slate-400 uppercase tracking-widest">Protection status</p>
                                                </div>
                                            </div>

                                            <div className="grid grid-cols-2 gap-3">
                                                <button
                                                    type="button"
                                                    onClick={() => setValue("ncd_protected", true)}
                                                    className={`h-16 rounded-2xl font-black transition-all ${watch("ncd_protected") ? 'bg-[#00539F] text-white shadow-lg scale-105' : 'bg-white text-slate-400 border-2 border-slate-100'}`}
                                                >
                                                    Protected
                                                </button>
                                                <button
                                                    type="button"
                                                    onClick={() => setValue("ncd_protected", false)}
                                                    className={`h-16 rounded-2xl font-black transition-all ${!watch("ncd_protected") ? 'bg-[#00539F] text-white shadow-lg scale-105' : 'bg-white text-slate-400 border-2 border-slate-100'}`}
                                                >
                                                    Unprotected
                                                </button>
                                            </div>
                                        </div>

                                        <div className="space-y-6 pt-4 border-t border-[#00539F]/10">
                                            <div className="flex items-center gap-4">
                                                <div className="h-12 w-12 bg-white rounded-2xl flex items-center justify-center flex-shrink-0 shadow-md">
                                                    <CreditCard className="h-6 w-6 text-[#00539F]" />
                                                </div>
                                                <div>
                                                    <Label className="text-lg font-black text-slate-900">Payment Frequency</Label>
                                                    <p className="text-xs font-bold text-slate-400 uppercase tracking-widest">Billing cycle</p>
                                                </div>
                                            </div>

                                            <div className="grid grid-cols-2 gap-3">
                                                {['annual', 'monthly'].map((freq) => (
                                                    <button
                                                        key={freq}
                                                        type="button"
                                                        onClick={() => setValue("premium_frequency", freq)}
                                                        className={`h-16 rounded-2xl font-black capitalize transition-all ${watch("premium_frequency") === freq ? 'bg-[#00539F] text-white shadow-lg scale-105' : 'bg-white text-slate-400 border-2 border-slate-100'}`}
                                                    >
                                                        {freq}
                                                    </button>
                                                ))}
                                            </div>
                                        </div>
                                    </Card>

                                    <div className="space-y-8">
                                        <div className="p-10 rounded-[40px] border-2 border-slate-100 bg-white space-y-6 shadow-sm">
                                            <div className="flex items-center gap-4">
                                                <div className="h-12 w-12 bg-slate-100 rounded-2xl flex items-center justify-center flex-shrink-0">
                                                    <Clock className="h-6 w-6 text-[#00539F]" />
                                                </div>
                                                <div>
                                                    <Label className="text-lg font-black text-slate-900">Policy Start Date</Label>
                                                    <p className="text-xs font-bold text-slate-400 uppercase tracking-widest">Activation timing</p>
                                                </div>
                                            </div>

                                            <FormField
                                                control={control}
                                                name="start_date"
                                                render={({ field }) => (
                                                    <Input
                                                        type="date"
                                                        {...field}
                                                        className="h-16 rounded-2xl border-2 border-slate-100 text-lg font-bold px-6 focus:border-[#00539F] transition-all bg-slate-50/50"
                                                    />
                                                )}
                                            />

                                            <div className="bg-yellow-50 p-6 rounded-[25px] border-2 border-yellow-100 flex gap-4">
                                                <AlertTriangle className="h-6 w-6 text-yellow-500 flex-shrink-0 mt-1" />
                                                <p className="text-sm font-bold text-yellow-700">Insurance cannot be backdated. The start date must be today or in the future.</p>
                                            </div>
                                        </div>

                                        <Button type="button" onClick={() => setStep(5)} className="w-full bg-[#00539F] hover:bg-[#004380] text-white rounded-[30px] h-20 text-2xl font-black shadow-2xl hover:translate-y-[-4px] transition-all active:translate-y-0">
                                            Find Eligible Policies <ChevronRight className="ml-2 h-8 w-8" />
                                        </Button>
                                    </div>
                                </div>
                            </div>
                        )}

                        {/* STEP 5: SELECT POLICY */}
                        {step === 5 && (
                            <div className="space-y-8 animate-in fade-in slide-in-from-bottom-4 duration-500">
                                <div className="flex items-center justify-between">
                                    <h3 className="text-2xl font-black text-slate-900">Recommended Policies</h3>
                                    <p className="text-sm font-bold text-slate-400">Based on your client profile and preferences.</p>
                                </div>

                                <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
                                    {eligiblePolicies.map(policy => (
                                        <div
                                            key={policy.id}
                                            onClick={() => handlePolicySelect(policy)}
                                            className={`relative p-8 rounded-[40px] border-2 transition-all cursor-pointer group hover:shadow-2xl ${selectedPolicy?.id === policy.id ? 'border-[#00539F] bg-blue-50/50 shadow-xl scale-[1.02]' : 'border-slate-100 bg-white shadow-md'}`}
                                        >
                                            <div className="flex flex-col h-full space-y-6">
                                                <div className="flex justify-between items-start">
                                                    <div className="h-14 w-14 rounded-2xl bg-blue-100 flex items-center justify-center">
                                                        <ShieldCheck className="h-8 w-8 text-[#00539F]" />
                                                    </div>
                                                    {policy.id === recommendedPolicyId && (
                                                        <Badge className="bg-[#00539F] text-white px-4 py-1.5 rounded-full font-black text-[10px] tracking-widest">RECOMMENDED</Badge>
                                                    )}
                                                </div>

                                                <div>
                                                    <h4 className="text-xl font-black text-slate-900 leading-tight">{policy.name}</h4>
                                                    <p className="text-sm font-medium text-slate-500 mt-2 line-clamp-2">{policy.description}</p>
                                                </div>

                                                <div className="pt-4 border-t border-slate-100 flex items-center justify-between mt-auto">
                                                    <span className="text-xs font-black text-slate-400 uppercase tracking-widest">Select Plan</span>
                                                    <ChevronRight className="h-6 w-6 text-[#00539F] group-hover:translate-x-1 transition-transform" />
                                                </div>
                                            </div>
                                        </div>
                                    ))}
                                </div>
                            </div>
                        )}

                        {/* STEP 6: OPTIONAL SERVICES */}
                        {step === 6 && selectedPolicy && (
                            <div className="space-y-8 animate-in fade-in slide-in-from-bottom-4 duration-500">
                                <div className="flex items-center justify-between">
                                    <h3 className="text-2xl font-black text-slate-900">Optional Extra Services</h3>
                                    <Badge variant="outline" className="border-slate-200 text-slate-500 font-bold px-4 py-1.5 rounded-full">
                                        Customize Coverage
                                    </Badge>
                                </div>

                                <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
                                    {allServices.length > 0 ? (
                                        allServices.map(service => {
                                            const isIncluded = selectedPolicy.services?.some((s: any) => s.id === service.id);
                                            const isSelected = watch("selected_services")?.includes(service.id);

                                            return (
                                                <div
                                                    key={service.id}
                                                    onClick={() => !isIncluded && (
                                                        isSelected
                                                            ? setValue("selected_services", (watch("selected_services") || []).filter((id: string) => id !== service.id))
                                                            : setValue("selected_services", [...(watch("selected_services") || []), service.id])
                                                    )}
                                                    className={`relative p-8 rounded-[40px] border-2 transition-all cursor-pointer group hover:shadow-2xl ${isSelected || isIncluded ? 'border-[#00539F] bg-blue-50/50 shadow-xl scale-[1.02]' : 'border-slate-100 bg-white shadow-md'}`}
                                                >
                                                    <div className="flex flex-col h-full space-y-4">
                                                        <div className="flex justify-between items-start">
                                                            <div className={`h-14 w-14 rounded-2xl flex items-center justify-center ${isSelected || isIncluded ? 'bg-blue-100' : 'bg-slate-100'}`}>
                                                                <CheckCircle2 className={`h-8 w-8 ${isSelected || isIncluded ? 'text-[#00539F]' : 'text-slate-400'}`} />
                                                            </div>
                                                            {isIncluded ? (
                                                                <Badge className="bg-emerald-500 text-white px-3 py-1 rounded-full font-black text-[10px] tracking-widest border-none">INCLUDED</Badge>
                                                            ) : (
                                                                <span className="text-lg font-black text-[#00539F]">+{wrapperFormatCurrency(service.default_price)}</span>
                                                            )}
                                                        </div>
                                                        <div>
                                                            <h4 className="text-lg font-black text-slate-900 leading-tight">{language === 'fr' ? service.name_fr || service.name_en : service.name_en}</h4>
                                                            <p className="text-xs font-bold text-slate-400 uppercase tracking-widest mt-1 tracking-wider">{service.category || 'Maintenance'}</p>
                                                        </div>
                                                    </div>
                                                </div>
                                            );
                                        })
                                    ) : (
                                        <div className="col-span-full py-20 text-center bg-slate-50 rounded-[40px] border-2 border-dashed border-slate-200">
                                            <div className="h-20 w-20 bg-white rounded-3xl flex items-center justify-center mx-auto mb-6 shadow-xl">
                                                <PlusCircle className="h-10 w-10 text-slate-300" />
                                            </div>
                                            <h4 className="text-xl font-black text-slate-900 uppercase tracking-widest">No Extra Services Available</h4>
                                            <p className="text-slate-400 font-bold mt-2">No additional services could be loaded at this time.</p>
                                        </div>
                                    )}
                                </div>

                                <div className="pt-8 border-t border-slate-100 flex gap-4">
                                    <Button type="button" onClick={() => setStep(7)} className="flex-1 bg-[#00539F] hover:bg-[#004380] text-white rounded-[25px] h-16 text-xl font-black shadow-xl">
                                        Next: Excess Breakdown <ChevronRight className="ml-2 h-6 w-6" />
                                    </Button>
                                    <Button type="button" variant="outline" onClick={() => setStep(5)} className="px-10 rounded-[25px] border-slate-200 font-black h-16 text-slate-400">
                                        Change Policy
                                    </Button>
                                </div>
                            </div>
                        )}
                        {/* STEP 7: EXCESS BREAKDOWN */}
                        {step === 7 && (
                            <div className="space-y-10 animate-in fade-in slide-in-from-bottom-4 duration-500">
                                <div className="flex items-center justify-between">
                                    <h3 className="text-2xl font-black text-slate-900">Detailed Excess Breakdown</h3>
                                    <Badge className="bg-orange-50 text-orange-600 border-none px-4 py-1.5 rounded-full font-black text-[10px] tracking-widest uppercase">Required Info</Badge>
                                </div>

                                <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
                                    {/* Compulsory / Mandatory */}
                                    <div className="p-8 rounded-[40px] border-2 border-slate-100 bg-white space-y-4 shadow-sm">
                                        <div className="flex items-center gap-3">
                                            <div className="h-10 w-10 bg-slate-100 rounded-xl flex items-center justify-center">
                                                <ShieldCheck className="h-5 w-5 text-[#00539F]" />
                                            </div>
                                            <Label className="text-sm font-black text-slate-900 uppercase tracking-widest">Compulsory Excess</Label>
                                        </div>
                                        <div className="relative">
                                            <div className="absolute left-4 top-1/2 -translate-y-1/2 font-black text-slate-400">$</div>
                                            <Input
                                                type="number"
                                                className="h-14 pl-10 rounded-2xl border-slate-100 font-bold focus:border-[#00539F] bg-slate-50/50"
                                                value={watch("excess_details")?.mandatory}
                                                onChange={(e) => {
                                                    const current = watch("excess_details");
                                                    setValue("excess_details", { ...current, mandatory: parseFloat(e.target.value) || 0 });
                                                }}
                                            />
                                        </div>
                                    </div>

                                    {/* Voluntary */}
                                    <div className="p-8 rounded-[40px] border-2 border-slate-100 bg-white space-y-4 shadow-sm">
                                        <div className="flex items-center gap-3">
                                            <div className="h-10 w-10 bg-slate-100 rounded-xl flex items-center justify-center">
                                                <PlusCircle className="h-5 w-5 text-[#00539F]" />
                                            </div>
                                            <Label className="text-sm font-black text-slate-900 uppercase tracking-widest">Voluntary Excess</Label>
                                        </div>
                                        <div className="relative">
                                            <div className="absolute left-4 top-1/2 -translate-y-1/2 font-black text-slate-400">$</div>
                                            <Input
                                                type="number"
                                                className="h-14 pl-10 rounded-2xl border-slate-100 font-bold focus:border-[#00539F] bg-slate-50/50"
                                                value={watch("excess_details")?.voluntary}
                                                onChange={(e) => {
                                                    const current = watch("excess_details");
                                                    setValue("excess_details", { ...current, voluntary: parseFloat(e.target.value) || 0 });
                                                }}
                                            />
                                        </div>
                                    </div>

                                    {/* Accidental Damage */}
                                    <div className="p-8 rounded-[40px] border-2 border-slate-100 bg-white space-y-4 shadow-sm">
                                        <div className="flex items-center gap-3">
                                            <div className="h-10 w-10 bg-slate-100 rounded-xl flex items-center justify-center">
                                                <Car className="h-5 w-5 text-red-500" />
                                            </div>
                                            <Label className="text-sm font-black text-slate-900 uppercase tracking-widest">Accidental Damage</Label>
                                        </div>
                                        <div className="relative">
                                            <div className="absolute left-4 top-1/2 -translate-y-1/2 font-black text-slate-400">$</div>
                                            <Input
                                                type="number"
                                                className="h-14 pl-10 rounded-2xl border-slate-100 font-bold focus:border-[#00539F] bg-slate-50/50"
                                                value={watch("excess_details")?.accidental_damage}
                                                onChange={(e) => {
                                                    const current = watch("excess_details");
                                                    setValue("excess_details", { ...current, accidental_damage: parseFloat(e.target.value) || 0 });
                                                }}
                                            />
                                        </div>
                                    </div>

                                    {/* Fire & Theft */}
                                    <div className="p-8 rounded-[40px] border-2 border-slate-100 bg-white space-y-4 shadow-sm">
                                        <div className="flex items-center gap-3">
                                            <div className="h-10 w-10 bg-slate-100 rounded-xl flex items-center justify-center">
                                                <TrendingUp className="h-5 w-5 text-orange-500" />
                                            </div>
                                            <Label className="text-sm font-black text-slate-900 uppercase tracking-widest">Fire & Theft</Label>
                                        </div>
                                        <div className="relative">
                                            <div className="absolute left-4 top-1/2 -translate-y-1/2 font-black text-slate-400">$</div>
                                            <Input
                                                type="number"
                                                className="h-14 pl-10 rounded-2xl border-slate-100 font-bold focus:border-[#00539F] bg-slate-50/50"
                                                value={watch("excess_details")?.fire_theft}
                                                onChange={(e) => {
                                                    const current = watch("excess_details");
                                                    setValue("excess_details", { ...current, fire_theft: parseFloat(e.target.value) || 0 });
                                                }}
                                            />
                                        </div>
                                    </div>

                                    {/* Theft of Keys */}
                                    <div className="p-8 rounded-[40px] border-2 border-slate-100 bg-white space-y-4 shadow-sm">
                                        <div className="flex items-center gap-3">
                                            <div className="h-10 w-10 bg-slate-100 rounded-xl flex items-center justify-center">
                                                <FileText className="h-5 w-5 text-purple-500" />
                                            </div>
                                            <Label className="text-sm font-black text-slate-900 uppercase tracking-widest">Theft of Keys</Label>
                                        </div>
                                        <div className="relative">
                                            <div className="absolute left-4 top-1/2 -translate-y-1/2 font-black text-slate-400">$</div>
                                            <Input
                                                type="number"
                                                className="h-14 pl-10 rounded-2xl border-slate-100 font-bold focus:border-[#00539F] bg-slate-50/50"
                                                value={watch("excess_details")?.theft_keys}
                                                onChange={(e) => {
                                                    const current = watch("excess_details");
                                                    setValue("excess_details", { ...current, theft_keys: parseFloat(e.target.value) || 0 });
                                                }}
                                            />
                                        </div>
                                    </div>

                                    {/* Replacement Locks */}
                                    <div className="p-8 rounded-[40px] border-2 border-slate-100 bg-white space-y-4 shadow-sm">
                                        <div className="flex items-center gap-3">
                                            <div className="h-10 w-10 bg-slate-100 rounded-xl flex items-center justify-center">
                                                <FileText className="h-5 w-5 text-blue-500" />
                                            </div>
                                            <Label className="text-sm font-black text-slate-900 uppercase tracking-widest">Replacement Locks</Label>
                                        </div>
                                        <div className="relative">
                                            <div className="absolute left-4 top-1/2 -translate-y-1/2 font-black text-slate-400">$</div>
                                            <Input
                                                type="number"
                                                className="h-14 pl-10 rounded-2xl border-slate-100 font-bold focus:border-[#00539F] bg-slate-50/50"
                                                value={watch("excess_details")?.replacement_locks}
                                                onChange={(e) => {
                                                    const current = watch("excess_details");
                                                    setValue("excess_details", { ...current, replacement_locks: parseFloat(e.target.value) || 0 });
                                                }}
                                            />
                                        </div>
                                    </div>
                                </div>

                                <Card className="p-10 rounded-[40px] border-none bg-blue-50/50 flex flex-col items-center gap-6 shadow-inner">
                                    <div className="text-center">
                                        <h4 className="text-xl font-black text-slate-900 uppercase tracking-widest">Total Policy Excess</h4>
                                        <div className="text-6xl font-black text-[#00539F] mt-2">
                                            {formatCurrency((watch("excess_details")?.mandatory || 0) + (watch("excess_details")?.voluntary || 0))}
                                        </div>
                                        <p className="text-sm font-bold text-slate-400 mt-4 max-w-md mx-auto">
                                            This is the total amount payable by the client across mandatory and voluntary contributions in the event of a standard claim.
                                        </p>
                                    </div>
                                    <Button type="button" onClick={() => setStep(8)} className="w-full max-w-md bg-[#00539F] hover:bg-[#004380] text-white rounded-[25px] h-16 text-xl font-black shadow-xl">
                                        Confirm & Go to Review <ChevronRight className="ml-2 h-6 w-6" />
                                    </Button>
                                </Card>
                            </div>
                        )}

                        {/* STEP 8: FINAL CALCULATION & REVIEW */}
                        {step === 8 && selectedPolicy && (
                            <div className="space-y-10 animate-in fade-in slide-in-from-bottom-4 duration-500">
                                <div className="flex items-center justify-between">
                                    <h3 className="text-2xl font-black text-slate-900">Quote Finalization</h3>
                                    <div className="flex items-center gap-2">
                                        <Button type="button" onClick={handleCalculate} disabled={loading} className="bg-green-500 hover:bg-green-600 text-white rounded-full px-8 py-6 font-black text-lg shadow-lg">
                                            {loading ? <Loader2 className="mr-2 h-6 w-6 animate-spin" /> : <Calculator className="mr-2 h-6 w-6" />}
                                            Calculate Final Premium
                                        </Button>
                                    </div>
                                </div>

                                <div className="grid grid-cols-1 xl:grid-cols-2 gap-10">
                                    <div className="space-y-8">
                                        <div className="space-y-8">
                                            {/* Configuration Summary Card */}
                                            <Card className="p-10 rounded-[40px] border-none bg-slate-50/50 space-y-8 shadow-inner">
                                                <div className="grid grid-cols-2 gap-6">
                                                    <div className="space-y-2">
                                                        <span className="text-[10px] font-black text-slate-400 uppercase tracking-widest">Policy Type</span>
                                                        <div className="font-black text-slate-900 text-lg">{selectedPolicy.name}</div>
                                                    </div>
                                                    <div className="space-y-2">
                                                        <span className="text-[10px] font-black text-slate-400 uppercase tracking-widest">Frequency</span>
                                                        <div className="font-black text-slate-900 text-lg capitalize">{watch("premium_frequency")}</div>
                                                    </div>
                                                    <div className="space-y-2">
                                                        <span className="text-[10px] font-black text-slate-400 uppercase tracking-widest">Start Date</span>
                                                        <div className="font-black text-slate-900 text-lg">{watch("start_date")}</div>
                                                    </div>
                                                    <div className="space-y-2">
                                                        <span className="text-[10px] font-black text-slate-400 uppercase tracking-widest">NCD Status</span>
                                                        <div className="font-black text-slate-900 text-lg">{watch("ncd_protected") ? "Protected" : "Unprotected"}</div>
                                                    </div>
                                                </div>

                                                <div className="pt-8 border-t border-slate-200">
                                                    <span className="text-[10px] font-black text-slate-400 uppercase tracking-widest mb-4 block">Included Extra Services</span>
                                                    <div className="flex flex-wrap gap-2">
                                                        {calculation?.included_services?.map((s: any) => (
                                                            <Badge key={s.id} className="bg-white text-[#00539F] border-2 border-blue-100 rounded-xl px-4 py-2 font-bold shadow-sm">
                                                                {language === 'fr' ? s.name_fr || s.name : s.name_en || s.name}
                                                            </Badge>
                                                        ))}
                                                        {(!calculation?.included_services || calculation.included_services.length === 0) && (
                                                            <span className="text-slate-400 italic font-medium">No additional services active</span>
                                                        )}
                                                    </div>
                                                </div>
                                            </Card>

                                            {/* Detailed Tables Section */}
                                            <div className="space-y-6">
                                                {/* Risk Adjustments */}
                                                <div className="space-y-4">
                                                    <div className="flex items-center justify-between">
                                                        <h4 className="text-sm font-black text-slate-900 uppercase tracking-widest">Risk Calculation</h4>
                                                        <Badge variant="outline" className="text-orange-600 border-orange-100 bg-orange-50 font-black">AI Assessment</Badge>
                                                    </div>
                                                    <div className="rounded-[30px] border-2 border-slate-100 overflow-hidden bg-white">
                                                        <table className="w-full text-left">
                                                            <thead className="bg-slate-50 border-b-2 border-slate-100">
                                                                <tr>
                                                                    <th className="px-6 py-4 text-[10px] font-black text-slate-400 uppercase">Adjustment Type</th>
                                                                    <th className="px-6 py-4 text-[10px] font-black text-slate-400 uppercase">Weight</th>
                                                                    <th className="px-6 py-4 text-[10px] font-black text-slate-400 uppercase text-right">Premium Increase</th>
                                                                </tr>
                                                            </thead>
                                                            <tbody className="divide-y divide-slate-50">
                                                                <tr>
                                                                    <td className="px-6 py-4 font-bold text-slate-600">Base Premium</td>
                                                                    <td className="px-6 py-4 font-bold text-slate-400">1.0x</td>
                                                                    <td className="px-6 py-4 font-black text-slate-900 text-right">{wrapperFormatCurrency(calculatedValues?.base || 0)}</td>
                                                                </tr>
                                                                {selectedMultipliers.map(id => {
                                                                    const el = quoteElements.find(e => e.id === id);
                                                                    return (
                                                                        <tr key={id}>
                                                                            <td className="px-6 py-4 font-bold text-slate-600">{el?.name}</td>
                                                                            <td className="px-6 py-4 font-bold text-orange-500">+{((el?.value || 1) - 1) * 100}%</td>
                                                                            <td className="px-6 py-4 font-black text-orange-600 text-right">+{wrapperFormatCurrency((calculatedValues?.base || 0) * ((el?.value || 1) - 1))}</td>
                                                                        </tr>
                                                                    );
                                                                })}
                                                            </tbody>
                                                        </table>
                                                    </div>
                                                </div>

                                                {/* Fixed Fees & Taxes */}
                                                <div className="space-y-4">
                                                    <h4 className="text-sm font-black text-slate-900 uppercase tracking-widest">Fees & External Charges</h4>
                                                    <div className="rounded-[30px] border-2 border-slate-100 overflow-hidden bg-white">
                                                        <table className="w-full text-left">
                                                            <thead className="bg-slate-50 border-b-2 border-slate-100">
                                                                <tr>
                                                                    <th className="px-6 py-4 text-[10px] font-black text-slate-400 uppercase">Description</th>
                                                                    <th className="px-6 py-4 text-[10px] font-black text-slate-400 uppercase">Note</th>
                                                                    <th className="px-6 py-4 text-[10px] font-black text-slate-400 uppercase text-right">Amount</th>
                                                                </tr>
                                                            </thead>
                                                            <tbody className="divide-y divide-slate-50">
                                                                {selectedFees.map(id => {
                                                                    const el = quoteElements.find(e => e.id === id);
                                                                    return (
                                                                        <tr key={id}>
                                                                            <td className="px-6 py-4 font-bold text-slate-600">{el?.name}</td>
                                                                            <td className="px-6 py-4 font-bold text-slate-400 text-xs">Extras</td>
                                                                            <td className="px-6 py-4 font-black text-slate-900 text-right">+{formatCurrency(el?.value || 0)}</td>
                                                                        </tr>
                                                                    );
                                                                })}
                                                                {/* Display Dynamic Admin Fee if > 0 */}
                                                                {(calculation?.calculation_breakdown?.step2_admin_fee?.amount ?? 0) > 0 && (
                                                                    <tr>
                                                                        <td className="px-6 py-4 font-bold text-slate-600 uppercase">COMPANY ADMIN FEE ({calculation?.calculation_breakdown?.step2_admin_fee?.percent ?? 0}%)</td>
                                                                        <td className="px-6 py-4 font-bold text-slate-400 text-xs">Mandatory</td>
                                                                        <td className="px-6 py-4 font-black text-slate-900 text-right">+{formatCurrency(calculation?.calculation_breakdown?.step2_admin_fee?.amount ?? 0)}</td>
                                                                    </tr>
                                                                )}
                                                                {/* Display Dynamic Tax */}
                                                                <tr>
                                                                    <td className="px-6 py-4 font-bold text-slate-600 uppercase">
                                                                        GOVT TAX ({calculation?.calculation_breakdown?.step5_tax?.percent ?? companySettings?.government_tax_percent ?? 0}%)
                                                                    </td>
                                                                    <td className="px-6 py-4 font-bold text-blue-500 text-xs">Included</td>
                                                                    <td className="px-6 py-4 font-black text-slate-900 text-right">+{formatCurrency(calculation?.calculation_breakdown?.step5_tax?.amount ?? 0)}</td>
                                                                </tr>
                                                            </tbody>
                                                        </table>
                                                    </div>
                                                </div>

                                                {/* Discounts */}
                                                {(selectedDiscounts.length > 0 || watch("discount_percent") > 0) && (
                                                    <div className="space-y-4">
                                                        <h4 className="text-sm font-black text-slate-900 uppercase tracking-widest text-green-600">Applied Discounts</h4>
                                                        <div className="rounded-[30px] border-2 border-green-100 overflow-hidden bg-green-50/20 text-green-700">
                                                            <table className="w-full text-left">
                                                                <tbody className="divide-y divide-green-50">
                                                                    {selectedDiscounts.map(id => {
                                                                        const el = quoteElements.find(e => e.id === id);
                                                                        return (
                                                                            <tr key={id}>
                                                                                <td className="px-6 py-4 font-bold">{el?.name}</td>
                                                                                <td className="px-6 py-4 font-bold text-xs">-{el?.value}% Discount</td>
                                                                                <td className="px-6 py-4 font-black text-right">-{wrapperFormatCurrency((calculatedValues?.base || 0) * ((el?.value || 0) / 100))}</td>
                                                                            </tr>
                                                                        );
                                                                    })}
                                                                    {/* Manual percent discount row */}
                                                                    {(watch("discount_percent") > 0 || (calculation?.calculation_breakdown?.step4_admin_discount?.amount ?? 0) > 0) && (
                                                                        <tr className="bg-green-100/50">
                                                                            <td className="px-6 py-4 font-black text-[#00539F]">TOTAL ADMIN DISCOUNTS</td>
                                                                            <td className="px-6 py-4 font-bold text-xs">-{calculation?.calculation_breakdown?.step4_admin_discount?.percent ?? watch("discount_percent")}% Total</td>
                                                                            <td className="px-6 py-4 font-black text-right">-{wrapperFormatCurrency(calculation?.calculation_breakdown?.step4_admin_discount?.amount ?? 0)}</td>
                                                                        </tr>
                                                                    )}
                                                                </tbody>
                                                            </table>
                                                        </div>
                                                    </div>
                                                )}
                                            </div>
                                        </div>
                                    </div>

                                    {/* Final Breakdown Card */}
                                    <div className="relative">
                                        <Card className="p-12 rounded-[50px] border-none bg-[#00539F] text-white shadow-2xl min-h-full flex flex-col">
                                            <div className="space-y-10 flex-1">
                                                <div className="flex justify-between items-start">
                                                    <div>
                                                        <h4 className="text-3xl font-black">Professional Summary</h4>
                                                        <p className="text-blue-100/60 font-medium uppercase tracking-widest text-xs mt-2">Comprehensive Premium Analysis</p>
                                                    </div>
                                                    <div className="h-16 w-16 bg-white/10 backdrop-blur-md rounded-[20px] flex items-center justify-center border border-white/20">
                                                        <FileText className="h-8 w-8 text-white" />
                                                    </div>
                                                </div>

                                                <div className="space-y-6">
                                                    <div className="flex justify-between items-center text-lg">
                                                        <span className="font-medium text-blue-100/80">Base Premium</span>
                                                        <span className="font-black">{wrapperFormatCurrency(calculatedValues?.base || 0)}</span>
                                                    </div>
                                                    <div className="flex justify-between items-center text-lg">
                                                        <span className="font-medium text-blue-100/80">Total Risks Increase</span>
                                                        <span className="font-black text-orange-400">+{wrapperFormatCurrency(calculatedValues?.totalRisk || 0)}</span>
                                                    </div>
                                                    <div className="flex justify-between items-center text-lg">
                                                        <span className="font-medium text-blue-100/80">Fixed Fees & Extras</span>
                                                        <span className="font-black">+{wrapperFormatCurrency(calculatedValues?.totalFees || 0)}</span>
                                                    </div>
                                                    {(calculatedValues?.adminFee ?? 0) > 0 && (
                                                        <div className="flex justify-between items-center text-lg">
                                                            <span className="font-medium text-blue-100/80">Company Admin Fee</span>
                                                            <span className="font-black">+{wrapperFormatCurrency(calculatedValues?.adminFee || 0)}</span>
                                                        </div>
                                                    )}
                                                    <div className="flex justify-between items-center text-lg">
                                                        <span className="font-medium text-blue-100/80">Total Discounts</span>
                                                        <span className="font-black text-green-400">-{wrapperFormatCurrency(calculatedValues?.totalDiscount || 0)}</span>
                                                    </div>
                                                    <div className="pt-6 border-t border-white/10 flex justify-between items-center text-lg">
                                                        <span className="font-medium text-blue-100/80">Net Premium (Subtotal)</span>
                                                        <span className="font-black">{wrapperFormatCurrency(calculatedValues?.subtotal || 0)}</span>
                                                    </div>
                                                    <div className="flex justify-between items-center text-lg">
                                                        <span className="font-medium text-blue-100/80">Government Taxes ({companySettings?.government_tax_percent || 0}%)</span>
                                                        <span className="font-black">+{wrapperFormatCurrency(calculatedValues?.totalTax || 0)}</span>
                                                    </div>
                                                </div>

                                                <div className="pt-10 border-t border-white/20">
                                                    <div className="flex flex-col gap-2">
                                                        <span className="text-sm font-black text-blue-100/60 uppercase tracking-[0.2em]">Final Premium Payable</span>
                                                        <div className="text-6xl font-black tracking-tighter">
                                                            {wrapperFormatCurrency(calculatedValues?.finalPremium || 0)}
                                                        </div>
                                                        {watch('premium_frequency') !== 'annual' && calculation && (
                                                            <div className="mt-4 p-4 bg-white/10 rounded-2xl space-y-2 border border-white/10">
                                                                <div className="flex justify-between items-center">
                                                                    <span className="text-sm font-bold text-blue-100/60 uppercase">Monthly Installment</span>
                                                                    <span className="text-xl font-black">{wrapperFormatCurrency(calculation.monthly_installment)}</span>
                                                                </div>
                                                                <div className="flex justify-between items-center text-xs text-blue-100/40">
                                                                    <span>Total with Interest (APR {calculation.apr_percent}%)</span>
                                                                    <span>{wrapperFormatCurrency(calculation.total_installment_price)}</span>
                                                                </div>
                                                            </div>
                                                        )}
                                                        <span className="text-blue-100/40 text-xs font-bold mt-2 uppercase tracking-widest">Guaranteed for 30 days • Inclusive of all taxes</span>
                                                    </div>
                                                </div>
                                            </div>

                                            <div className="mt-12 flex gap-4">
                                                <Button type="button" onClick={(e) => onCreate('sent', e)} disabled={loading || !calculation} className="flex-1 bg-white hover:bg-white/90 text-[#00539F] rounded-[25px] h-20 text-xl font-black shadow-xl">
                                                    <Save className="mr-2 h-6 w-6" /> Finalize & Send
                                                </Button>
                                                <Button type="button" variant="outline" onClick={(e) => onCreate('draft', e)} disabled={loading || !calculation} className="px-8 rounded-[25px] border-white/20 bg-white/5 hover:bg-white/10 text-white font-black h-20 border-2">
                                                    Draft
                                                </Button>
                                            </div>
                                        </Card>

                                        {/* Floating Badge for matching policies */}
                                        <div className="absolute -top-4 -right-4 h-12 w-12 bg-white rounded-full flex items-center justify-center shadow-xl border-4 border-[#00539F]">
                                            <Check className="h-6 w-6 text-green-500" />
                                        </div>
                                    </div>
                                </div>
                            </div>
                        )}
                    </form>
                </FormProvider>
            </CardContent>

            <CardFooter className="flex justify-between border-t border-slate-100 p-8 bg-slate-50/50 rounded-b-[60px]">
                {step > 1 ? (
                    <Button
                        variant="ghost"
                        onClick={() => setStep(step - 1)}
                        className="text-slate-400 font-black uppercase tracking-widest text-xs hover:text-[#00539F] hover:bg-white transition-all px-8 h-12 rounded-2xl"
                    >
                        <ArrowLeft className="mr-2 h-4 w-4" /> Go Back
                    </Button>
                ) : (
                    <Button
                        variant="ghost"
                        onClick={() => router.push('/dashboard/quotes')}
                        className="text-slate-400 font-black uppercase tracking-widest text-xs hover:text-slate-600 hover:bg-white transition-all px-8 h-12 rounded-2xl"
                    >
                        Exit Wizard
                    </Button>
                )}
            </CardFooter>

            {/* ERROR DIALOGS */}
            <AlertDialog open={noPolicyOpen} onOpenChange={setNoPolicyOpen}>
                <AlertDialogContent className="rounded-[40px] border-none p-10">
                    <AlertDialogHeader>
                        <AlertDialogTitle className="text-2xl font-black text-slate-900">No Premium Policy Available</AlertDialogTitle>
                        <AlertDialogDescription className="text-slate-500 font-medium text-lg leading-relaxed">
                            {noPolicyMessage || "You must create a policy first before creating a quote."}
                        </AlertDialogDescription>
                    </AlertDialogHeader>
                    <AlertDialogFooter className="mt-8">
                        <AlertDialogAction onClick={() => setNoPolicyOpen(false)} className="bg-[#00539F] text-white rounded-2xl h-14 px-10 font-black">Close</AlertDialogAction>
                    </AlertDialogFooter>
                </AlertDialogContent>
            </AlertDialog>

            <AlertDialog open={missingInfoOpen} onOpenChange={setMissingInfoOpen}>
                <AlertDialogContent className="rounded-[40px] border-none p-10">
                    <AlertDialogHeader>
                        <AlertDialogTitle className="text-2xl font-black text-slate-900">Missing Information</AlertDialogTitle>
                        <AlertDialogDescription className="text-slate-500 font-medium text-lg leading-relaxed">
                            The client is missing information required for eligibility check. Please update the client profile with the following fields:
                            <ul className="list-disc pl-5 mt-4 space-y-2 text-slate-900 font-black">
                                {missingFields.map(field => (
                                    <li key={field}>{field}</li>
                                ))}
                            </ul>
                        </AlertDialogDescription>
                    </AlertDialogHeader>
                    <AlertDialogFooter className="mt-8">
                        <AlertDialogAction onClick={() => setMissingInfoOpen(false)} className="bg-[#00539F] text-white rounded-2xl h-14 px-10 font-black">OK, I'll fix it</AlertDialogAction>
                    </AlertDialogFooter>
                </AlertDialogContent>
            </AlertDialog>
        </Card>
    );
}
