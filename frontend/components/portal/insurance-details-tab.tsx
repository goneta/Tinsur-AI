'use client';

import React, { useState, useEffect, useCallback } from 'react';
import { Card } from '@/components/ui/card';
import { useLanguage } from '@/contexts/language-context';
import { Button } from '@/components/ui/button';
import {
    LayoutGrid, List, Plus, User, Car, Phone,
    CreditCard, Calendar, Briefcase,
    XCircle, Info, Camera, Calculator,
    ShieldCheck, Edit3, ChevronRight, FileText, Download,
    Check, AlertTriangle
} from 'lucide-react';
import { QuoteCreationWizard } from './quote-creation-wizard';
import { UniversalEntityCard } from '@/components/shared/universal-entity-card';
import { PolicyCard } from '@/components/shared/policy-card';
import { getCompanySettings } from "@/lib/settings-api";
import { ClientDriver, ClientAutomobile } from '@/types/client';
import { Quote as BackendQuote } from '@/types/quote';
import { Policy as BackendPolicy } from '@/types/policy';
import { Claim as BackendClaim } from '@/types/claim';
import { Payment as BackendPayment } from '@/types/payment';
import { policyApi } from "@/lib/policy-api";
import { clientApi } from "@/lib/client-api";
import { useToast } from "@/components/ui/use-toast";
import { quoteApi } from '@/lib/quote-api';
import { claimApi } from '@/lib/claim-api';
import { paymentApi } from '@/lib/payment-api';
import { UnifiedEntityForm } from '@/components/shared/unified-entity-form';
import { VehicleDetailsTable } from './vehicle-details-table';

import {
    Dialog,
    DialogTrigger,
} from "@/components/ui/dialog";
import {
    Table,
    TableBody,
    TableCell,
    TableHead,
    TableHeader,
    TableRow,
} from "@/components/ui/table";
import { Badge } from "@/components/ui/badge";

export interface PortalDriver {
    id: string;
    fullName: string;
    firstName?: string;
    lastName?: string;
    phoneNumber: string;
    address: string;
    city?: string;
    postalCode?: string;
    country?: string;
    licenseNumber: string;
    licenseIssueDate: string;
    employmentStatus: string;
    maritalStatus: string;
    numberOfChildren: number;
    photoUrl: string;
    dateOfBirth: string;
    clientId?: string;
    licenseType?: string;
    carsInHousehold?: number;
    residentialStatus?: string;
    accidentCount?: number;
    noClaimsYears?: number;
    drivingLicenseYears?: number;
    drivingLicenseUrl?: string;
}

export interface PortalVehicle {
    id: string;
    make: string;
    model: string;
    mileage: string;
    colour: string;
    modified: boolean;
    dateAcquired: string;
    registrationNumber: string;
    vehicleType: 'Manual' | 'Automatic';
    usage: 'Domestic' | 'For Work' | 'Taxi' | 'Delivery';
    dateOfPurchase: string;
    vehicleAge: string;
    parkedLocation: string;
    imageUrl?: string;
}

export interface PortalQuote {
    id: string;
    vehicle: PortalVehicle;
    reference: string;
    coverLevel: string;
    coverType: string;
    basePremium: string;
    premium: string;
    expiresAt: string;
    drivers: string[];
    usage: string;
    status: string;
    included_services: string[];
    created_at?: string;
}

export interface PortalPolicy {
    id: string;
    policyNumber: string;
    status: string;
    activeDate: string;
    premium: string;
    coverLevel: string;
    vehicle: PortalVehicle;
    included_services: string[];
}

export interface PortalClaim {
    id: string;
    reference: string;
    type: string;
    date: string;
    vehicle: string;
    amount: string;
    status: 'Settled' | 'Pending' | 'Rejected' | string;
    policyId: string;
}

export interface PortalPayment {
    id: string;
    date: string;
    amount: string;
    method: string;
    status: 'Paid' | 'Pending' | string;
    type: string;
    policyId: string;
}

export type Driver = PortalDriver;
export type Vehicle = PortalVehicle;

const MOCK_DRIVERS: PortalDriver[] = [
    {
        id: '1',
        fullName: 'Kenneth Cisse',
        phoneNumber: '+44 7700 900000',
        address: '123 Insurance Way, London, E1 6AN',
        licenseNumber: 'CISSE825255KC99',
        licenseIssueDate: '2015-05-20',
        employmentStatus: 'Employed',
        maritalStatus: 'Married',
        numberOfChildren: 2,
        photoUrl: 'https://api.dicebear.com/7.x/avataaars/svg?seed=Kenneth',
        dateOfBirth: '1990-05-15'
    }
];

const MOCK_VEHICLES: PortalVehicle[] = [
    {
        id: '1',
        make: 'KIA',
        model: 'CEE\'D 2 CRDI (126)',
        mileage: '45,000',
        colour: 'Silver',
        modified: false,
        dateAcquired: '2023-01-15',
        registrationNumber: 'LG13MWC',
        vehicleType: 'Manual',
        usage: 'Domestic',
        dateOfPurchase: '2013-03-25',
        vehicleAge: '11 years',
        parkedLocation: 'Driveway',
        imageUrl: 'https://images.unsplash.com/photo-1541899481282-d53bffe3c35d?auto=format&fit=crop&q=80&w=400'
    }
];

export interface InsuranceDetailsTabProps {
    initialDrivers?: PortalDriver[];
    initialVehicles?: PortalVehicle[];
    initialQuotes?: PortalQuote[];
    initialPolicies?: PortalPolicy[];
    initialClaims?: PortalClaim[];
    initialPayments?: PortalPayment[];
    clientId?: string;
    isAdmin?: boolean;
}

