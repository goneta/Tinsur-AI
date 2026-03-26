'use client';

import { useEffect, useState } from 'react';
import { InsuranceDetailsTab, PortalDriver as Driver, PortalVehicle } from '@/components/portal/insurance-details-tab';
import { clientApi } from '@/lib/client-api';
import { policyApi } from '@/lib/policy-api';
import { quoteApi } from '@/lib/quote-api';
import { claimApi } from '@/lib/claim-api';
import { paymentApi } from '@/lib/payment-api';
import { Client } from '@/types/client';
import { Quote } from '@/types/quote';

export default function InsuranceDetailsPage() {
    const [loading, setLoading] = useState(true);
    const [client, setClient] = useState<Client | null>(null);
    const [drivers, setDrivers] = useState<Driver[]>([]);
    const [vehicles, setVehicles] = useState<PortalVehicle[]>([]);
    const [quotes, setQuotes] = useState<Quote[]>([]);
    const [policies, setPolicies] = useState<any[]>([]);
    const [claims, setClaims] = useState<any[]>([]);
    const [payments, setPayments] = useState<any[]>([]);

    useEffect(() => {
        const loadData = async () => {
            try {
                const clientData = await clientApi.getMyClient();
                console.log("DEBUG: insurance-details/page.tsx - clientData:", clientData);
                setClient(clientData);

                // Map Drivers
                // Map Drivers
                if (clientData.drivers && clientData.drivers.length > 0) {
                    setDrivers(clientData.drivers.map(d => ({
                        id: d.id,
                        fullName: `${d.first_name || ''} ${d.last_name || ''}`.trim(),
                        phoneNumber: d.phone_number || '',
                        address: d.address || '',
                        licenseNumber: d.license_number || 'PENDING',
                        licenseIssueDate: d.license_issue_date || '',
                        employmentStatus: d.employment_status || '',
                        maritalStatus: d.marital_status || '',
                        numberOfChildren: d.number_of_children || 0,
                        photoUrl: d.photo_url || `https://api.dicebear.com/7.x/avataaars/svg?seed=${d.id}`,
                        dateOfBirth: d.date_of_birth ? new Date(d.date_of_birth).toISOString().split('T')[0] : ''
                    })));
                } else {
                    console.log("DEBUG: insurance-details/page.tsx - No drivers found, applying fallback logic");
                    // Fallback to basic user info if no explicit drivers
                    const dob = clientData.date_of_birth ? new Date(clientData.date_of_birth) : null;
                    const dobString = (dob && !isNaN(dob.getTime())) ? dob.toISOString().split('T')[0] : '';

                    setDrivers([{
                        id: clientData.id,
                        fullName: `${clientData.first_name || ''} ${clientData.last_name || ''}`.trim(),
                        phoneNumber: clientData.phone || '',
                        address: clientData.address || '',
                        city: clientData.city || '',
                        country: clientData.country || '',
                        postalCode: '',
                        licenseNumber: clientData.driving_licence_number || 'PENDING',
                        licenseIssueDate: '',
                        employmentStatus: clientData.employment_status || '',
                        maritalStatus: clientData.marital_status || '',
                        numberOfChildren: 0,
                        photoUrl: clientData.profile_picture || `https://api.dicebear.com/7.x/avataaars/svg?seed=${clientData.first_name}`,
                        dateOfBirth: dobString,
                        clientId: clientData.id,
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

                const defaultVehicle: PortalVehicle = portalVehicles[0] || {
                    id: 'default-mock-id',
                    make: 'Unknown',
                    model: 'Unknown',
                    registrationNumber: 'Unknown',
                    mileage: '0',
                    colour: 'Unknown',
                    modified: false,
                    dateAcquired: new Date().toISOString().split('T')[0],
                    vehicleType: 'Manual',
                    usage: 'Domestic',
                    dateOfPurchase: new Date().toISOString().split('T')[0],
                    vehicleAge: 'N/A',
                    parkedLocation: 'Driveway',
                    imageUrl: 'https://images.unsplash.com/photo-1541899481282-d53bffe3c35d?auto=format&fit=crop&q=80&w=400'
                };

                // Fetch Other Data
                const [qs, ps, cs, pays] = await Promise.all([
                    quoteApi.getQuotes({ client_id: clientData.id }),
                    policyApi.getPolicies({ client_id: clientData.id }),
                    claimApi.getClaims({ client_id: clientData.id }),
                    paymentApi.getPayments({ client_id: clientData.id, page: 1, page_size: 100 })
                ]);
                setQuotes(qs.quotes);

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
