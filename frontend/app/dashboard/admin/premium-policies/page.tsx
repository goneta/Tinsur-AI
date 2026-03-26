"use client"

import { useState, useEffect, useMemo, useCallback } from 'react'
import { Plus, Pencil, Trash2, Filter, LayoutGrid, List as ListIcon, Loader2, Check } from 'lucide-react'
import { Button } from '@/components/ui/button'
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from '@/components/ui/card'
import { DataView } from '@/components/ui/data-view'
import { useToast } from '@/components/ui/use-toast'
import { UniversalEntityCard } from '@/components/shared/universal-entity-card'
import { FormattedCurrency } from '@/components/shared/formatted-currency'
import { premiumPolicyApi, PremiumPolicyType } from '@/lib/premium-policy-api'
import { columns as getColumns } from './columns'
import { PremiumPolicyForm } from './components/premium-policy-form'
import { Badge } from '@/components/ui/badge'
import { useLanguage } from '@/contexts/language-context'

export default function PremiumPoliciesPage() {
    const { t, language, formatPrice } = useLanguage()
    const [policyTypes, setPolicyTypes] = useState<PremiumPolicyType[]>([])
    const [loading, setLoading] = useState(true)
    const [isFormOpen, setIsFormOpen] = useState(false)
    const [selectedPolicy, setSelectedPolicy] = useState<PremiumPolicyType | undefined>()
    const [mounted, setMounted] = useState(false)
    const { toast } = useToast()

    useEffect(() => {
        setMounted(true)
        loadPolicyTypes()
    }, [])

    const loadPolicyTypes = async () => {
        setLoading(true)
        try {
            const data = await premiumPolicyApi.getPolicyTypes()
            setPolicyTypes(data.premium_policy_types)
        } catch (error) {
            console.error('Failed to load policy types:', error)
            toast({
                title: 'Error',
                description: 'Failed to load policy types',
                variant: 'destructive',
            })
        } finally {
            setLoading(false)
        }
    }

    const handleEdit = (policy: PremiumPolicyType) => {
        setSelectedPolicy(policy)
        setIsFormOpen(true)
    }

    const handleDelete = async (policy: PremiumPolicyType) => {
        if (!confirm(`Are you sure you want to delete ${policy.name}?`)) return
        try {
            await premiumPolicyApi.deletePolicyType(policy.id)
            toast({ title: 'Success', description: 'Policy type deleted' })
            loadPolicyTypes()
        } catch (error) {
            toast({ title: 'Error', description: 'Failed to delete policy type', variant: 'destructive' })
        }
    }

    const handleSuccess = () => {
        loadPolicyTypes()
        setIsFormOpen(false)
        setSelectedPolicy(undefined)
    }

    const columns = useMemo(() => getColumns(handleEdit, handleDelete, formatPrice), [handleEdit, handleDelete, formatPrice])

    const renderPolicyCard = useCallback((policy: PremiumPolicyType) => {
        // Map services to generic card items
        const serviceItems = (policy.services || []).map(service => ({
            id: `service-${service.id}`,
            label: (
                <span className="text-[10px]">
                    {language === 'fr' && service.name_fr ? service.name_fr : service.name_en}
                </span>
            ),
            checked: true,
            disabled: true,
            price: service.default_price, // Add price to display on the right
            priceClassName: "text-[10px]" // Reduced font size for price
        }));

        // Map criteria to generic card items
        const criteriaItems = (policy.criteria || []).map(criterion => ({
            id: `criteria-${criterion.id}`,
            label: (
                <span className="text-[10px]">
                    {t(`criteria.${criterion.field_name}`, criterion.field_name)} {criterion.operator} {criterion.value}
                </span>
            ),
            checked: true,
            disabled: true,
            icon: <Check className="h-2 w-2 text-white" />,
            checkClassName: "h-3 w-3 mt-0.5", // Reduced from h-5 w-5
            iconClassName: "h-2 w-2" // Reduced from h-3.5 w-3.5
        }));

        const allItems = [
            // Criteria Section
            {
                id: 'header-criteria',
                label: "Eligibility criteria",
                isSectionHeader: true
            },
            ...criteriaItems,

            // Services Section
            {
                id: 'header-services',
                label: "Included services",
                isSectionHeader: true
            },
            ...serviceItems
        ];

        // Calculate Total Premium: Base Price + Sum of all included services
        const servicesTotal = (policy.services || []).reduce((sum, service) => sum + Number(service.default_price || 0), 0);
        const totalPremium = Number(policy.price || 0) + servicesTotal;

        return (
            <div className="h-full relative group">
                <UniversalEntityCard
                    header={{
                        title: t(`policy.${policy.name.toLowerCase().replace(/ /g, '_')}`, policy.name),
                        customContent: (
                            <div className="flex flex-col items-center justify-center text-center w-full mb-2">
                                {/* Policy Name - Larger and Bolder */}
                                <h3 className="text-sm font-extrabold text-slate-800 uppercase tracking-wide mb-1">
                                    {t(`policy.${policy.name.toLowerCase().replace(/ /g, '_')}`, policy.name)}
                                </h3>

                                {/* Rating - Smaller */}
                                <div className="flex items-center gap-1 mb-1">
                                    <span className="text-[10px] font-black text-[#00539F]">4.8</span>
                                    <div className="flex gap-0.5 text-[#00539F]">
                                        {Array(5).fill(0).map((_, i) => (
                                            <svg key={i} xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="currentColor" className="w-2.5 h-2.5">
                                                <path fillRule="evenodd" d="M10.788 3.21c.448-1.077 1.976-1.077 2.424 0l2.082 5.007 5.404.433c1.164.093 1.636 1.545.749 2.305l-4.117 3.527 1.257 5.273c.271 1.136-.964 2.033-1.96 1.425L12 18.354 7.373 21.18c-.996.608-2.231-.29-1.96-1.425l1.257-5.273-4.117-3.527c-.887-.76-.415-2.212.749-2.305l5.404-.433 2.082-5.006z" clipRule="evenodd" />
                                            </svg>
                                        ))}
                                    </div>
                                </div>
                            </div>
                        )
                    }}
                    items={allItems}
                    financials={[
                        {
                            label: <span className="text-xs font-bold text-slate-600 uppercase tracking-wider">{t('premium_policies.cover_amount', 'Cover amount')}:</span>,
                            amount: <FormattedCurrency amount={totalPremium} className="text-sm font-black text-[#00539F] ml-2" />,
                            isTotal: false
                        }
                    ]}
                    actions={
                        <div className="flex gap-2 w-full">
                            <Button
                                variant="outline"
                                className="flex-1"
                                onClick={() => handleEdit(policy)}
                            >
                                <Pencil className="mr-2 h-4 w-4" />
                                {t('common.edit', 'Edit')}
                            </Button>
                            <Button
                                variant="destructive"
                                size="icon"
                                onClick={() => handleDelete(policy)}
                            >
                                <Trash2 className="h-4 w-4" />
                            </Button>
                        </div>
                    }
                />
            </div>
        );
    }, [handleEdit, handleDelete, t, language]);

    if (!mounted) return null

    return (
        <div className="space-y-4">
            <div className="flex items-center justify-between">
                <div>
                    <h2 className="text-3xl font-bold tracking-tight">{t('premium_policies.title')}</h2>
                    <p className="text-muted-foreground">
                        {t('premium_policies.desc')}
                    </p>
                </div>
                <Button onClick={() => {
                    setSelectedPolicy(undefined)
                    setIsFormOpen(true)
                }}>
                    <Plus className="mr-2 h-4 w-4" />
                    {t('premium_policies.new_policy')}
                </Button>
            </div>

            {loading && policyTypes.length === 0 ? (
                <div className="flex flex-col items-center justify-center py-20 gap-4">
                    <Loader2 className="h-8 w-8 animate-spin text-primary" />
                    <p className="text-muted-foreground">{t('common.loading', 'Loading premium policies...')}</p>
                </div>
            ) : (
                <DataView
                    columns={columns}
                    data={policyTypes}
                    renderCard={renderPolicyCard}
                    defaultView="card"
                    getRowId={(row) => row.id}
                />
            )}

            <PremiumPolicyForm
                open={isFormOpen}
                onOpenChange={setIsFormOpen}
                policyType={selectedPolicy}
                onSuccess={handleSuccess}
            />
        </div>
    )
}