export function InsuranceDetailsTab({
    initialDrivers,
    initialVehicles,
    initialQuotes,
    initialPolicies,
    initialClaims,
    initialPayments,
    clientId,
    isAdmin = false
}: InsuranceDetailsTabProps) {
    const { language, t } = useLanguage();
    const [viewMode, setViewMode] = useState<'list' | 'card'>('card');
    const [activeSection, setActiveSection] = useState<'drivers' | 'vehicles' | 'quotes' | 'policies' | 'claims' | 'payments' | 'documents'>('drivers');

    // Use initial data if provided, otherwise fallback to mocks ONLY if not admin (or handle empty)
    // Actually, for Admin we want to show real data, so fallback to empty array if initial is undefined but we are in admin mode?
    // Let's keep mocks for dev/portal if not provided, but prioritize initial.
    // Use initial data if provided, otherwise empty. Mocks should not be used in production flows to avoid ID conflicts.
    const [drivers, setDrivers] = useState<PortalDriver[]>(initialDrivers || []);
    const [vehicles, setVehicles] = useState<PortalVehicle[]>(initialVehicles || []);
    const [isEditingVehicle, setIsEditingVehicle] = useState(false);
    const [editingVehicle, setEditingVehicle] = useState<PortalVehicle | null>(null);
    const [quoteWizardOpen, setQuoteWizardOpen] = useState(false);
    const [selectedVehicleForQuote, setSelectedVehicleForQuote] = useState<PortalVehicle | null>(null);
    const [isEditing, setIsEditing] = useState(false);
    const [editingDriver, setEditingDriver] = useState<PortalDriver | null>(null);
    const [isAddingDriver, setIsAddingDriver] = useState(false);
    const [isAddingVehicle, setIsAddingVehicle] = useState(false);
    const { toast } = useToast();
    const [isAddDialogOpen, setIsAddDialogOpen] = useState(false);


    // Form States
    const handleAddVehicle = async () => {
        setIsAddingVehicle(true);
        setEditingVehicle(null);
        setActiveSection('vehicles');
    };
    const [expandedQuotes, setExpandedQuotes] = useState<Record<string, boolean>>({});
    const [selectedQuoteServices, setSelectedQuoteServices] = useState<Record<string, string[]>>({});

    const toggleQuoteService = (quoteId: string, serviceId: string) => {
        setSelectedQuoteServices(prev => {
            const quote = quotes.find(q => q.id === quoteId);
            const current = prev[quoteId] !== undefined ? prev[quoteId] : (quote?.included_services || []);

            const updated = current.includes(serviceId)
                ? current.filter((id: string) => id !== serviceId)
                : [...current, serviceId];
            return { ...prev, [quoteId]: updated };
        });
    };

    const [companySettings, setCompanySettings] = useState<{ government_tax_percent: number; admin_fee: number } | null>(null);

    React.useEffect(() => {
        const loadSettings = async () => {
            try {
                const settings = await getCompanySettings();
                setCompanySettings({
                    government_tax_percent: settings.government_tax_percent || 0,
                    admin_fee: Number(settings.admin_fee || 0)
                });
            } catch (error) {
                console.error("Failed to load company settings:", error);
            }
        };
        loadSettings();
    }, []);

    const calculateBreakdown = (basePremium: string, quoteId: string) => {
        const base = parseFloat(basePremium.replace('£', ''));
        const quote = quotes.find(q => q.id === quoteId);
        const currentServices = selectedQuoteServices[quoteId] !== undefined
            ? selectedQuoteServices[quoteId]
            : (quote?.included_services || []);

        const additional = currentServices.reduce((acc: number, id: string) => {
            return acc + (FEATURES_MAP[id]?.price || 0);
        }, 0);

        const subtotal = base + additional;
        const adminFee = companySettings?.admin_fee || 0;
        const taxPercent = companySettings?.government_tax_percent || 0;
        const taxAmount = (subtotal * taxPercent) / 100;
        const total = subtotal + adminFee + taxAmount;

        return {
            subtotal,
            adminFee,
            taxPercent,
            taxAmount,
            total
        };
    };

    const toggleQuoteFeatures = (id: string) => {
        setExpandedQuotes(prev => ({ ...prev, [id]: !prev[id] }));
    };

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

    // Realistic Mock Data for UI demonstration
    const [quotes, setQuotes] = useState<PortalQuote[]>(initialQuotes || [
        {
            id: 'q1',
            vehicle: MOCK_VEHICLES[0],
            reference: 'Q-7A2B4C',
            coverLevel: 'Silver',
            coverType: 'Comprehensive',
            basePremium: '£189.00',
            premium: '£189.00',
            expiresAt: '2026-02-10',
            drivers: ['Kenneth Cisse'],
            usage: 'Social, Domestic & Pleasure',
            status: 'approved',
            included_services: ['comprehensive', 'small_courtesy', 'windscreen', 'eu_cover']
        }
    ]);

    const [policies, setPolicies] = useState<PortalPolicy[]>(initialPolicies || [
        {
            id: 'p1',
            vehicle: MOCK_VEHICLES[0],
            policyNumber: 'TNS-8829-XJ',
            coverLevel: 'Gold',
            activeDate: '2025-06-12',
            status: 'active',
            premium: '£245.00',
            included_services: ['comprehensive', 'small_courtesy', 'upgraded_courtesy', 'eu_cover', 'windscreen', 'uninsured_driver', 'loss_keys', 'claims_portal', 'personal_accident', 'personal_belongings', 'mfr_audio', 'audio_equip', 'driving_other', 'car_seats', 'theft_keys', 'new_car_replace', 'misfuelling', 'onward_travel', 'vandalism', 'hotel_expenses']
        }
    ]);

    const [claims, setClaims] = useState<PortalClaim[]>(initialClaims || [
        {
            id: 'c1',
            reference: 'CLM-992834',
            date: '2025-08-15',
            policyId: 'TNS-8829-XJ',
            vehicle: 'TOYOTA COROLLA',
            type: 'Accident',
            status: 'Pending',
            amount: '£1,250.00'
        },
        {
            id: 'c2',
            reference: 'CLM-771209',
            date: '2025-02-10',
            policyId: 'TNS-8829-XJ',
            vehicle: 'TOYOTA COROLLA',
            type: 'Windscreen',
            status: 'Settled',
            amount: '£450.00'
        }
    ]);

    const [payments, setPayments] = useState<PortalPayment[]>(initialPayments || [
        {
            id: 'pay1',
            date: '2025-12-01',
            policyId: 'TNS-8829-XJ',
            amount: '£245.00',
            method: 'Visa **** 4421',
            status: 'Paid',
            type: 'Policy Activation'
        },
        {
            id: 'pay2',
            date: '2025-11-01',
            policyId: 'TNS-8829-XJ',
            amount: '£20.50',
            method: 'Direct Debit',
            status: 'Paid',
            type: 'Monthly Installment'
        }
    ]);

    const refreshData = useCallback(async () => {
        if (!clientId) return;
        try {
            const [qs, ps, cs, pays, clientData] = await Promise.all([
                quoteApi.getQuotes({ client_id: clientId }),
                policyApi.getPolicies({ client_id: clientId }),
                claimApi.getClaims({ client_id: clientId }),
                paymentApi.getPayments({ client_id: clientId, page: 1, page_size: 100 }),
                clientApi.getClient(clientId)
            ]);

            const fetchedVehicles: PortalVehicle[] = (clientData.automobile_details || []).map((v: ClientAutomobile) => ({
                id: v.id,
                make: v.vehicle_make || 'Unknown',
                model: v.vehicle_model || 'Unknown',
                registrationNumber: v.vehicle_registration || 'N/A',
                mileage: v.vehicle_mileage?.toString() || '0',
                transmission: v.engine_capacity_cc ? 'Manual' : 'Automatic',
                usage: (v.vehicle_usage as PortalVehicle['usage']) || 'Domestic',
                dateOfPurchase: v.created_at?.split('T')[0] || '',
                parkedLocation: 'Driveway',
                colour: v.vehicle_color || 'Unknown',
                vehicleType: 'Manual',
                vehicleAge: 'N/A',
                modified: false,
                imageUrl: (v as Record<string, unknown>).vehicle_image_url as string || 'https://images.unsplash.com/photo-1541899481282-d53bffe3c35d?auto=format&fit=crop&q=80&w=400'
            }));

            const fetchedDrivers: PortalDriver[] = (clientData.drivers || []).map((d: ClientDriver) => ({
                id: d.id,
                fullName: `${d.first_name || ''} ${d.last_name || ''}`.trim(),
                firstName: d.first_name,
                lastName: d.last_name,
                phoneNumber: d.phone_number,
                address: d.address,
                city: d.city,
                postalCode: d.postal_code,
                country: d.country,
                licenseNumber: d.license_number,
                licenseIssueDate: d.license_issue_date,
                employmentStatus: d.employment_status,
                maritalStatus: d.marital_status,
                numberOfChildren: d.number_of_children,
                photoUrl: d.photo_url || `https://api.dicebear.com/7.x/avataaars/svg?seed=${d.id}`,
                dateOfBirth: '', // Need DOB handling if available
                clientId: d.client_id,
                licenseType: d.license_type,
                carsInHousehold: d.cars_in_household,
                residentialStatus: d.residential_status,
                accidentCount: d.accident_count,
                noClaimsYears: d.no_claims_years,
                drivingLicenseYears: d.driving_license_years,
                drivingLicenseUrl: d.driving_license_url
            }));

            setVehicles(fetchedVehicles);
            setDrivers(fetchedDrivers);

            // Map Quotes
            setQuotes(qs.quotes.map((q: BackendQuote) => ({
                id: q.id,
                vehicle: fetchedVehicles.find((v: PortalVehicle) => v.id === (q.details?.vehicle_id || '')) || fetchedVehicles[0] || MOCK_VEHICLES[0],
                reference: q.quote_number,
                coverLevel: q.details?.cover_level || 'Standard',
                coverType: 'Comprehensive',
                basePremium: `£${q.final_premium}`,
                premium: `£${q.final_premium}`,
                expiresAt: new Date(new Date(q.created_at).setMonth(new Date(q.created_at).getMonth() + 3)).toISOString().split('T')[0],
                drivers: fetchedDrivers.length > 0 ? [fetchedDrivers[0].fullName] : ['Main Driver'],
                usage: 'Social, Domestic & Pleasure',
                status: q.status,
                included_services: (q.details?.selected_services as string[]) || ['comprehensive']
            })));

            // Map Policies
            setPolicies(ps.policies.map((p: BackendPolicy) => ({
                id: p.id,
                vehicle: fetchedVehicles.find((v: PortalVehicle) => v.id === (p.details?.vehicle_id || '')) || fetchedVehicles[0] || MOCK_VEHICLES[0],
                policyNumber: p.policy_number,
                coverLevel: ((p.details as Record<string, unknown>)?.cover_level as string) || 'Gold',
                activeDate: p.start_date.split('T')[0],
                status: p.status,
                premium: `£${p.premium_amount || 0}`,
                included_services: ((p.details as Record<string, unknown>)?.selected_services as string[]) || ['comprehensive', 'windscreen']
            })));

            // Map Claims
            setClaims(cs.filter((c: BackendClaim) => c.client_id === clientId).map((c: BackendClaim) => ({
                id: c.id,
                reference: c.claim_number,
                date: c.incident_date.split('T')[0],
                policyId: c.policy_id,
                vehicle: fetchedVehicles[0]?.make + ' ' + fetchedVehicles[0]?.model || 'Unknown Vehicle',
                type: 'Accident',
                status: c.status,
                amount: `£${c.claim_amount}`
            })));

            // Map Payments
            setPayments(pays.payments.map((p: BackendPayment) => ({
                id: p.id,
                date: p.created_at.split('T')[0],
                policyId: p.policy_id,
                amount: `£${p.amount}`,
                method: p.payment_method,
                status: p.status,
                type: 'Premium'
            })));

        } catch (error) {
            console.error('Failed to poll background updates:', error);
        }
    }, [clientId]);

    // Polling for updates
    useEffect(() => {
        // eslint-disable-next-line react-hooks/set-state-in-effect
        refreshData();
        const refreshInterval = setInterval(refreshData, 10000); // Polling every 10 seconds
        return () => clearInterval(refreshInterval);
    }, [refreshData]);

    // Documents State
    const [policyDocuments, setPolicyDocuments] = useState<Record<string, string[]>>({});
    const [expandedDocs, setExpandedDocs] = useState<Record<string, boolean>>({});

    const handleViewDocuments = async (policyId: string) => {
        setSelectedPolicyForDocuments(policyId);

        if (!policyDocuments[policyId]) {
            try {
                // Fetch documents if not loaded
                const docs = await policyApi.getPolicyDocuments(policyId);
                setPolicyDocuments(prev => ({ ...prev, [policyId]: docs }));
            } catch (error) {
                console.error("Failed to fetch documents", error);
            }
        }
        setExpandedDocs(prev => ({ ...prev, [policyId]: true }));
        setActiveSection('documents');
    };

    const toggleDocSection = async (policyId: string) => {
        const isExpanding = !expandedDocs[policyId];

        if (isExpanding && !policyDocuments[policyId]) {
            try {
                const docs = await policyApi.getPolicyDocuments(policyId);
                setPolicyDocuments(prev => ({ ...prev, [policyId]: docs }));
            } catch (error) {
                console.error("Failed to fetch documents", error);
            }
        }

        setExpandedDocs(prev => ({ ...prev, [policyId]: isExpanding }));
    };

    const handleEditDetails = (driver: PortalDriver) => {
        setEditingDriver(driver);
        setIsEditing(true);
    };

    const handleEditVehicleDetails = (vehicle: PortalVehicle) => {
        setEditingVehicle(vehicle);
        setIsEditingVehicle(true);
    };

    const handleDriverPhotoChange = (id: string, file: File) => {
        const imageUrl = URL.createObjectURL(file);
        setDrivers(prev => prev.map(d => d.id === id ? { ...d, photoUrl: imageUrl } : d));
    };

    const handleVehicleImageChange = (id: string, file: File) => {
        const imageUrl = URL.createObjectURL(file);
        setVehicles(prev => prev.map(v => v.id === id ? { ...v, imageUrl } : v));
    };

    const handleCreateQuote = (vehicle: PortalVehicle) => {
        setSelectedVehicleForQuote(vehicle);
        setQuoteWizardOpen(true);
    };

    const handleQuoteSuccess = (newQuote: PortalQuote) => {
        setQuotes(prev => [...prev, newQuote]);
        setQuoteWizardOpen(false);
        setActiveSection('quotes');
        setSelectedVehicleForQuote(null);
    };

    const handleApproveQuote = async (quote: PortalQuote) => {
        try {
            toast({ title: "Activating Policy...", description: "Please wait while we generate your policy documents." });
            const result = await quoteApi.approveQuote(quote.id);

            const newPolicy = {
                ...quote,
                id: result.policy_id || quote.id,
                policyNumber: result.policy_number || 'PENDING',
                status: 'active',
                activeDate: new Date().toISOString().split('T')[0],
                validUntil: new Date(new Date().setFullYear(new Date().getFullYear() + 1)).toISOString().split('T')[0] // Default 1 year if missing
            };

            setPolicies(prev => [...prev, newPolicy]);
            // Remove from quotes list (optional, but logical)
            setQuotes(prev => prev.filter(q => q.id !== quote.id));

            toast({ title: "Values Updated", description: "Policy activated successfully!" });
            setActiveSection('policies');
        } catch (error: unknown) {
            console.error("Approval error:", error);
            const message = error instanceof Error ? (error as { response?: { data?: { detail?: string } } }).response?.data?.detail : "Failed to activate policy. Please contact support.";
            toast({
                title: "Activation Failed",
                description: message || "Failed to activate policy. Please contact support.",
                variant: "destructive"
            });
        }
    };

    return (
        <div className="space-y-8 animate-in fade-in duration-500">
            <div className="flex flex-col md:flex-row md:items-center justify-between gap-6">
                <div className="flex items-center gap-2 bg-gray-100 p-1 rounded-2xl w-fit">
                    <button
                        onClick={() => setActiveSection('drivers')}
                        className={`flex items-center gap-2 px-6 py-3 rounded-xl font-bold transition-all ${activeSection === 'drivers' ? 'bg-white text-[#00539F] shadow-sm' : 'text-gray-500 hover:text-gray-700'}`}
                    >
                        <User className="h-5 w-5" />
                        {t('Drivers')}
                    </button>
                    <button
                        onClick={() => setActiveSection('vehicles')}
                        className={`flex items-center gap-2 px-6 py-3 rounded-xl font-bold transition-all ${activeSection === 'vehicles' ? 'bg-white text-[#00539F] shadow-sm' : 'text-gray-500 hover:text-gray-700'}`}
                    >
                        <Car className="h-5 w-5" />
                        {t('Vehicles')}
                    </button>
                    <button
                        onClick={() => setActiveSection('quotes')}
                        className={`flex items-center gap-2 px-6 py-3 rounded-xl font-bold transition-all ${activeSection === 'quotes' ? 'bg-white text-[#00539F] shadow-sm' : 'text-gray-500 hover:text-gray-700'}`}
                    >
                        <Calculator className="h-5 w-5" />
                        {t('Quotes')}
                    </button>
                    <button
                        onClick={() => setActiveSection('policies')}
                        className={`flex items-center gap-2 px-6 py-3 rounded-xl font-bold transition-all ${activeSection === 'policies' ? 'bg-white text-[#00539F] shadow-sm' : 'text-gray-500 hover:text-gray-700'}`}
                    >
                        <ShieldCheck className="h-5 w-5" />
                        {t('Insurance Policies')}
                    </button>
                    <button
                        onClick={() => setActiveSection('claims')}
                        className={`flex items-center gap-2 px-6 py-3 rounded-xl font-bold transition-all ${activeSection === 'claims' ? 'bg-white text-[#00539F] shadow-sm' : 'text-gray-500 hover:text-gray-700'}`}
                    >
                        <XCircle className="h-5 w-5" />
                        {t('Claims')}
                    </button>
                    <button
                        onClick={() => setActiveSection('payments')}
                        className={`flex items-center gap-2 px-6 py-3 rounded-xl font-bold transition-all ${activeSection === 'payments' ? 'bg-white text-[#00539F] shadow-sm' : 'text-gray-500 hover:text-gray-700'}`}
                    >
                        <CreditCard className="h-5 w-5" />
                        {t('Payments')}
                    </button>
                    <button
                        onClick={() => setActiveSection('documents')}
                        className={`flex items-center gap-2 px-6 py-3 rounded-xl font-bold transition-all ${activeSection === 'documents' ? 'bg-white text-[#00539F] shadow-sm' : 'text-gray-500 hover:text-gray-700'}`}
                    >
                        <FileText className="h-5 w-5" />
                        {t('Documents')}
                    </button>
                </div>

                <div className="flex items-center gap-4">
                    <div className="flex items-center gap-1 bg-gray-100 p-1 rounded-xl">
                        <button
                            onClick={() => setViewMode('card')}
                            className={`p-2 rounded-lg transition-all ${viewMode === 'card' ? 'bg-white text-[#00539F] shadow-sm' : 'text-gray-400'}`}
                        >
                            <LayoutGrid className="h-5 w-5" />
                        </button>
                        <button
                            onClick={() => setViewMode('list')}
                            className={`p-2 rounded-lg transition-all ${viewMode === 'list' ? 'bg-white text-[#00539F] shadow-sm' : 'text-gray-400'}`}
                        >
                            <List className="h-5 w-5" />
                        </button>
                    </div>

                    <div className="flex items-center gap-2">
                        {(activeSection === 'vehicles' || activeSection === 'quotes' || activeSection === 'policies') && !isAddingVehicle && !isEditingVehicle && (
                            activeSection === 'vehicles' ? (
                                <Button
                                    onClick={handleAddVehicle}
                                    className="bg-[#00539F] hover:bg-[#004380] text-white rounded-xl px-6 font-bold flex items-center gap-2"
                                >
                                    <Plus className="h-5 w-5" />
                                    {t('Add Vehicle')}
                                </Button>
                            ) : (
                                <Dialog open={isAddDialogOpen} onOpenChange={setIsAddDialogOpen}>
                                    <DialogTrigger asChild>
                                        <Button className="bg-[#00539F] hover:bg-[#004380] text-white rounded-xl px-6 font-bold flex items-center gap-2">
                                            <Plus className="h-5 w-5" />
                                            {activeSection === 'quotes' ? t('New Quote') : t('New Policy')}
                                        </Button>
                                    </DialogTrigger>
                                </Dialog>
                            )
                        )}
                        {activeSection === 'drivers' && !isAddingDriver && !isEditing && (
                            <Button
                                onClick={() => setIsAddingDriver(true)}
                                className="bg-[#00539F] hover:bg-[#004380] text-white rounded-xl px-6 font-bold flex items-center gap-2"
                            >
                                <Plus className="h-5 w-5" />
                                {t('Add Driver')}
                            </Button>
                        )}
                    </div>
                </div>
            </div>

            {
                quoteWizardOpen && selectedVehicleForQuote ? (
                    <QuoteCreationWizard
                        open={quoteWizardOpen}
                        onOpenChange={(open) => {
                            setQuoteWizardOpen(open);
                            if (!open) setSelectedVehicleForQuote(null);
                        }}
                        vehicle={selectedVehicleForQuote}
                        drivers={drivers}
                        onSuccess={handleQuoteSuccess}
                        clientId={clientId}
                        isAdmin={isAdmin}
                    />
                ) : (isAddingDriver || (isEditing && editingDriver)) ? (
                    <UnifiedEntityForm
                        type="driver"
                        clientId={clientId || ''}
                        mode={isAddingDriver ? 'create' : 'edit'}
                        entity={isAddingDriver ? {} : {
                            ...editingDriver,
                            id: editingDriver!.id,
                            first_name: editingDriver!.firstName,
                            last_name: editingDriver!.lastName,
                            phone_number: editingDriver!.phoneNumber,
                            postal_code: editingDriver!.postalCode,
                            license_number: editingDriver!.licenseNumber,
                            license_issue_date: editingDriver!.licenseIssueDate,
                            employment_status: editingDriver!.employmentStatus,
                            marital_status: editingDriver!.maritalStatus,
                            number_of_children: editingDriver!.numberOfChildren,
                            photo_url: editingDriver!.photoUrl,
                            license_type: editingDriver!.licenseType,
                            cars_in_household: editingDriver!.carsInHousehold,
                            residential_status: editingDriver!.residentialStatus,
                            accident_count: editingDriver!.accidentCount,
                            no_claims_years: editingDriver!.noClaimsYears,
                            driving_license_years: editingDriver!.drivingLicenseYears,
                            driving_license_url: editingDriver!.drivingLicenseUrl,
                            date_of_birth: editingDriver!.dateOfBirth
                        }}
                        onUpdate={() => {
                            refreshData();
                            setIsAddingDriver(false);
                            setIsEditing(false);
                            setEditingDriver(null);
                        }}
                        onBack={() => {
                            setIsAddingDriver(false);
                            setIsEditing(false);
                            setEditingDriver(null);
                        }}
                    />
                ) : (isAddingVehicle || (isEditingVehicle && editingVehicle)) ? (
                    <VehicleDetailsTable
                        clientId={clientId || ''}
                        mode={isAddingVehicle ? 'create' : 'edit'}
                        vehicle={isAddingVehicle ? {} : {
                            ...editingVehicle,
                            id: editingVehicle.id,
                            vehicle_registration: editingVehicle.registrationNumber,
                            vehicle_make: editingVehicle.make,
                            vehicle_model: editingVehicle.model,
                            vehicle_year: Number(editingVehicle.vehicleAge.replace(/\D/g, '')) ? new Date().getFullYear() - Number(editingVehicle.vehicleAge.replace(/\D/g, '')) : undefined,
                            vehicle_value: undefined,
                            vehicle_mileage: Number(editingVehicle.mileage.replace(/\D/g, '')),
                            fuel_type: undefined,
                            vehicle_usage: editingVehicle.usage,
                            engine_capacity_cc: undefined,
                            seat_count: undefined,
                            vehicle_color: editingVehicle.colour,
                            parked_location: editingVehicle.parkedLocation,
                            vehicle_image_url: editingVehicle.imageUrl
                        }}
                        onUpdate={() => {
                            refreshData();
                            setIsAddingVehicle(false);
                            setIsEditingVehicle(false);
                            setEditingVehicle(null);
                        }}
                        onBack={() => {
                            setIsAddingVehicle(false);
                            setIsEditingVehicle(false);
                            setEditingVehicle(null);
                        }}
                    />
                ) : (
                    <>
                        {activeSection === 'drivers' && (
                            viewMode === 'card' ? (
                                <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-8">
                                    {drivers.map((driver) => (
                                        <Card key={driver.id} className="rounded-[30px] overflow-hidden border border-gray-100 shadow-xl hover:shadow-2xl transition-all group">
                                            <div className="p-8 space-y-6">
                                                <div className="flex items-center gap-6">
                                                    <div className="relative group/avatar cursor-pointer">
                                                        <div className="h-20 w-20 rounded-2xl overflow-hidden bg-blue-50 flex-shrink-0 border-2 border-[#00539F]/10 transition-opacity group-hover/avatar:opacity-80">
                                                            {/* eslint-disable-next-line @next/next/no-img-element */}
                                                            <img src={driver.photoUrl} alt={driver.fullName} className="w-full h-full object-cover" />
                                                        </div>
                                                        <label
                                                            htmlFor={`driver-upload-${driver.id}`}
                                                            className="absolute inset-0 flex items-center justify-center bg-black/40 rounded-2xl opacity-0 group-hover/avatar:opacity-100 transition-opacity cursor-pointer"
                                                        >
                                                            <Camera className="text-white h-6 w-6" />
                                                        </label>
                                                        <input
                                                            id={`driver-upload-${driver.id}`}
                                                            type="file"
                                                            accept="image/*"
                                                            className="hidden"
                                                            onChange={(e) => {
                                                                const file = e.target.files?.[0];
                                                                if (file) handleDriverPhotoChange(driver.id, file);
                                                            }}
                                                        />
                                                    </div>
                                                    <div>
                                                        <h4 className="text-xl font-black text-gray-900 group-hover:text-[#00539F] transition-colors">{driver.fullName}</h4>
                                                        <p className="text-gray-400 font-bold uppercase text-[10px] tracking-widest mt-1">Driving License</p>
                                                        <p className="text-black font-black text-sm">{driver.licenseNumber}</p>
                                                    </div>
                                                </div>
                                                <div className="flex gap-3">
                                                    <Button
                                                        variant="outline"
                                                        onClick={() => handleEditDetails(driver)}
                                                        className="flex-1 rounded-xl border-gray-200 hover:bg-gray-50 font-bold text-gray-700 h-11 transition-all active:scale-95"
                                                    >
                                                        <Edit3 className="h-4 w-4 mr-2" />
                                                        Edit details
                                                    </Button>
                                                </div>
                                                <div className="pt-4 border-t border-gray-100 flex items-center justify-between">
                                                    <div className="flex items-center gap-2 text-gray-500">
                                                        <Phone className="h-4 w-4" />
                                                        <span className="text-sm font-bold">{driver.phoneNumber}</span>
                                                    </div>
                                                    <Badge className="bg-green-100 text-green-700 hover:bg-green-100 border-none px-3 py-1 font-black text-[10px] uppercase">Validated</Badge>
                                                </div>
                                            </div>
                                        </Card>
                                    ))}
                                </div>
                            ) : (
                                <div className="bg-white rounded-[30px] border border-gray-100 shadow-xl overflow-hidden overflow-x-auto">
                                    <Table>
                                        <TableHeader>
                                            <TableRow className="bg-gray-50/50">
                                                <TableHead className="font-black text-black pl-8">Name</TableHead>
                                                <TableHead className="font-black text-black">Contact</TableHead>
                                                <TableHead className="font-black text-black">License</TableHead>
                                                <TableHead className="font-black text-black">Status</TableHead>
                                                <TableHead className="font-black text-black">Children</TableHead>
                                                <TableHead className="font-black text-black">License Issue</TableHead>
                                            </TableRow>
                                        </TableHeader>
                                        <TableBody>
                                            {drivers.map((driver) => (
                                                <TableRow key={driver.id} className="hover:bg-gray-50/50">
                                                    <TableCell className="font-bold pl-8 py-6">{driver.fullName}</TableCell>
                                                    <TableCell className="font-bold py-6">
                                                        <div className="flex flex-col">
                                                            <span>{driver.phoneNumber}</span>
                                                            <span className="text-xs text-gray-400 font-medium line-clamp-1">{driver.address}</span>
                                                        </div>
                                                    </TableCell>
                                                    <TableCell className="font-mono font-bold text-[#00539F] py-6">{driver.licenseNumber}</TableCell>
                                                    <TableCell className="font-bold py-6">{driver.employmentStatus} / {driver.maritalStatus}</TableCell>
                                                    <TableCell className="font-bold py-6 text-center">{driver.numberOfChildren}</TableCell>
                                                    <TableCell className="font-bold py-6">{driver.licenseIssueDate}</TableCell>
                                                </TableRow>
                                            ))}
                                        </TableBody>
                                    </Table>
                                </div>
                            )
                        )}

                        {activeSection === 'vehicles' && (
                            viewMode === 'card' ? (
                                <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-8">
                                    {vehicles.map((vehicle) => (
                                        <Card key={vehicle.id} className="rounded-[30px] overflow-hidden border border-gray-100 shadow-xl hover:shadow-2xl transition-all group">
                                            <div className="h-48 overflow-hidden relative group/vehicle cursor-pointer">
                                                {/* eslint-disable-next-line @next/next/no-img-element */}
                                                <img src={vehicle.imageUrl} alt={vehicle.make} className="w-full h-full object-cover group-hover/vehicle:scale-110 transition-transform duration-500" />
                                                <label
                                                    htmlFor={`vehicle-upload-${vehicle.id}`}
                                                    className="absolute inset-0 flex items-center justify-center bg-black/40 opacity-0 group-hover/vehicle:opacity-100 transition-opacity cursor-pointer"
                                                >
                                                    <div className="flex flex-col items-center gap-2">
                                                        <Camera className="text-white h-8 w-8" />
                                                        <span className="text-white text-xs font-bold uppercase tracking-widest">Change Image</span>
                                                    </div>
                                                </label>
                                                <input
                                                    id={`vehicle-upload-${vehicle.id}`}
                                                    type="file"
                                                    accept="image/*"
                                                    className="hidden"
                                                    onChange={(e) => {
                                                        const file = e.target.files?.[0];
                                                        if (file) handleVehicleImageChange(vehicle.id, file);
                                                    }}
                                                />
                                                <div className="absolute top-4 right-4 bg-white/90 backdrop-blur px-3 py-1.5 rounded-xl border border-gray-200 shadow-sm z-10">
                                                    <p className="font-mono font-black text-xs text-black tracking-widest">{vehicle.registrationNumber}</p>
                                                </div>
                                            </div>
                                            <div className="p-8 space-y-6">
                                                <div>
                                                    <h4 className="text-xl font-black text-gray-900">{vehicle.make} {vehicle.model}</h4>
                                                    <div className="flex items-center gap-4 mt-3">
                                                        <div className="flex items-center gap-1.5 text-gray-500">
                                                            <Info className="h-4 w-4" />
                                                            <span className="text-xs font-bold">{vehicle.vehicleType}</span>
                                                        </div>
                                                        <span className="text-gray-300">•</span>
                                                        <div className="flex items-center gap-1.5 text-gray-500">
                                                            <Briefcase className="h-4 w-4" />
                                                            <span className="text-xs font-bold">{vehicle.usage} Use</span>
                                                        </div>
                                                    </div>
                                                </div>
                                                <div className="pt-4 border-t border-gray-100 flex flex-col gap-4">
                                                    <div className="flex items-center justify-between">
                                                        <div className="flex items-center gap-2">
                                                            <span className="h-2 w-2 rounded-full bg-blue-500 animate-pulse"></span>
                                                            <span className="text-sm font-bold text-gray-500">{vehicle.mileage} miles</span>
                                                        </div>
                                                        <Badge className="bg-blue-50 text-[#00539F] hover:bg-blue-50 border-none px-3 py-1 font-black text-[10px] uppercase">{vehicle.colour}</Badge>
                                                    </div>
                                                    <div className="flex gap-2">
                                                        <Button
                                                            variant="outline"
                                                            size="sm"
                                                            onClick={() => handleEditVehicleDetails(vehicle)}
                                                            className="flex-1 rounded-xl border-gray-200 hover:bg-gray-50 font-bold text-gray-700 h-9 transition-all active:scale-95 text-[10px] px-1"
                                                        >
                                                            <Edit3 className="h-3 w-3 mr-1" />
                                                            Edit details
                                                        </Button>
                                                        <Button
                                                            size="sm"
                                                            className="flex-1 bg-[#00539F] hover:bg-[#004380] text-white rounded-xl font-bold h-9 transition-all shadow-lg active:scale-95 text-[10px] px-1"
                                                            onClick={() => handleCreateQuote(vehicle)}
                                                        >
                                                            <Calculator className="h-3 w-3 mr-1" />
                                                            Create quote
                                                        </Button>
                                                    </div>
                                                </div>
                                            </div>
                                        </Card>
                                    ))}
                                </div>
                            ) : (
                                <div className="bg-white rounded-[30px] border border-gray-100 shadow-xl overflow-hidden overflow-x-auto">
                                    <Table>
                                        <TableHeader>
                                            <TableRow className="bg-gray-50/50">
                                                <TableHead className="font-black text-black pl-8">Vehicle</TableHead>
                                                <TableHead className="font-black text-black">Registration</TableHead>
                                                <TableHead className="font-black text-black">Transmission</TableHead>
                                                <TableHead className="font-black text-black">usage</TableHead>
                                                <TableHead className="font-black text-black">Mileage</TableHead>
                                                <TableHead className="font-black text-black">Details</TableHead>
                                                <TableHead className="font-black text-black pr-8">Parked</TableHead>
                                            </TableRow>
                                        </TableHeader>
                                        <TableBody>
                                            {vehicles.map((vehicle) => (
                                                <TableRow key={vehicle.id} className="hover:bg-gray-50/50">
                                                    <TableCell className="font-bold pl-8 py-6">
                                                        <div className="flex flex-col">
                                                            <span>{vehicle.make} {vehicle.model}</span>
                                                            <span className="text-xs text-gray-400 font-medium">Purchased: {vehicle.dateOfPurchase} ({vehicle.vehicleAge})</span>
                                                        </div>
                                                    </TableCell>
                                                    <TableCell className="font-mono font-bold text-black py-6">
                                                        <span className="bg-gray-100 px-3 py-1.5 rounded-lg border border-gray-200">{vehicle.registrationNumber}</span>
                                                    </TableCell>
                                                    <TableCell className="font-bold py-6">{vehicle.vehicleType}</TableCell>
                                                    <TableCell className="font-bold py-6">{vehicle.usage}</TableCell>
                                                    <TableCell className="font-bold py-6">{vehicle.mileage}</TableCell>
                                                    <TableCell className="font-bold py-6">
                                                        <div className="flex flex-col gap-1">
                                                            <Badge variant="outline" className="w-fit text-[10px] font-bold py-0">{vehicle.colour}</Badge>
                                                            {vehicle.modified && <Badge className="bg-yellow-100 text-yellow-700 border-none w-fit text-[10px] font-bold py-0">MODIFIED</Badge>}
                                                        </div>
                                                    </TableCell>
                                                    <TableCell className="font-bold py-6 pr-8">{vehicle.parkedLocation}</TableCell>
                                                </TableRow>
                                            ))}
                                        </TableBody>
                                    </Table>
                                </div>
                            )
                        )}

                        {activeSection === 'quotes' && (
                            <div className="space-y-6">
                                {quotes.length === 0 ? (
                                    <Card className="rounded-[30px] p-12 text-center border-dashed border-2 border-gray-200">
                                        <div className="mx-auto h-16 w-16 bg-gray-50 rounded-2xl flex items-center justify-center mb-6">
                                            <Calculator className="h-8 w-8 text-gray-300" />
                                        </div>
                                        <h3 className="text-xl font-black text-gray-900 mb-2">No quotes yet</h3>
                                        <p className="text-gray-500 font-medium mb-8">Create a new quote from the Vehicle Details tab to see it here.</p>
                                        <Button
                                            onClick={() => setActiveSection('vehicles')}
                                            className="bg-[#00539F] text-white rounded-xl font-bold"
                                        >
                                            View Vehicles
                                        </Button>
                                    </Card>
                                ) : (
                                    <div className="grid grid-cols-1 lg:grid-cols-2 gap-10">
                                        {quotes.map((quote) => {
                                            const breakdown = calculateBreakdown(quote.basePremium || quote.premium, quote.id);

                                            // Map services to items format
                                            const allServices = (expandedQuotes[quote.id] ? Object.keys(FEATURES_MAP) : (quote.included_services || []));
                                            const items = allServices.map((serviceId: string) => ({
                                                id: serviceId,
                                                label: FEATURES_MAP[serviceId]?.[language] || FEATURES_MAP[serviceId]?.en || serviceId,
                                                price: FEATURES_MAP[serviceId]?.price,
                                                checked: (selectedQuoteServices[quote.id] !== undefined ? selectedQuoteServices[quote.id] : (quote.included_services || [])).includes(serviceId),
                                                onCheckedChange: () => {
                                                    if (quote.status === 'draft') { // Only allow editing if draft (simplified logic)
                                                        toggleQuoteService(quote.id, serviceId)
                                                    }
                                                },
                                                disabled: quote.status !== 'draft' // Disable check if not draft
                                            }));

                                            // Financials
                                            const financials = [
                                                { label: t('quote.admin_fee', 'Company Admin Fee'), amount: `£${breakdown.adminFee.toFixed(2)}` },
                                                { label: `${t('quote.tax', 'Govt Tax')} (${breakdown.taxPercent}%)`, amount: `£${breakdown.taxAmount.toFixed(2)}` },
                                                { label: 'Total Premium', amount: `£${breakdown.total.toFixed(2)}`, isTotal: true }
                                            ];

                                            // Actions
                                            const actions = (
                                                <div className="flex gap-2 w-full">
                                                    {quote.status === 'approved' && (
                                                        <Button
                                                            onClick={() => handleApproveQuote(quote)}
                                                            className="flex-1 bg-green-600 hover:bg-green-700 text-white font-bold rounded-xl"
                                                        >
                                                            <Check className="h-4 w-4 mr-2" />
                                                            Activate Policy
                                                        </Button>
                                                    )}
                                                    {/* Add other actions like Edit/Delete if needed */}
                                                </div>
                                            );

                                            return (
                                                <UniversalEntityCard
                                                    key={quote.id}
                                                    header={{
                                                        title: `${quote.vehicle.make} ${quote.vehicle.model}`,
                                                        subtitle: `Quote #${quote.reference}`,
                                                        status: quote.status,
                                                        icon: ShieldCheck,
                                                        badgeText: `Tinsur.AI ${quote.coverLevel}`
                                                    }}
                                                    items={items}
                                                    financials={financials}
                                                    footer={{
                                                        validUntil: quote.expiresAt,
                                                        createdAt: quote.created_at ? new Date(quote.created_at).toLocaleDateString() : 'Today'
                                                    }}
                                                    actions={actions}
                                                    onToggleExpand={() => toggleQuoteFeatures(quote.id)}
                                                    isExpanded={expandedQuotes[quote.id]}
                                                />
                                            );
                                        })}
                                    </div>
                                )}
                            </div>
                        )}

                        {activeSection === 'documents' && (
                            <div className="space-y-6">
                                <div className="flex justify-between items-center mb-6">
                                    <div>
                                        <h2 className="text-2xl font-black text-gray-900">Documents</h2>
                                        <p className="text-gray-500 font-medium">Access and download your insurance documents.</p>
                                    </div>
                                </div>

                                {policies.length === 0 ? (
                                    <Card className="p-8 text-center text-gray-500 border-dashed border-2">
                                        No active policies found.
                                    </Card>
                                ) : (
                                    <div className="space-y-4">
                                        {policies.map(policy => (
                                            <Card key={policy.id} className="overflow-hidden border border-gray-100 shadow-sm rounded-2xl">
                                                <div
                                                    className="p-6 flex items-center justify-between cursor-pointer hover:bg-gray-50 transition-colors"
                                                    onClick={() => toggleDocSection(policy.id)}
                                                >
                                                    <div className="flex items-center gap-4">
                                                        <div className="h-10 w-10 bg-blue-50 rounded-xl flex items-center justify-center">
                                                            <FileText className="h-5 w-5 text-[#00539F]" />
                                                        </div>
                                                        <div>
                                                            <h4 className="font-black text-gray-900">{policy.vehicle.make} {policy.vehicle.model}</h4>
                                                            <p className="text-xs text-gray-500 font-bold tracking-wide">POLICY: {policy.policyNumber}</p>
                                                        </div>
                                                    </div>
                                                    <ChevronRight className={`h-5 w-5 text-gray-400 transform transition-transform ${expandedDocs[policy.id] ? 'rotate-90' : ''}`} />
                                                </div>

                                                {expandedDocs[policy.id] && (
                                                    <div className="bg-gray-50 px-6 py-4 border-t border-gray-100 space-y-3">
                                                        {policyDocuments[policy.id]?.length > 0 ? (
                                                            policyDocuments[policy.id].map((docPath, index) => {
                                                                const fileName = docPath.split('/').pop() || 'Document';
                                                                const cleanName = fileName.replace('.html', '').replace(/_[^_]+$/, '').replace(/_/g, ' ');
                                                                // Logic to clean filename: remove extension, remove policy suffix if needed
                                                                // Current format: Name_Template_PolicyNum.html

                                                                const downloadUrl = `/api/v1/documents/policy/${policy.id}/${fileName}`;

                                                                return (
                                                                    <div key={index} className="flex items-center justify-between bg-white p-4 rounded-xl border border-gray-200 shadow-sm hover:shadow-md transition-all">
                                                                        <div className="flex items-center gap-3">
                                                                            <div className="h-8 w-8 bg-red-50 rounded-lg flex items-center justify-center">
                                                                                <FileText className="h-4 w-4 text-red-500" />
                                                                            </div>
                                                                            <span className="font-bold text-gray-700 text-sm">{cleanName}</span>
                                                                        </div>
                                                                        <a
                                                                            href={downloadUrl}
                                                                            target="_blank"
                                                                            rel="noopener noreferrer"
                                                                            className="flex items-center gap-2 text-[#00539F] font-black text-xs hover:underline bg-blue-50 px-3 py-2 rounded-lg"
                                                                        >
                                                                            <Download className="h-3 w-3" /> Download
                                                                        </a>
                                                                    </div>
                                                                );
                                                            })
                                                        ) : (
                                                            <p className="text-gray-500 text-sm italic py-2">No documents generated yet.</p>
                                                        )}
                                                    </div>
                                                )}
                                            </Card>
                                        ))}
                                    </div>
                                )}
                            </div>
                        )}

                        {activeSection === 'policies' && (
                            <div className="space-y-6">
                                {policies.length === 0 ? (
                                    <Card className="rounded-[30px] p-12 text-center border-dashed border-2 border-gray-200">
                                        <div className="mx-auto h-16 w-16 bg-gray-50 rounded-2xl flex items-center justify-center mb-6">
                                            <ShieldCheck className="h-8 w-8 text-gray-300" />
                                        </div>
                                        <h3 className="text-xl font-black text-gray-900 mb-2">No active policies</h3>
                                        <p className="text-gray-500 font-medium mb-8">Approve a quote to convert it into a full insurance policy.</p>
                                    </Card>
                                ) : (
                                    <div className="grid grid-cols-1 lg:grid-cols-2 gap-10">
                                        {policies.map((policy) => {
                                            // Map services
                                            const allServices = (policy.included_services || []);

                                            const features = allServices.map((serviceId: string) => ({
                                                id: serviceId,
                                                label: FEATURES_MAP[serviceId]?.[language] || FEATURES_MAP[serviceId]?.en || serviceId,
                                                included: (policy.included_services || []).includes(serviceId)
                                            }));

                                            const policyData = {
                                                id: policy.id,
                                                vehicleName: `${policy.vehicle.make} ${policy.vehicle.model}`,
                                                registrationNumber: policy.vehicle.registrationNumber,
                                                policyNumber: policy.policyNumber,
                                                status: policy.status,
                                                activeDate: policy.activeDate,
                                                premium: policy.premium,
                                                coverLevel: policy.coverLevel,
                                                features: features
                                            };

                                            return (
                                                <PolicyCard
                                                    key={policy.id}
                                                    policy={policyData}
                                                    onViewDocuments={() => handleViewDocuments(policy.id)}
                                                    onMakeClaim={() => setActiveSection('claims')}
                                                    onMakePayment={() => setActiveSection('payments')}
                                                />
                                            );
                                        })}
                                    </div>
                                )}
                            </div>
                        )}

                        {activeSection === 'claims' && (
                            <div className="space-y-6">
                                {viewMode === 'card' ? (
                                    <div className="grid grid-cols-1 lg:grid-cols-2 gap-10">
                                        {claims.map((claim) => (
                                            <UniversalEntityCard
                                                key={claim.id}
                                                header={{
                                                    title: claim.type || 'Claim',
                                                    subtitle: `Ref: ${claim.reference}`,
                                                    status: claim.status,
                                                    icon: AlertTriangle,
                                                    badgeText: claim.date
                                                }}
                                                items={[
                                                    { id: 'veh', label: `Vehicle: ${claim.vehicle}`, checked: true, disabled: true },
                                                    { id: 'pol', label: `Policy: ${claim.policyId}`, checked: true, disabled: true }
                                                ]}
                                                financials={[
                                                    { label: 'Claim Amount', amount: claim.amount, isTotal: true }
                                                ]}
                                                footer={{
                                                    validUntil: claim.date,
                                                    createdAt: claim.date
                                                }}
                                                actions={
                                                    <Button variant="outline" className="w-full rounded-xl font-bold">View Details</Button>
                                                }
                                            />
                                        ))}
                                        {claims.length === 0 && <div className="col-span-full text-center py-10 text-gray-500 font-bold">No claims found.</div>}
                                    </div>
                                ) : (
                                    <Card className="rounded-[40px] overflow-hidden border-none shadow-xl bg-white">
                                        <div className="p-8 border-b border-gray-100 flex justify-between items-center">
                                            <div>
                                                <h3 className="text-2xl font-black text-gray-900">Your Claims History</h3>
                                                <p className="text-gray-500 font-bold">Manage and track your active and past claims.</p>
                                            </div>
                                            <div className="flex gap-2">
                                                <Badge variant="outline" className="rounded-lg h-10 px-4 font-bold border-gray-200">Active (1)</Badge>
                                                <Badge variant="outline" className="rounded-lg h-10 px-4 font-bold border-gray-200 text-gray-400">Past (1)</Badge>
                                            </div>
                                        </div>
                                        <div className="overflow-x-auto">
                                            <Table>
                                                <TableHeader className="bg-gray-50/50">
                                                    <TableRow className="border-none">
                                                        <TableHead className="font-black text-[10px] uppercase tracking-widest text-gray-400 py-6 pl-8">Reference</TableHead>
                                                        <TableHead className="font-black text-[10px] uppercase tracking-widest text-gray-400 py-6">Date</TableHead>
                                                        <TableHead className="font-black text-[10px] uppercase tracking-widest text-gray-400 py-6">Policy / Vehicle</TableHead>
                                                        <TableHead className="font-black text-[10px] uppercase tracking-widest text-gray-400 py-6 text-center">Status</TableHead>
                                                        <TableHead className="font-black text-[10px] uppercase tracking-widest text-gray-400 py-6 text-right pr-8">Amount</TableHead>
                                                    </TableRow>
                                                </TableHeader>
                                                <TableBody>
                                                    {claims.map((claim) => (
                                                        <TableRow key={claim.id} className="group hover:bg-gray-50/50 transition-colors border-gray-50">
                                                            <TableCell className="py-6 pl-8">
                                                                <span className="font-black text-gray-900">#{claim.reference}</span>
                                                            </TableCell>
                                                            <TableCell className="py-6">
                                                                <div className="flex items-center gap-2 text-gray-500 font-bold text-sm">
                                                                    <Calendar className="h-4 w-4" />
                                                                    {claim.date}
                                                                </div>
                                                            </TableCell>
                                                            <TableCell className="py-6">
                                                                <div className="space-y-0.5">
                                                                    <p className="font-black text-sm text-gray-900">{claim.vehicle}</p>
                                                                    <p className="text-[10px] font-bold text-gray-400 tracking-wider">REF: {claim.policyId}</p>
                                                                </div>
                                                            </TableCell>
                                                            <TableCell className="py-6 text-center">
                                                                <Badge
                                                                    className={`font-black text-[10px] px-3 py-1 rounded-lg border-none ${claim.status === 'Settled' ? 'bg-green-50 text-green-600' :
                                                                        claim.status === 'Pending' ? 'bg-orange-50 text-orange-600' :
                                                                            'bg-red-50 text-red-600'
                                                                        }`}
                                                                >
                                                                    {claim.status.toUpperCase()}
                                                                </Badge>
                                                            </TableCell>
                                                            <TableCell className="py-6 text-right pr-8 font-black text-gray-900">
                                                                {claim.amount}
                                                            </TableCell>
                                                        </TableRow>
                                                    ))}
                                                </TableBody>
                                            </Table>
                                        </div>
                                    </Card>
                                )}
                            </div>
                        )}

                        {activeSection === 'payments' && (
                            <div className="space-y-6">
                                {viewMode === 'card' ? (
                                    <div className="grid grid-cols-1 lg:grid-cols-2 gap-10">
                                        {payments.map((payment) => (
                                            <UniversalEntityCard
                                                key={payment.id}
                                                header={{
                                                    title: payment.type || 'Payment',
                                                    subtitle: `Method: ${payment.method}`,
                                                    status: payment.status,
                                                    icon: CreditCard,
                                                    badgeText: payment.date
                                                }}
                                                items={[]}
                                                financials={[
                                                    { label: 'Amount Paid', amount: payment.amount, isTotal: true }
                                                ]}
                                                footer={{
                                                    validUntil: payment.date,
                                                    createdAt: payment.date
                                                }}
                                                actions={
                                                    <Button variant="outline" className="w-full rounded-xl font-bold">Download Receipt</Button>
                                                }
                                            />
                                        ))}
                                        {payments.length === 0 && <div className="col-span-full text-center py-10 text-gray-500 font-bold">No payments found.</div>}
                                    </div>
                                ) : (
                                    <Card className="rounded-[40px] overflow-hidden border-none shadow-xl bg-white">
                                        <div className="p-8 border-b border-gray-100 flex justify-between items-center">
                                            <div>
                                                <h3 className="text-2xl font-black text-gray-900">Payment History</h3>
                                                <p className="text-gray-500 font-bold">Your recent transactions and upcoming payments.</p>
                                            </div>
                                            <Button variant="default" className="bg-[#00539F] hover:bg-[#004380] rounded-xl font-black h-12 px-6">
                                                Download Statement
                                            </Button>
                                        </div>
                                        <div className="overflow-x-auto">
                                            <Table>
                                                <TableHeader className="bg-gray-50/50">
                                                    <TableRow className="border-none">
                                                        <TableHead className="font-black text-[10px] uppercase tracking-widest text-gray-400 py-6 pl-8">Date</TableHead>
                                                        <TableHead className="font-black text-[10px] uppercase tracking-widest text-gray-400 py-6">Transaction Type</TableHead>
                                                        <TableHead className="font-black text-[10px] uppercase tracking-widest text-gray-400 py-6">Payment Method</TableHead>
                                                        <TableHead className="font-black text-[10px] uppercase tracking-widest text-gray-400 py-6 text-center">Status</TableHead>
                                                        <TableHead className="font-black text-[10px] uppercase tracking-widest text-gray-400 py-6 text-right pr-8">Amount</TableHead>
                                                    </TableRow>
                                                </TableHeader>
                                                <TableBody>
                                                    {payments.map((payment) => (
                                                        <TableRow key={payment.id} className="group hover:bg-gray-50/50 transition-colors border-gray-50">
                                                            <TableCell className="py-6 pl-8">
                                                                <div className="font-black text-gray-900">{payment.date}</div>
                                                            </TableCell>
                                                            <TableCell className="py-6">
                                                                <div className="space-y-0.5">
                                                                    <p className="font-black text-sm text-gray-900">{payment.type}</p>
                                                                    <p className="text-[10px] font-bold text-gray-400 tracking-wider font-mono">{payment.policyId}</p>
                                                                </div>
                                                            </TableCell>
                                                            <TableCell className="py-6">
                                                                <div className="flex items-center gap-2 text-gray-700 font-bold text-sm">
                                                                    <CreditCard className="h-4 w-4 text-gray-400" />
                                                                    {payment.method}
                                                                </div>
                                                            </TableCell>
                                                            <TableCell className="py-6 text-center">
                                                                <div className="flex items-center justify-center gap-1.5 text-green-600 font-black text-[10px]">
                                                                    <div className="h-1.5 w-1.5 rounded-full bg-green-500 shadow-[0_0_8px_rgba(34,197,94,0.6)]" />
                                                                    {payment.status.toUpperCase()}
                                                                </div>
                                                            </TableCell>
                                                            <TableCell className="py-6 text-right pr-8 font-black text-[#00539F]">
                                                                {payment.amount}
                                                            </TableCell>
                                                        </TableRow>
                                                    ))}
                                                </TableBody>
                                            </Table>
                                        </div>
                                    </Card>
                                )}
                            </div>
                        )}
                    </>
                )}

            <div className="bg-blue-50 rounded-[30px] p-8 border border-blue-100 flex flex-col md:flex-row items-center gap-8 mt-8">
                <div className="h-16 w-16 bg-white rounded-2xl flex items-center justify-center flex-shrink-0 shadow-sm">
                    <Info className="h-8 w-8 text-[#00539F]" />
                </div>
                <div>
                    <h5 className="text-lg font-black text-[#002B52]">Need to make temporary changes?</h5>
                    <p className="text-[#00539F] font-bold">Adding a temporary driver or updating your usage for a short period? Our support team can assist you with immediate adjustments.</p>
                </div>
                <Button variant="outline" className="md:ml-auto rounded-xl border-[#00539F] text-[#00539F] hover:bg-blue-100 font-black px-8 h-12">
                    Contact Agent
                </Button>
            </div>
        </div>
    );
}
