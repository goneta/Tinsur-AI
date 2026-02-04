'use client';

import React, { useState } from 'react';
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from '@/components/ui/card';
import { useLanguage } from '@/contexts/language-context';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import {
    LayoutGrid, List, Plus, User, Car, Phone, MapPin,
    CreditCard, Calendar, Briefcase, Users, Baby,
    CheckCircle2, XCircle, Info, Upload, Search, Camera, Calculator,
    ShieldCheck, Edit3, PlusCircle, ArrowLeft, Save, Edit2, ChevronRight, FileText, Download,
    Clock
} from 'lucide-react';
import { portalApi } from '@/lib/portal-api';
import { useEffect } from 'react';
import { QuoteAPI } from '@/lib/api/quotes';
import { useAuth } from '@/lib/auth';
import { Badge } from "@/components/ui/badge";
import { Checkbox } from "@/components/ui/checkbox";
import {
    Table,
    TableBody,
    TableCell,
    TableHead,
    TableHeader,
    TableRow,
} from "@/components/ui/table";
import { Driver } from './insurance-details-tab';
import { useToast } from '@/components/ui/use-toast';

interface Vehicle {
    id: string;
    make: string;
    model: string;
    registrationNumber: string;
    mileage: string;
    vehicleAge: string;
}

interface QuoteCreationWizardProps {
    open: boolean;
    onOpenChange: (open: boolean) => void;
    vehicle: Vehicle | null;
    drivers: Driver[];
    onSuccess: (quote: any) => void;
    clientId?: string;
    isAdmin?: boolean;
}

