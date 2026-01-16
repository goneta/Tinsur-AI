'use client';

import { useEffect, useState, use } from 'react';
import { useRouter } from 'next/navigation';
import { clientApi } from '@/lib/client-api';
import { Client } from '@/types/client';
import { Button } from '@/components/ui/button';
import { ArrowLeft, Edit, Save, Plus, Camera, Car, Upload } from 'lucide-react';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { Separator } from '@/components/ui/separator';
import { useToast } from '@/components/ui/use-toast';
import { Badge } from '@/components/ui/badge';
import { ProfileUploader } from '@/components/shared/profile-uploader';
import { IdVerificationCard } from '@/components/clients/id-verification-card';

import { quoteApi } from '@/lib/quote-api';
import { policyApi } from '@/lib/policy-api';
import { claimApi } from '@/lib/claim-api';
import { paymentApi } from '@/lib/payment-api';
import { InsuranceDetailsTab, PortalDriver as Driver, PortalVehicle } from '@/components/portal/insurance-details-tab';

// ... (keep existing imports, remove unused ones later if strictly needed, but verify first)

import { useLanguage } from '@/contexts/language-context';

export default function ClientDetailPage({ params }: { params: Promise<{ id: string }> }) {
    const router = useRouter();
    const resolvedParams = use(params);
    const { t } = useLanguage();
    const { toast } = useToast();
    const [client, setClient] = useState<Client | null>(null);
    const [loading, setLoading] = useState(true);
    const [quotes, setQuotes] = useState<any[]>([]);
    const [policies, setPolicies] = useState<any[]>([]);
    const [claims, setClaims] = useState<any[]>([]);
    const [payments, setPayments] = useState<any[]>([]);
    // Map Client Data to Portal Data Structures
    const mapClientToDrivers = (c: Client): Driver[] => {
        if (c.drivers && Array.isArray(c.drivers) && c.drivers.length > 0) {
            return c.drivers.map(d => ({
                id: d.id,
                firstName: d.first_name,
                lastName: d.last_name,
                fullName: `${d.last_name} ${d.first_name}`,
                phoneNumber: d.phone_number,
                address: d.address,
                city: d.city,
                country: d.country,
                licenseNumber: d.license_number,
                licenseIssueDate: d.license_issue_date ? new Date(d.license_issue_date).toISOString().split('T')[0] : '',
                employmentStatus: d.employment_status,
                maritalStatus: d.marital_status,
                numberOfChildren: d.number_of_children,
                photoUrl: d.photo_url || `https://api.dicebear.com/7.x/avataaars/svg?seed=${d.last_name}`,
                dateOfBirth: '' // TODO: Map real DOB if available in backend
            }));
        }

        // Fallback for primary lead data if no explicit drivers yet
        return [{
            id: c.id,
            firstName: c.first_name,
            lastName: c.last_name,
            fullName: c.client_type === 'individual' ? `${c.last_name} ${c.first_name}` : c.business_name || 'Business',
            phoneNumber: c.phone || '',
            address: c.address || '',
            city: c.city || '',
            country: c.country || '',
            licenseNumber: c.driving_licence_number || 'PENDING',
            licenseIssueDate: '',
            employmentStatus: c.employment_status || '',
            maritalStatus: c.marital_status || '',
            numberOfChildren: c.life_details?.dependent_count || 0,
            numberOfChildren: c.life_details?.dependent_count || 0,
            photoUrl: c.profile_picture || `https://api.dicebear.com/7.x/avataaars/svg?seed=${c.first_name}`,
            dateOfBirth: c.date_of_birth ? new Date(c.date_of_birth).toISOString().split('T')[0] : ''
        }];
    };

    const mapClientToVehicles = (c: Client): PortalVehicle[] => {
        if (!c.automobile_details || !Array.isArray(c.automobile_details) || c.automobile_details.length === 0) return [];

        return c.automobile_details.map(auto => ({
            id: auto.id || 'v1',
            make: auto.vehicle_make || 'Unknown',
            model: auto.vehicle_model || 'Unknown',
            mileage: auto.vehicle_mileage ? `${auto.vehicle_mileage}` : '0',
            colour: auto.vehicle_color || 'Unknown',
            modified: false,
            dateAcquired: auto.created_at ? auto.created_at.split('T')[0] : '2020-01-01',
            registrationNumber: auto.vehicle_registration || '',
            vehicleType: (auto.fuel_type === 'Automatic' ? 'Automatic' : 'Manual') as any,
            usage: (auto.vehicle_usage as any) || 'Domestic',
            dateOfPurchase: auto.created_at ? auto.created_at.split('T')[0] : '2020-01-01',
            vehicleAge: auto.vehicle_year ? `${new Date().getFullYear() - auto.vehicle_year} years` : 'Unknown',
            parkedLocation: 'Driveway',
            imageUrl: 'https://images.unsplash.com/photo-1541899481282-d53bffe3c35d?auto=format&fit=crop&q=80&w=400'
        }));
    };

    useEffect(() => {
        loadClient();
    }, [resolvedParams.id]);

    const loadClient = async () => {
        try {
            const data = await clientApi.getClient(resolvedParams.id);
            setClient(data);

            const clientVehicles = mapClientToVehicles(data);
            const defaultVehicle = clientVehicles[0] || { make: 'Unknown', model: 'Unknown', registrationNumber: 'Unknown' };

            const [qs, ps, cs, pays] = await Promise.all([
                quoteApi.getQuotes({ client_id: resolvedParams.id }),
                policyApi.getPolicies({ client_id: resolvedParams.id }),
                claimApi.getClaims({ client_id: resolvedParams.id }), // params updated in lib
                paymentApi.getPayments({ client_id: resolvedParams.id, page: 1, page_size: 100 })
            ]);

            // Map Quotes
            setQuotes(qs.quotes.map(q => ({
                id: q.id,
                vehicle: clientVehicles.find(v => v.id === (q.details?.vehicle_id || '')) || defaultVehicle,
                reference: q.quote_number,
                coverLevel: 'Standard', // TODO: Map from policy_type
                coverType: 'Comprehensive',
                basePremium: `£${q.final_premium}`,
                premium: `£${q.final_premium}`,
                expiresAt: new Date(new Date(q.created_at).setMonth(new Date(q.created_at).getMonth() + 1)).toISOString().split('T')[0], // Mock expiry
                drivers: [`${data.first_name} ${data.last_name}`],
                usage: 'Social, Domestic & Pleasure',
                status: q.status,
                included_services: ['comprehensive'] // Mock
            })));

            // Map Policies
            setPolicies(ps.policies.map(p => ({
                id: p.id,
                vehicle: clientVehicles.find(v => v.id === (p.details?.vehicle_id || '')) || defaultVehicle,
                policyNumber: p.policy_number,
                coverLevel: 'Gold', // Mock
                coverType: 'Comprehensive',
                activeDate: p.start_date.split('T')[0],
                status: p.status,
                premium: `£${p.premium_amount || 0}`,
                included_services: ['comprehensive', 'windscreen'] // Mock
            })));

            // Map Claims
            setClaims(cs.filter(c => c.client_id === resolvedParams.id).map(c => ({
                id: c.id,
                reference: c.claim_number,
                date: c.incident_date.split('T')[0],
                policyId: c.policy_id, // TODO: map to policy number if needed
                vehicle: defaultVehicle.make + ' ' + defaultVehicle.model, // Simple vehicle string
                type: 'Accident', // Mock or map from incident_description
                status: c.status,
                amount: `£${c.claim_amount}`
            })));

            // Map Payments
            setPayments(pays.payments.map(p => ({
                id: p.id,
                date: p.created_at.split('T')[0], // Use created_at if payment_date not in type
                policyId: p.policy_id,
                amount: `£${p.amount}`,
                method: p.payment_method,
                status: p.status,
                type: 'Premium'
            })));

        } catch (error) {
            console.error('Failed to load client data:', error);
            toast({
                title: t('Error'),
                description: t('Failed to load client details'),
                variant: 'destructive',
            });
        } finally {
            setLoading(false);
        }
    };

    const handleProfilePictureUpload = async (path: string) => {
        if (!client) return;
        setClient({ ...client, profile_picture: path });
    };

    if (loading) return <div className="p-8">{t('Loading...')}</div>;
    if (!client) return <div className="p-8">{t('Client not found')}</div>;





    return (
        <div className="space-y-6 p-8 pt-6 bg-gray-50/50 min-h-screen">
            <div className="flex items-center justify-between">
                <div className="flex items-center space-x-4">
                    <Button variant="ghost" size="icon" onClick={() => router.back()} className="rounded-xl hover:bg-white">
                        <ArrowLeft className="h-5 w-5 text-gray-500" />
                    </Button>
                    <div className="flex items-center gap-4">
                        <ProfileUploader
                            entityId={client.id}
                            entityType="client"
                            currentImageUrl={client.profile_picture}
                            name={client.client_type === 'individual' ? `${client.first_name} ${client.last_name}` : client.business_name || ''}
                            size="lg"
                            onUploadSuccess={loadClient}
                            className="border-4 border-white shadow-lg"
                        />
                        <div>
                            <h2 className="text-3xl font-black tracking-tight text-gray-900">
                                {client.client_type === 'individual' ? `${client.last_name} ${client.first_name}` : client.business_name}
                            </h2>
                            <div className="flex items-center gap-2 mt-2">
                                <Badge variant="outline" className="rounded-lg px-2 py-1 uppercase text-[10px] font-bold tracking-widest bg-white">{client.client_type}</Badge>
                                <Badge className={`rounded-lg px-2 py-1 uppercase text-[10px] font-bold tracking-widest border-none ${client.kyc_status === 'verified' ? 'bg-green-100 text-green-700' : 'bg-amber-100 text-amber-700'}`}>
                                    {t('KYC')}: {client.kyc_status}
                                </Badge>
                                <span className="text-xs text-gray-400 font-bold ml-2">{t('ID')}: {client.id.split('-')[0]}...</span>
                            </div>
                        </div>
                    </div>
                </div>
                {/* 
                <Button>Edit Profile</Button> 
                Maybe add some top-level actions here later
                */}
            </div>

            <Separator className="bg-gray-200" />

            {/* Reusing Portal Component directly */}
            <InsuranceDetailsTab
                initialDrivers={mapClientToDrivers(client)}
                initialVehicles={mapClientToVehicles(client)}
                initialQuotes={quotes}
                initialPolicies={policies}
                initialClaims={claims}
                initialPayments={payments}
                clientId={client.id}
                isAdmin={true}
            />
        </div>
    );
}
