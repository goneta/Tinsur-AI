'use client';

import { useEffect, useState } from 'react';
import { InsuranceDetailsTab, Driver, Vehicle as PortalVehicle } from '@/components/portal/insurance-details-tab';
import { clientApi } from '@/lib/client-api';
import { policyApi } from '@/lib/policy-api';
import { quoteApi } from '@/lib/quote-api';
import { claimApi } from '@/lib/claim-api';
import { paymentApi } from '@/lib/payment-api';
import { Client } from '@/types/client';

export default function InsuranceDetailsPage() {
    const [loading, setLoading] = useState(true);
    const [client, setClient] = useState<Client | null>(null);
    const [drivers, setDrivers] = useState<Driver[]>([]);
    const [vehicles, setVehicles] = useState<PortalVehicle[]>([]);
    const [quotes, setQuotes] = useState<any[]>([]);
    const [policies, setPolicies] = useState<any[]>([]);
    const [claims, setClaims] = useState<any[]>([]);
    const [payments, setPayments] = useState<any[]>([]);

    useEffect(() => {
        const loadData = async () => {
            try {
                const clientData = await clientApi.getMyClient();
                setClient(clientData);

                // Map Drivers
                if (clientData.drivers && clientData.drivers.length > 0) {
                    setDrivers(clientData.drivers.map(d => ({
                        id: d.id,
                        fullName: d.full_name,
                        phoneNumber: d.phone_number,
                        address: d.address,
                        licenseNumber: d.license_number,
                        licenseIssueDate: d.license_issue_date,
                        employmentStatus: d.employment_status,
                        maritalStatus: d.marital_status,
                        numberOfChildren: d.number_of_children,
                        photoUrl: d.photo_url || `https://api.dicebear.com/7.x/avataaars/svg?seed=${d.full_name}`
                    })));
                } else {
                    // Fallback to basic user info if no explicit drivers
                    setDrivers([{
                        id: clientData.id,
                        fullName: `${clientData.first_name} ${clientData.last_name}`,
                        phoneNumber: clientData.phone,
                        address: clientData.address || '',
                        licenseNumber: clientData.driving_licence_number || 'PENDING',
                        licenseIssueDate: '',
                        employmentStatus: clientData.employment_status || '',
                        maritalStatus: clientData.marital_status || '',
                        numberOfChildren: 0,
                        photoUrl: clientData.profile_picture || `https://api.dicebear.com/7.x/avataaars/svg?seed=${clientData.first_name}`
                    }]);
                }

                // Map Vehicles
                let portalVehicles: PortalVehicle[] = [];
                if (clientData.automobile_details && clientData.automobile_details.length > 0) {
                    portalVehicles = clientData.automobile_details.map(auto => ({
                        id: auto.id,
                        make: auto.vehicle_make || 'Unknown',
                        model: auto.vehicle_model || 'Unknown',
                        mileage: `${auto.vehicle_mileage || 0}`,
                        colour: auto.vehicle_color || 'Unknown',
                        modified: false,
                        dateAcquired: auto.created_at,
                        registrationNumber: auto.vehicle_registration || '',
                        vehicleType: (auto.fuel_type === 'Automatic' ? 'Automatic' : 'Manual') as any,
                        usage: (auto.vehicle_usage as any) || 'Domestic',
                        dateOfPurchase: auto.created_at,
                        vehicleAge: 'N/A',
                        parkedLocation: 'Driveway',
                        imageUrl: 'https://images.unsplash.com/photo-1541899481282-d53bffe3c35d?auto=format&fit=crop&q=80&w=400'
                    }));
                    setVehicles(portalVehicles);
                }

                const defaultVehicle = portalVehicles[0] || { make: 'Unknown', model: 'Unknown', registrationNumber: 'Unknown' };

                // Fetch Other Data
                const [qs, ps, cs, pays] = await Promise.all([
                    quoteApi.getQuotes({ client_id: clientData.id }),
                    policyApi.getPolicies({ client_id: clientData.id }),
                    claimApi.getClaims({ client_id: clientData.id }),
                    paymentApi.getPayments({ client_id: clientData.id, page: 1, page_size: 100 })
                ]);

                // Map Quotes
                setQuotes(qs.quotes.map(q => ({
                    id: q.id,
                    vehicle: portalVehicles.find(v => v.id === (q.details?.vehicle_id || '')) || defaultVehicle,
                    reference: q.quote_number,
                    coverLevel: q.details?.cover_level || 'Standard',
                    coverType: 'Comprehensive',
                    basePremium: `£${q.final_premium}`,
                    premium: `£${q.final_premium}`,
                    expiresAt: new Date(new Date(q.created_at).setMonth(new Date(q.created_at).getMonth() + 1)).toISOString().split('T')[0],
                    drivers: [`${clientData.first_name} ${clientData.last_name}`],
                    usage: 'Social, Domestic & Pleasure',
                    status: q.status,
                    included_services: q.details?.selected_services || ['comprehensive']
                })));

                // Map Policies
                setPolicies(ps.policies.map(p => ({
                    id: p.id,
                    vehicle: portalVehicles.find(v => v.id === (p.details?.vehicle_id || '')) || defaultVehicle,
                    policyNumber: p.policy_number,
                    coverLevel: p.details?.cover_level || 'Gold',
                    coverType: 'Comprehensive',
                    activeDate: p.start_date.split('T')[0],
                    validUntil: p.end_date.split('T')[0],
                    status: p.status,
                    premium: `£${p.premium_amount || 0}`,
                    included_services: p.details?.selected_services || ['comprehensive', 'windscreen']
                })));

                // Map Claims
                setClaims(cs.filter(c => c.client_id === clientData.id).map(c => ({
                    id: c.id,
                    reference: c.claim_number,
                    date: c.incident_date.split('T')[0],
                    policyId: c.policy_id,
                    vehicle: defaultVehicle.make + ' ' + defaultVehicle.model,
                    type: 'Accident',
                    status: c.status,
                    amount: `£${c.claim_amount}`
                })));

                // Map Payments
                setPayments(pays.payments.map(p => ({
                    id: p.id,
                    date: p.created_at.split('T')[0],
                    policyId: p.policy_id,
                    amount: `£${p.amount}`,
                    method: p.payment_method,
                    status: p.status,
                    type: 'Premium'
                })));
            } catch (error) {
                console.error('Failed to load portal insurance details:', error);
            } finally {
                setLoading(false);
            }
        };

        loadData();
    }, []);

    if (loading) {
        return (
            <div className="flex items-center justify-center min-h-[400px]">
                <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-[#00539F]"></div>
            </div>
        );
    }

    return (
        <div className="space-y-12">
            <div className="space-y-4">
                <h2 className="text-2xl font-black text-gray-900 tracking-tight">Insurance Details</h2>
                <p className="text-gray-400 text-lg font-bold">Manage your policy drivers and vehicles. Keep your information up to date to ensure valid cover.</p>
            </div>

            <div className="bg-white border border-gray-100 shadow-xl rounded-[40px] p-6 md:p-12">
                <InsuranceDetailsTab
                    clientId={client?.id}
                    initialDrivers={drivers}
                    initialVehicles={vehicles}
                    initialQuotes={quotes}
                    initialPolicies={policies}
                    initialClaims={claims}
                    initialPayments={payments}
                />
            </div>
        </div>
    );
}