export function QuoteCreationWizard({ open, onOpenChange, vehicle, drivers, onSuccess, clientId, isAdmin }: QuoteCreationWizardProps) {
    const [step, setStep] = useState(1);
    const [isSubmitting, setIsSubmitting] = useState(false);
    const { language, t } = useLanguage();
    const { toast } = useToast();
    const { user } = useAuth();

    // Form States
    const [selectedPolicy, setSelectedPolicy] = useState<any>(null);
    const [selectedServices, setSelectedServices] = useState<string[]>([]);
    const [mainDriver, setMainDriver] = useState(drivers.length > 0 ? drivers[0].fullName : '');
    const [additionalDrivers, setAdditionalDrivers] = useState<any[]>([]);
    const [ncdProtected, setNcdProtected] = useState<boolean | null>(null);
    const [startDate, setStartDate] = useState(new Date().toISOString().split('T')[0]);
    const [paymentFrequency, setPaymentFrequency] = useState<'Annual' | 'Monthly'>('Monthly');
    const [expandedTiers, setExpandedTiers] = useState<Record<string, boolean>>({});
    const [realPolicies, setRealPolicies] = useState<any[]>([]);
    const [isLoadingPolicies, setIsLoadingPolicies] = useState(false);

    const isPublicMarketplace = user?.role === 'client' && !user?.company_id;

    useEffect(() => {
        if (open) {
            const fetchPolicies = async () => {
                setIsLoadingPolicies(true);
                try {
                    const mainDriverObj = drivers.find(d => d.fullName === mainDriver) || drivers[0];

                    const calculateAge = (dobString?: string) => {
                        if (!dobString) return 30; // Default
                        const dob = new Date(dobString);
                        const diff_ms = Date.now() - dob.getTime();
                        const age_dt = new Date(diff_ms);
                        return Math.abs(age_dt.getUTCFullYear() - 1970);
                    };

                    const calculateLicenseYears = (issueDate?: string) => {
                        if (!issueDate) return 0;
                        const issue = new Date(issueDate);
                        const diff_ms = Date.now() - issue.getTime();
                        const val = new Date(diff_ms);
                        return Math.abs(val.getUTCFullYear() - 1970);
                    }

                    const overrides = {
                        vehicle_details: {
                            make: vehicle?.make,
                            model: vehicle?.model,
                            registration_number: vehicle?.registrationNumber,
                            mileage: vehicle?.mileage,
                            value: 12500, // Todo: Add value to vehicle interface
                            age: parseInt(vehicle?.vehicleAge || "0") || 0
                        },
                        driver_details: {
                            date_of_birth: (mainDriverObj as any).dateOfBirth,
                            age: calculateAge((mainDriverObj as any).dateOfBirth),
                            license_years: calculateLicenseYears(mainDriverObj?.licenseIssueDate),
                            ncd: 5 // Default for now
                        }
                    };

                    const result = isPublicMarketplace
                        ? await QuoteAPI.matchPoliciesPublic(overrides)
                        : await QuoteAPI.matchPolicies(clientId, overrides);

                    if (result.status === "success") {
                        const policies = isPublicMarketplace
                            ? (result.companies || []).flatMap((c: any) => (c.policies || []).map((p: any) => ({
                                ...p,
                                company_name: c.company_name,
                                company_primary_color: c.company_primary_color
                            })))
                            : result.data;

                        setRealPolicies(policies);
                        // Default selection to the first policy (often Bronze or similar)
                        if (policies && policies.length > 0) {
                            setSelectedPolicy(policies[0]);
                        }
                    } else if (result.status === "no_policies") {
                        setRealPolicies([]);
                    }
                } catch (error: any) {
                    console.error("Failed to fetch eligible policies:", error);
                    if (error.response?.data?.detail?.code === "NO_PREMIUM_POLICIES") {
                        setRealPolicies([]);
                    }
                } finally {
                    setIsLoadingPolicies(false);
                }
            };
            fetchPolicies();
        }
    }, [open, clientId, isPublicMarketplace]);

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

    const getServicesForPolicy = (policy: any) => {
        if (!policy || !policy.services) return [];
        return policy.services.map((s: any) => s.id || s.code);
    };

    const getServicesForLevel = (level: string) => {
        const policy = realPolicies.find(p => p.name === level);
        return getServicesForPolicy(policy);
    };

    const coverLevel = selectedPolicy?.name || 'Bronze';

    const calculateTotalPremium = (policy: any, additionalServices: string[]) => {
        if (!policy) return "0.00";
        const basePrice = parseFloat(policy.price) || 0;

        const defaultServiceIds = policy.services?.map((s: any) => s.id) || [];
        const extraServices = additionalServices.filter(id => !defaultServiceIds.includes(id));

        const additionalPrice = extraServices.reduce((acc, id) => {
            return acc + (FEATURES_MAP[id]?.price || 0);
        }, 0);

        return (basePrice + additionalPrice).toFixed(2);
    };

    const toggleTierFeatures = (level: string) => {
        setExpandedTiers(prev => ({ ...prev, [level]: !prev[level] }));
    };

    // Guard against null vehicle or not open
    // Move after hooks to follow React rules
    if (!open || !vehicle) return null;

    const nextStep = () => setStep(prev => prev + 1);
    const prevStep = () => setStep(prev => prev - 1);

    const handleSubmit = async () => {
        // Validation
        if (!selectedPolicy) {
            toast({ title: "Validation Error", description: "Please select a coverage plan", variant: "destructive" });
            return;
        }
        if (!mainDriver) {
            toast({ title: "Validation Error", description: "Main driver is required", variant: "destructive" });
            return;
        }
        if (!startDate) {
            toast({ title: "Validation Error", description: "Start date is required", variant: "destructive" });
            return;
        }

        setIsSubmitting(true);
        try {
            const finalPremium = calculateTotalPremium(selectedPolicy, selectedServices);
            const defaultServices = selectedPolicy.services?.map((s: any) => s.id) || [];
            const allIncludedServices = Array.from(new Set([...defaultServices, ...selectedServices]));

            const quoteData = {
                client_id: clientId!,
                policy_type_id: selectedPolicy.id,
                coverage_amount: 1000000,
                premium_frequency: paymentFrequency.toLowerCase() as any,
                duration_months: 12,
                discount_percent: 0,
                details: {
                    vehicle_id: vehicle?.id,
                    cover_level: selectedPolicy.name,
                    main_driver: mainDriver,
                    additional_drivers: additionalDrivers,
                    ncd_protected: ncdProtected,
                    start_date: startDate,
                    included_services: allIncludedServices
                },
                included_services: allIncludedServices
            };

            const createdQuote = await QuoteAPI.create(quoteData as any);

            // Map createdQuote back to the format InsuranceDetailsTab expects
            const mappedQuote = {
                id: createdQuote.id,
                vehicle,
                reference: createdQuote.quote_number,
                coverLevel: selectedPolicy.name,
                basePremium: `£${selectedPolicy.price}`,
                premium: `£${createdQuote.final_premium}`,
                expiresAt: createdQuote.valid_until || new Date(Date.now() + 30 * 24 * 60 * 60 * 1000).toISOString().split('T')[0],
                drivers: [mainDriver, ...additionalDrivers.map(d => d.name)],
                startDate,
                paymentFrequency,
                included_services: allIncludedServices,
                status: createdQuote.status
            };

            onSuccess(mappedQuote);
            toast({ title: "Success", description: "Quote created successfully!" });
        } catch (error: any) {
            console.error("Failed to create quote:", error);
            toast({
                title: "Error",
                description: error.response?.data?.detail || "Failed to create quote. Please try again.",
                variant: "destructive"
            });
        } finally {
            setIsSubmitting(false);
        }
    };

    return (
        <div className="space-y-8 animate-in slide-in-from-right duration-500">
            {/* Header */}
            <div className="flex items-center justify-between">
                <Button variant="ghost" onClick={() => onOpenChange(false)} className="text-gray-500 hover:text-gray-700 font-bold -ml-4">
                    <ArrowLeft className="h-5 w-5 mr-2" />
                    {t('Back to Vehicles')}
                </Button>
                <div className="flex items-center gap-2">
                    <span className="text-sm font-bold text-gray-400">{t('Step')} {step} {t('of')} 7</span>
                    <div className="flex gap-1">
                        {[1, 2, 3, 4, 5, 6, 7].map(s => (
                            <div key={s} className={`h-1.5 w-8 rounded-full transition-all ${s === step ? 'bg-[#00539F]' : s < step ? 'bg-green-500' : 'bg-gray-100'}`} />
                        ))}
                    </div>
                </div>
            </div>

            <Card className="rounded-[40px] border-none shadow-2xl overflow-hidden bg-white">
                <CardContent className="p-12">
                    {/* STEP 1: PRELIMINARIES (IMG 1-4) - INTRO & INFO */}
                    {step === 1 && (
                        <div className="space-y-8 animate-in fade-in slide-in-from-bottom-4 duration-500">
                            <div className="space-y-4">
                                <h2 className="text-4xl font-black text-gray-900 tracking-tight">{t("Let's get you a quote")}</h2>
                                <p className="text-xl text-gray-500 font-medium tracking-tight">{t('For your')} {vehicle.make} {vehicle.model} ({vehicle.registrationNumber})</p>
                            </div>

                            <div className="bg-blue-50 rounded-3xl p-8 border border-blue-100 space-y-4">
                                <div className="flex items-start gap-4">
                                    <div className="h-12 w-12 bg-white rounded-2xl flex items-center justify-center flex-shrink-0 shadow-sm">
                                        <Info className="h-6 w-6 text-[#00539F]" />
                                    </div>
                                    <div className="space-y-2">
                                        <h3 className="text-lg font-black text-[#002B52]">{t('Important Information')}</h3>
                                        <p className="text-[#00539F] font-bold leading-relaxed">
                                            {t("To provide an accurate quote, we'll perform a soft credit check. This won't affect your credit score. By proceeding, you confirm all details provided are accurate.")}
                                        </p>
                                    </div>
                                </div>
                            </div>

                            <div className="p-8 bg-gray-50 rounded-[30px] border border-gray-100 space-y-6">
                                <div className="flex items-center justify-between gap-4">
                                    <div>
                                        <h4 className="font-black text-gray-900">{t('Eligibility Guarantee')}</h4>
                                        <p className="text-sm text-gray-500 font-bold">{t('98% of users with your profile get approved instantly.')}</p>
                                    </div>
                                    <ShieldCheck className="h-10 w-10 text-green-500" />
                                </div>
                            </div>

                            <Button onClick={nextStep} className="w-full bg-[#00539F] hover:bg-[#004380] text-white rounded-2xl h-16 text-xl font-black shadow-lg transition-all active:scale-[0.98]">
                                {t('Get Started')} <ChevronRight className="ml-2 h-6 w-6" />
                            </Button>
                        </div>
                    )}

                    {/* STEP 2: DRIVERS (IMG 5-10) - MAIN & NAMED DRIVERS */}
                    {step === 2 && (
                        <div className="space-y-8 animate-in fade-in slide-in-from-bottom-4 duration-500">
                            <div className="space-y-4">
                                <h2 className="text-3xl font-black text-gray-900">{t('Who will be the drivers?')}</h2>
                                <p className="text-gray-500 font-bold text-lg">{t('Select the main driver and any additional named drivers.')}</p>
                            </div>

                            <div className="space-y-6">
                                <div className="space-y-3">
                                    <Label className="text-xs font-black uppercase tracking-widest text-gray-400">{t('Main Driver')}</Label>
                                    <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                                        {drivers.map((driver) => (
                                            <div
                                                key={driver.id}
                                                onClick={() => setMainDriver(driver.fullName)}
                                                className={`p-6 rounded-[25px] border-2 cursor-pointer transition-all flex items-center justify-between ${mainDriver === driver.fullName ? 'border-[#00539F] bg-blue-50/50 shadow-md' : 'border-gray-100 hover:border-gray-200 bg-white'}`}
                                            >
                                                <div className="flex items-center gap-4">
                                                    <div className="h-10 w-10 rounded-full bg-gray-100 flex items-center justify-center font-black text-[#00539F] overflow-hidden">
                                                        {driver.photoUrl ? (
                                                            <img src={driver.photoUrl} alt={driver.fullName} className="w-full h-full object-cover" />
                                                        ) : (
                                                            driver.fullName.charAt(0)
                                                        )}
                                                    </div>
                                                    <span className="font-black text-gray-900">{driver.fullName}</span>
                                                </div>
                                                {mainDriver === driver.fullName && <CheckCircle2 className="h-5 w-5 text-[#00539F]" />}
                                            </div>
                                        ))}
                                    </div>
                                </div>

                                <div className="space-y-4">
                                    <div className="flex items-center justify-between">
                                        <Label className="text-xs font-black uppercase tracking-widest text-gray-400">{t('Additional Drivers')}</Label>

                                        <div className="flex items-center gap-2">
                                            <select
                                                className="h-8 rounded-xl border border-gray-200 text-sm font-bold text-gray-700 px-3 outline-none focus:border-[#00539F]"
                                                value=""
                                                onChange={(e) => {
                                                    const driverId = e.target.value;
                                                    if (!driverId) return;
                                                    const driver = drivers.find(d => d.id === driverId);
                                                    if (driver) {
                                                        // Default relationship to 'Other' or prompt user, for now hardcoding or mapping if possible
                                                        // Since we don't have relationship in Driver model, assume 'Other' for now or add to state
                                                        setAdditionalDrivers([...additionalDrivers, { name: driver.fullName, relationship: 'Named Driver' }]);
                                                    }
                                                }}
                                            >
                                                <option value="" disabled>{t('Select driver to add...')}</option>
                                                {drivers
                                                    .filter(d => d.fullName !== mainDriver && !additionalDrivers.some(ad => ad.name === d.fullName))
                                                    .map(d => (
                                                        <option key={d.id} value={d.id}>{d.fullName}</option>
                                                    ))
                                                }
                                            </select>
                                        </div>
                                    </div>

                                    {additionalDrivers.length > 0 ? (
                                        <div className="space-y-3">
                                            {additionalDrivers.map((driver, idx) => (
                                                <div key={idx} className="p-4 bg-gray-50 rounded-2xl flex items-center justify-between">
                                                    <div className="flex items-center gap-3">
                                                        <User className="h-5 w-5 text-gray-400" />
                                                        <span className="font-bold">{driver.name}</span>
                                                    </div>
                                                    <Button variant="ghost" size="sm" onClick={() => setAdditionalDrivers(additionalDrivers.filter((_, i) => i !== idx))} className="text-red-500 hover:text-red-600 hover:bg-red-50">
                                                        Remove
                                                    </Button>
                                                </div>
                                            ))}
                                        </div>
                                    ) : (
                                        <div className="p-8 border border-dashed border-gray-200 rounded-[30px] text-center">
                                            <p className="text-sm text-gray-400 font-bold uppercase tracking-wider">No additional drivers added</p>
                                        </div>
                                    )}
                                </div>
                            </div>

                            <div className="flex gap-4">
                                <Button onClick={prevStep} variant="outline" className="h-16 px-8 rounded-2xl font-black border-gray-200">{t('Back')}</Button>
                                <Button onClick={nextStep} className="flex-1 bg-[#00539F] hover:bg-[#004380] text-white rounded-2xl h-16 text-xl font-black shadow-lg transition-all active:scale-[0.98]">
                                    {t('Next: Policy Details')} <ChevronRight className="ml-2 h-6 w-6" />
                                </Button>
                            </div>
                        </div>
                    )}

                    {/* STEP 3: POLICY DETAILS (IMG 11-14) - NCD, START DATE & PAYMENT */}
                    {step === 3 && (
                        <div className="space-y-10 animate-in fade-in slide-in-from-bottom-4 duration-500">
                            <h2 className="text-3xl font-black text-gray-900">{t('Policy Preferences')}</h2>

                            <div className="space-y-8">
                                <Card className="p-8 rounded-[30px] border-none bg-blue-50/50 space-y-6">
                                    <div className="flex items-center gap-4">
                                        <div className="h-10 w-10 bg-white rounded-xl flex items-center justify-center flex-shrink-0 shadow-sm">
                                            <ShieldCheck className="h-5 w-5 text-[#00539F]" />
                                        </div>
                                        <div>
                                            <h3 className="font-black text-gray-900">{t('Protect your No Claims Discount?')}</h3>
                                            <p className="text-sm text-gray-500 font-bold leading-snug">{t('Allows you to make two claims in the first year before your NCD is affected.')}</p>
                                        </div>
                                    </div>
                                    <div className="flex gap-4">
                                        <Button
                                            variant={ncdProtected === true ? 'default' : 'outline'}
                                            onClick={() => setNcdProtected(true)}
                                            className={`flex-1 h-14 rounded-2xl font-black text-lg ${ncdProtected === true ? 'bg-[#00539F]' : 'bg-white'}`}
                                        >
                                            {t('Yes, protect it')}
                                        </Button>
                                        <Button
                                            variant={ncdProtected === false ? 'default' : 'outline'}
                                            onClick={() => setNcdProtected(false)}
                                            className={`flex-1 h-14 rounded-2xl font-black text-lg ${ncdProtected === false ? 'bg-[#00539F]' : 'bg-white'}`}
                                        >
                                            {t('No thanks')}
                                        </Button>
                                    </div>
                                </Card>

                                <div className="grid grid-cols-1 md:grid-cols-2 gap-8">
                                    <div className="space-y-3">
                                        <Label className="text-xs font-black uppercase tracking-widest text-gray-400">{t('When do you want to start?')}</Label>
                                        <Input
                                            type="date"
                                            value={startDate}
                                            onChange={(e) => setStartDate(e.target.value)}
                                            className="h-14 rounded-2xl border-2 border-gray-100 font-black px-6 focus:border-[#00539F] transition-all"
                                        />
                                    </div>
                                    <div className="space-y-3">
                                        <Label className="text-xs font-black uppercase tracking-widest text-gray-400">{t('Payment frequency')}</Label>
                                        <div className="flex gap-2 p-1 bg-gray-100 rounded-2xl h-14">
                                            <button
                                                onClick={() => setPaymentFrequency('Monthly')}
                                                className={`flex-1 rounded-xl font-black text-sm transition-all ${paymentFrequency === 'Monthly' ? 'bg-white text-[#00539F] shadow-sm' : 'text-gray-500'}`}
                                            >
                                                {t('Monthly')}
                                            </button>
                                            <button
                                                onClick={() => setPaymentFrequency('Annual')}
                                                className={`flex-1 rounded-xl font-black text-sm transition-all ${paymentFrequency === 'Annual' ? 'bg-white text-[#00539F] shadow-sm' : 'text-gray-500'}`}
                                            >
                                                {t('Annual')}
                                            </button>
                                        </div>
                                    </div>
                                </div>
                            </div>

                            <div className="flex gap-4">
                                <Button onClick={prevStep} variant="outline" className="h-16 px-8 rounded-2xl font-black border-gray-200">{t('Back')}</Button>
                                <Button onClick={nextStep} className="flex-1 bg-[#00539F] hover:bg-[#004380] text-white rounded-2xl h-16 text-xl font-black shadow-lg transition-all active:scale-[0.98]">
                                    {t('Next: Review Details')} <ChevronRight className="ml-2 h-6 w-6" />
                                </Button>
                            </div>
                        </div>
                    )}

                    {/* STEP 4: REVIEW (IMG 15-20) - SUMMARY OF ALL DETAILS */}
                    {step === 4 && (
                        <div className="space-y-8 animate-in fade-in slide-in-from-bottom-4 duration-500">
                            <h2 className="text-3xl font-black text-gray-900">{t('Review your information')}</h2>

                            <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                                <Card className="rounded-[30px] border border-gray-100 p-8 space-y-6">
                                    <div className="flex justify-between items-start">
                                        <div className="flex items-center gap-3">
                                            <div className="p-2 bg-blue-50 rounded-xl">
                                                <Car className="h-5 w-5 text-[#00539F]" />
                                            </div>
                                            <h3 className="font-black text-gray-400 uppercase text-[10px] tracking-widest">{t('The Car')}</h3>
                                        </div>
                                        <Button variant="ghost" size="sm" className="text-[#00539F] font-black h-auto p-0 hover:bg-transparent">Edit</Button>
                                    </div>
                                    <div className="space-y-1">
                                        <p className="font-black text-xl">{vehicle.make} {vehicle.model}</p>
                                        <div className="inline-block bg-white border-2 border-gray-900 px-2 font-mono text-sm font-black tracking-widest mb-2">{vehicle.registrationNumber}</div>
                                        <p className="text-gray-400 font-bold text-sm">Value: £12,500 • Automatic</p>
                                    </div>
                                </Card>

                                <Card className="rounded-[30px] border border-gray-100 p-8 space-y-12">
                                    <div className="space-y-6">
                                        <div className="flex justify-between items-start">
                                            <div className="flex items-center gap-3">
                                                <div className="p-2 bg-blue-50 rounded-xl">
                                                    <User className="h-5 w-5 text-[#00539F]" />
                                                </div>
                                                <h3 className="font-black text-gray-400 uppercase text-[10px] tracking-widest">{t('Main Driver')}</h3>
                                            </div>
                                            <Button variant="ghost" size="sm" className="text-[#00539F] font-black h-auto p-0 hover:bg-transparent">Edit</Button>
                                        </div>
                                        <div className="space-y-1">
                                            <p className="font-black text-xl">{mainDriver}</p>
                                            <p className="font-bold text-gray-500 text-sm">123 Insurance Way, London • 8 Years NCD</p>
                                        </div>
                                    </div>

                                    {additionalDrivers.length > 0 && (
                                        <div className="space-y-4 pt-6 border-t border-gray-100">
                                            <div className="flex items-center gap-3">
                                                <Users className="h-4 w-4 text-gray-400" />
                                                <h3 className="font-black text-gray-400 uppercase text-[10px] tracking-widest">Named Drivers</h3>
                                            </div>
                                            <div className="flex flex-wrap gap-2">
                                                {additionalDrivers.map((d, i) => (
                                                    <Badge key={i} className="bg-gray-100 text-gray-700 hover:bg-gray-100 font-bold py-1 px-3 rounded-lg border-none">
                                                        {d.name}
                                                    </Badge>
                                                ))}
                                            </div>
                                        </div>
                                    )}
                                </Card>
                            </div>

                            <Card className="p-8 rounded-[30px] border border-gray-100 bg-gray-50/50">
                                <h3 className="font-black text-gray-400 uppercase text-[10px] tracking-widest mb-6 border-b border-gray-100 pb-4">{t('Eligibility Verification')}</h3>
                                <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                                    {[
                                        "No claims/accidents in 5 years",
                                        "Primary residence in the UK",
                                        "Vehicle for social use only",
                                        "No driving convictions"
                                    ].map((check, i) => (
                                        <div key={i} className="flex items-center gap-3">
                                            <div className="h-5 w-5 rounded-full bg-green-500 flex items-center justify-center">
                                                <CheckCircle2 className="h-4 w-4 text-white" />
                                            </div>
                                            <span className="font-bold text-sm text-gray-700">{check}</span>
                                        </div>
                                    ))}
                                </div>
                            </Card>

                            <div className="flex gap-4">
                                <Button onClick={prevStep} variant="outline" className="h-16 px-8 rounded-2xl font-black border-gray-200">{t('Back')}</Button>
                                <Button onClick={nextStep} className="flex-1 bg-[#00539F] hover:bg-[#004380] text-white rounded-2xl h-16 text-xl font-black shadow-lg transition-all active:scale-[0.98]">
                                    {t('Looks good, show quotes')} <ChevronRight className="ml-2 h-6 w-6" />
                                </Button>
                            </div>
                        </div>
                    )}

                    {/* STEP 5: QUOTES (IMG 21-25) - CHOOSE COVERAGE */}
                    {step === 5 && (
                        <div className="space-y-8 animate-in fade-in slide-in-from-bottom-4 duration-500">
                            <div className="space-y-2">
                                <h2 className="text-3xl font-black text-gray-900">{t('Choose your coverage')}</h2>
                                <p className="text-gray-500 font-bold">{t('Great news! We found 3 eligible policies for you.')}</p>
                            </div>

                            {isLoadingPolicies ? (
                                <div className="flex flex-col items-center justify-center p-20 space-y-4">
                                    <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-[#00539F]"></div>
                                    <p className="font-bold text-gray-500">{t('Matching eligible policies...')}</p>
                                </div>
                            ) : realPolicies.length === 0 ? (
                                <div className="p-12 text-center bg-gray-50 rounded-[40px] border-2 border-dashed border-gray-200">
                                    <XCircle className="h-12 w-12 text-gray-300 mx-auto mb-4" />
                                    <h3 className="text-xl font-black text-gray-900 mb-2">{t('No policies found')}</h3>
                                    <p className="text-gray-500 font-bold">{t('We couldn\'t find any eligible policies matching your profile.')}</p>
                                </div>
                            ) : (
                                <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
                                    {realPolicies.map((policy) => (
                                        <div
                                            key={policy.id}
                                            onClick={() => setSelectedPolicy(policy)}
                                            className={`rounded-[40px] cursor-pointer transition-all border-2 p-8 space-y-8 relative group bg-white ${selectedPolicy?.id === policy.id ? 'border-[#00539F] shadow-2xl scale-[1.02] ring-4 ring-blue-50' : 'border-gray-100 hover:border-gray-200 hover:shadow-xl'}`}
                                        >
                                            <div className="space-y-4">
                                                <div className="flex justify-between items-center">
                                                    <div className="flex items-center gap-2">
                                                        <div className={`h-8 w-8 rounded-lg flex items-center justify-center ${selectedPolicy?.id === policy.id ? 'bg-[#00539F] text-white' : 'bg-gray-100 text-gray-400'}`}>
                                                            <ShieldCheck className="h-5 w-5" />
                                                        </div>
                                                        <h3 className="font-black text-xl group-hover:text-[#00539F] transition-colors">{policy.name}</h3>
                                                    </div>
                                                    {policy.name.toLowerCase().includes('silver') && <Badge className="bg-[#00539F] text-white font-black text-[10px] py-1 px-3 rounded-lg uppercase tracking-wider">{t('Popular')}</Badge>}
                                                </div>
                                                <p className={`font-black text-4xl ${selectedPolicy?.id === policy.id ? 'text-[#00539F]' : 'text-gray-900'}`}>£{policy.price}</p>
                                            </div>

                                            <div className="space-y-3 pt-6 border-t border-gray-50 max-h-[200px] overflow-y-auto pr-1">
                                                {(expandedTiers[policy.id] ? Object.keys(FEATURES_MAP) : (policy.services?.map((s: any) => s.id) || [])).map((serviceId: string, i: number) => (
                                                    <div key={i} className="flex items-center gap-3">
                                                        <CheckCircle2 className={`h-4 w-4 flex-shrink-0 ${selectedPolicy?.id === policy.id ? 'text-[#00539F]' : 'text-gray-300'}`} />
                                                        <span className="text-xs font-bold text-gray-600 line-clamp-1">
                                                            {FEATURES_MAP[serviceId]?.[language] || FEATURES_MAP[serviceId]?.en || serviceId}
                                                        </span>
                                                    </div>
                                                ))}
                                                <button
                                                    onClick={(e) => {
                                                        e.stopPropagation();
                                                        toggleTierFeatures(policy.id);
                                                    }}
                                                    className="text-[#00539F] text-xs font-bold hover:underline mt-2 flex items-center gap-1"
                                                >
                                                    {expandedTiers[policy.id] ? t('common.see_less', 'See base features') : t('common.see_all', 'See all included features')}
                                                    <ChevronRight className={`h-3 w-3 transform transition-transform ${expandedTiers[policy.id] ? '-rotate-90' : 'rotate-90'}`} />
                                                </button>
                                            </div>

                                            <Button
                                                variant={selectedPolicy?.id === policy.id ? 'default' : 'outline'}
                                                className={`w-full rounded-2xl font-black h-12 shadow-md transition-all ${selectedPolicy?.id === policy.id ? 'bg-[#00539F] hover:bg-[#004380]' : 'border-gray-200'}`}
                                            >
                                                {selectedPolicy?.id === policy.id ? t('Selected') : t('Choose')}
                                            </Button>
                                        </div>
                                    ))}
                                </div>
                            )}

                            <div className="flex gap-4">
                                <Button onClick={prevStep} variant="outline" className="h-16 px-8 rounded-2xl font-black border-gray-200">{t('Back')}</Button>
                                <Button onClick={nextStep} className="flex-1 bg-[#00539F] hover:bg-[#004380] text-white rounded-2xl h-16 text-xl font-black shadow-lg transition-all active:scale-[0.98]">
                                    {t('Review Optional Extras')} <ChevronRight className="ml-2 h-6 w-6" />
                                </Button>
                            </div>
                        </div>
                    )}

                    {/* STEP 6: OPTIONAL EXTRAS (IMG 26-34) - ADD-ONS */}
                    {step === 6 && (
                        <div className="space-y-8 animate-in fade-in slide-in-from-bottom-4 duration-500">
                            <div className="space-y-2">
                                <h2 className="text-3xl font-black text-gray-900">{t('Add optional extras')}</h2>
                                <p className="text-gray-500 font-bold">{t('Customize your policy with these valuable additions.')}</p>
                            </div>

                            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                                {Object.keys(FEATURES_MAP).filter(id => !getServicesForLevel(coverLevel).includes(id)).map((id) => (
                                    <div
                                        key={id}
                                        className={`flex items-center justify-between p-6 rounded-[25px] border-2 transition-all cursor-pointer group ${selectedServices.includes(id) ? 'border-[#00539F] bg-blue-50/20' : 'border-gray-100 hover:border-gray-200 bg-white'}`}
                                        onClick={() => {
                                            setSelectedServices(prev =>
                                                prev.includes(id) ? prev.filter(i => i !== id) : [...prev, id]
                                            );
                                        }}
                                    >
                                        <div className="flex items-center gap-4">
                                            <div className={`h-6 w-6 rounded-lg border-2 flex items-center justify-center transition-all ${selectedServices.includes(id) ? 'border-[#00539F] bg-[#00539F]' : 'border-gray-300'}`}>
                                                {selectedServices.includes(id) && <CheckCircle2 className="h-4 w-4 text-white" />}
                                            </div>
                                            <div className="space-y-0.5">
                                                <p className="font-bold text-sm text-gray-900 line-clamp-1">{FEATURES_MAP[id]?.[language] || FEATURES_MAP[id]?.en}</p>
                                                <p className="text-[10px] font-bold text-gray-400 uppercase">{t('Optional Add-on')}</p>
                                            </div>
                                        </div>
                                        <Badge className="bg-white border border-gray-100 text-[#00539F] font-black px-3 py-1 rounded-lg text-xs shadow-sm group-hover:border-[#00539F] transition-all">
                                            +£{FEATURES_MAP[id].price.toFixed(2)}
                                        </Badge>
                                    </div>
                                ))}
                            </div>

                            <div className="flex gap-4 pt-4">
                                <Button onClick={prevStep} variant="outline" className="h-16 px-8 rounded-2xl font-black border-gray-200">{t('Back')}</Button>
                                <Button onClick={nextStep} className="flex-1 bg-[#00539F] hover:bg-[#004380] text-white rounded-2xl h-16 text-xl font-black shadow-lg transition-all active:scale-[0.98]">
                                    {t('Finish & View Summary')} <ChevronRight className="ml-2 h-6 w-6" />
                                </Button>
                            </div>
                        </div>
                    )}

                    {/* STEP 7: FINAL SUMMARY (IMG 35-43) - FINAL BREAKDOWN */}
                    {step === 7 && (
                        <div className="space-y-8 animate-in fade-in slide-in-from-bottom-4 duration-500">
                            <h2 className="text-3xl font-black text-gray-900">{t('Your final quote summary')}</h2>

                            <div className="bg-[#00539F] rounded-[40px] p-12 text-white shadow-2xl space-y-10 relative overflow-hidden">
                                <div className="absolute -top-24 -right-24 h-64 w-64 bg-white/5 rounded-full blur-3xl" />
                                <div className="absolute -bottom-24 -left-24 h-64 w-64 bg-blue-400/10 rounded-full blur-3xl" />

                                <div className="flex flex-col md:flex-row justify-between items-start md:items-center bg-white/10 rounded-[30px] p-8 backdrop-blur-md gap-8">
                                    <div className="space-y-2">
                                        <p className="font-black text-blue-200 text-xs uppercase tracking-[0.2em]">{t('Monthly Premium')}</p>
                                        <p className="text-6xl font-black flex items-start">
                                            <span className="text-3xl mt-2">£</span>
                                            {(parseFloat(calculateTotalPremium(selectedPolicy, selectedServices)) / 12).toFixed(2)}
                                        </p>
                                    </div>
                                    <div className="h-px w-full md:h-16 md:w-px bg-white/20" />
                                    <div className="space-y-4">
                                        <div>
                                            <p className="font-black text-blue-200 text-[10px] uppercase tracking-widest mb-1">{t('Quote Reference')}</p>
                                            <p className="text-2xl font-black">#TNS-{Math.random().toString(36).substr(2, 6).toUpperCase()}</p>
                                        </div>
                                        <div className="flex items-center gap-2 text-blue-200 font-bold text-sm">
                                            <Calendar className="h-4 w-4" />
                                            <span>{t('Starts')} {new Date(startDate).toLocaleDateString()}</span>
                                        </div>
                                    </div>
                                </div>

                                <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
                                    <div className="bg-white/5 rounded-[25px] p-6 backdrop-blur-sm border border-white/10">
                                        <p className="font-black text-blue-200 text-[10px] uppercase tracking-widest mb-2">{t('Cover Type')}</p>
                                        <p className="text-lg font-black">{coverLevel} {t('Comprehensive')}</p>
                                    </div>
                                    <div className="bg-white/5 rounded-[25px] p-6 backdrop-blur-sm border border-white/10">
                                        <p className="font-black text-blue-200 text-[10px] uppercase tracking-widest mb-2">{t('Main Excess')}</p>
                                        <p className="text-lg font-black">£200.00</p>
                                    </div>
                                    <div className="bg-white/5 rounded-[25px] p-6 backdrop-blur-sm border border-white/10">
                                        <p className="font-black text-blue-200 text-[10px] uppercase tracking-widest mb-2">{t('Included extras')}</p>
                                        <p className="text-lg font-black">{selectedServices.length} {t('Selected')}</p>
                                    </div>
                                </div>
                            </div>

                            <Card className="rounded-[40px] border border-gray-100 overflow-hidden shadow-xl">
                                <div className="p-8 border-b border-gray-100">
                                    <h3 className="text-lg font-black text-gray-900">{t('Detailed Excess Breakdown')}</h3>
                                </div>
                                <Table>
                                    <TableBody>
                                        {[
                                            { label: 'Accidental Damage', price: '£200.00', type: 'Compulsory' },
                                            { label: 'Fire & Theft', price: '£200.00', type: 'Compulsory' },
                                            { label: 'Theft of Keys', price: '£75.00', type: 'Basic' },
                                            { label: 'Replacement Locks', price: '£150.00', type: 'Basic' }
                                        ].map((item) => (
                                            <TableRow key={item.label} className="border-gray-50 hover:bg-gray-50/50">
                                                <TableCell className="pl-8 py-5">
                                                    <div className="flex flex-col">
                                                        <span className="font-black text-gray-800">{item.label}</span>
                                                        <span className="text-[10px] uppercase font-black tracking-widest text-gray-400">{t(item.type)}</span>
                                                    </div>
                                                </TableCell>
                                                <TableCell className="font-black text-gray-900 pr-8 text-right text-lg">{item.price}</TableCell>
                                            </TableRow>
                                        ))}
                                    </TableBody>
                                </Table>
                            </Card>

                            <div className="flex gap-4 pt-4">
                                <Button onClick={prevStep} variant="outline" className="h-16 px-8 rounded-2xl font-black border-gray-200" disabled={isSubmitting}>{t('Back')}</Button>
                                <Button
                                    onClick={handleSubmit}
                                    disabled={isSubmitting}
                                    className="flex-1 bg-green-600 hover:bg-green-700 text-white rounded-2xl h-16 text-2xl font-black shadow-xl transition-all active:scale-[0.98] flex items-center justify-center gap-3"
                                >
                                    {isSubmitting ? (
                                        <>
                                            <Clock className="h-6 w-6 animate-spin" />
                                            {t('Finishing...')}
                                        </>
                                    ) : (
                                        <>
                                            <PlusCircle className="h-6 w-6" />
                                            {t('Confirm & Save Quote')}
                                        </>
                                    )}
                                </Button>
                            </div>
                        </div>
                    )}
                </CardContent>
            </Card>

            {/* Footer Notice */}
            <div className="flex items-center gap-3 justify-center text-gray-400 font-bold uppercase text-[10px] tracking-widest">
                <ShieldCheck className="h-4 w-4" />
                <span>{t('Your data is encrypted and secure with Tinsur.AI')}</span>
            </div>
        </div>
    );
}
