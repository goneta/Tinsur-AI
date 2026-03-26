/**
 * Policy list page.
 */
'use client';

import { useState, useEffect, useCallback, useMemo } from 'react';
import { useRouter } from 'next/navigation';
import {
    Plus,
    Shield,
    Loader2
} from 'lucide-react';
import { useLanguage } from '@/contexts/language-context';

import { policyApi } from '@/lib/policy-api';
import { premiumPolicyApi, PremiumPolicyType } from '@/lib/premium-policy-api';
import { QuoteAPI } from '@/lib/api/quotes';
import { Policy } from '@/types/policy';

import { Button } from '@/components/ui/button';
import { PolicyFormDialog } from '@/components/policies/policy-form-dialog';
import { DataView } from '@/components/ui/data-view';
import { PolicyCard } from '@/components/shared/policy-card';
import { columns } from './columns';
import { EmptyState } from '@/components/ui/empty-state';

export default function PoliciesPage() {
    const router = useRouter();
    const { t, formatPrice } = useLanguage();
    const [policies, setPolicies] = useState<Policy[]>([]);
    const [loading, setLoading] = useState(true);
    const [isMounted, setIsMounted] = useState(false);

    // Rich Data Maps
    const [policyTypeNames, setPolicyTypeNames] = useState<Record<string, string>>({});
    const [premiumPolicyTypes, setPremiumPolicyTypes] = useState<Record<string, PremiumPolicyType>>({});

    // Dialog states
    const [isCreateOpen, setIsCreateOpen] = useState(false);
    const [editingPolicy, setEditingPolicy] = useState<Policy | null>(null);

    const loadPolicies = async () => {
        setLoading(true);
        try {
            // Fetch ALL policies
            const data = await policyApi.getPolicies({ limit: 1000 });
            setPolicies(data.policies);

            // Fetch Policy Types (Basic Names)
            try {
                const types = await QuoteAPI.listPolicyTypes()
                const typeMap: Record<string, string> = {}
                types.forEach(t => typeMap[t.id] = t.name)
                setPolicyTypeNames(typeMap)
            } catch (e) {
                console.warn("Failed to load policy types", e)
            }

            // Fetch Premium Policy Types (Rich Data like services/criteria)
            try {
                const premData = await premiumPolicyApi.getPolicyTypes()
                const premMap: Record<string, PremiumPolicyType> = {}
                if (premData && premData.premium_policy_types) {
                    premData.premium_policy_types.forEach(p => premMap[p.id] = p)
                }
                setPremiumPolicyTypes(premMap)
            } catch (err) {
                console.warn("Failed to fetch premium policies", err)
            }

        } catch (error) {
            console.error('Failed to load policies:', error);
        } finally {
            setLoading(false);
        }
    };

    useEffect(() => {
        setIsMounted(true);
        loadPolicies();
    }, []);


    const handlePolicyCreated = useCallback(() => {
        setIsCreateOpen(false);
        loadPolicies();
    }, []);

    const handlePolicyUpdated = useCallback(() => {
        setEditingPolicy(null);
        loadPolicies();
    }, []);

    const handleDelete = useCallback(async (id: string) => {
        if (confirm(t('Are you sure you want to delete this policy?'))) {
            try {
                await policyApi.deletePolicy(id);
                loadPolicies();
            } catch (error) {
                console.error('Failed to delete policy:', error);
            }
        }
    }, []);

    const handleView = useCallback((id: string) => {
        router.push(`/dashboard/policies/${id}`);
    }, [router]);

    const handleGenerateSchedule = useCallback((id: string) => {
        // We can navigate to details page where button exists, or implement direct call here.
        // For alignment with current flow, let's navigate to view. 
        // OR: If we want direct action, we call API.
        // User request "Send to Client" on card implies generation/send.
        // For now, let's just View, as generation is on details page.
        // Wait, reference image has "Send to Client". 
        // Let's make it go to details page for now to leverage existing flow + verify.
        router.push(`/dashboard/policies/${id}`);
    }, [router]);

    const tableColumns = useMemo(() => columns(handleView, setEditingPolicy, handleDelete, t, formatPrice), [handleView, handleDelete, t, formatPrice]);

    const renderCard = useCallback((policy: Policy) => {
        // Map Policy to PolicyCardProps
        const features = (policy.details?.included_services || ['comprehensive', 'windscreen']).map((service: string) => ({
            id: service,
            label: t(service, service.replace(/_/g, ' ').replace(/\b\w/g, l => l.toUpperCase())), // Use t() for translation with fallback
            included: true
        }));

        const cardPolicy = {
            id: policy.id,
            vehicleName: `${policy.details?.vehicle_make || t('Unknown', 'Unknown')} ${policy.details?.vehicle_model || t('Vehicle', 'Vehicle')}`,
            registrationNumber: policy.details?.vehicle_registration || policy.details?.registration_number || 'N/A',
            policyNumber: policy.policy_number,
            status: policy.status,
            activeDate: policy.start_date ? new Date(policy.start_date).toLocaleDateString() : 'N/A',
            premium: `£${policy.premium_amount}`,
            coverLevel: t(policyTypeNames[policy.policy_type_id] || 'Standard', policyTypeNames[policy.policy_type_id] || 'Standard'),
            features: features
        };

        return (
            <PolicyCard
                key={policy.id}
                policy={cardPolicy}
                onViewDocuments={() => handleView(policy.id)}
                onMakeClaim={() => router.push(`/dashboard/policies/${policy.id}`)}
                onMakePayment={() => router.push(`/dashboard/clients/${policy.client_id}`)} // Redirect to client profile
                className="mb-4"
            />
        );
    }, [policyTypeNames, handleView, router]);

    if (!isMounted) return null;

    return (
        <div className="flex-1 space-y-4 p-8 pt-6">
            <div className="flex justify-between items-center">
                <div>
                    <h2 className="text-3xl font-bold tracking-tight">{t('policies.title')}</h2>
                    <p className="text-muted-foreground">{t('policies.desc')}</p>
                </div>
                <Button onClick={() => setIsCreateOpen(true)}>
                    <Plus className="mr-2 h-4 w-4" />
                    {t('policies.new_policy')}
                </Button>
            </div>

            <div className="mt-4">
                {loading ? (
                    <div className="flex flex-col items-center justify-center py-20 gap-4">
                        <Loader2 className="h-8 w-8 animate-spin text-primary" />
                        <p className="text-muted-foreground">{t('common.loading', 'Loading policies...')}</p>
                    </div>
                ) : policies.length === 0 ? (
                    <div className="py-10">
                        <EmptyState
                            title={t('policies.no_policies', 'No policies found')}
                            description={t('policies.no_policies_desc', "You haven't created any insurance policies yet.")}
                            icon={Shield}
                            action={{
                                label: t('policies.create_first', "Create First Policy"),
                                onClick: () => setIsCreateOpen(true),
                                icon: Plus
                            }}
                        />
                    </div>
                ) : (
                    <div className="animate-in fade-in-50 duration-500">
                        <DataView
                            columns={tableColumns}
                            data={policies}
                            renderCard={renderCard}
                            defaultView="card"
                            getRowId={(row) => row.id}
                        />
                    </div>
                )}
            </div>

            <PolicyFormDialog
                open={isCreateOpen}
                onOpenChange={setIsCreateOpen}
                onSuccess={handlePolicyCreated}
            />

            {editingPolicy && (
                <PolicyFormDialog
                    open={!!editingPolicy}
                    onOpenChange={(open) => !open && setEditingPolicy(null)}
                    policy={editingPolicy}
                    onSuccess={handlePolicyUpdated}
                />
            )}
        </div>
    );
}
