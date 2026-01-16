"use client"

import { useState, useEffect, useMemo, useCallback } from 'react'
import { Plus, Pencil, Trash2, Filter, LayoutGrid, List as ListIcon, Loader2, Check } from 'lucide-react'
import { Button } from '@/components/ui/button'
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from '@/components/ui/card'
import { DataView } from '@/components/ui/data-view'
import { useToast } from '@/components/ui/use-toast'
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

    const renderPolicyCard = useCallback((policy: PremiumPolicyType) => (
        <Card className="relative overflow-hidden hover:shadow-xl transition-all h-full flex flex-col border border-border shadow-sm group bg-white p-0 rounded-none">
            {/* Green Header Strip */}
            <div className="h-4 bg-[#76c077] w-full" />

            <div className="p-5 flex flex-col h-full relative">
                {/* Action Buttons (Absolute Top Right) */}
                <div className="absolute top-2 right-2 flex items-center gap-1 opacity-0 group-hover:opacity-100 transition-opacity z-10">
                    <Button
                        variant="ghost"
                        size="icon"
                        className="h-8 w-8 text-muted-foreground hover:text-foreground"
                        onClick={() => handleEdit(policy)}
                        title="Edit"
                    >
                        <Pencil className="h-4 w-4" />
                    </Button>
                    <Button
                        variant="ghost"
                        size="icon"
                        className="h-8 w-8 text-destructive hover:text-destructive"
                        onClick={() => handleDelete(policy)}
                        title="Delete"
                    >
                        <Trash2 className="h-4 w-4" />
                    </Button>
                </div>

                {/* Header Section */}
                <div className="mb-4">
                    <div className="text-sm font-bold text-black mb-0">{t('policy.demo_co', 'Demo Insurance Co')}</div>
                    <h3 className="text-2xl font-bold text-black tracking-tight mb-1">
                        {t(`policy.${policy.name.toLowerCase().replace(/ /g, '_')}`, policy.name)}
                    </h3>

                    {/* Star Rating */}
                    <div className="flex items-center gap-2 mb-1">
                        <span className="text-sm font-medium">4.8 {t('premium_policies.client_rating', 'Client Rating')}</span>
                        <div className="flex gap-0.5 text-black">
                            {Array(5).fill(0).map((_, i) => (
                                <svg key={i} xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="currentColor" className="w-4 h-4 text-black">
                                    <path fillRule="evenodd" d="M10.788 3.21c.448-1.077 1.976-1.077 2.424 0l2.082 5.007 5.404.433c1.164.093 1.636 1.545.749 2.305l-4.117 3.527 1.257 5.273c.271 1.136-.964 2.033-1.96 1.425L12 18.354 7.373 21.18c-.996.608-2.231-.29-1.96-1.425l1.257-5.273-4.117-3.527c-.887-.76-.415-2.212.749-2.305l5.404-.433 2.082-5.006z" clipRule="evenodd" />
                                </svg>
                            ))}
                        </div>
                    </div>
                    <div className="text-sm font-bold text-black">{t('premium_policies.excess', 'Excess')}: {formatPrice(policy.excess)}</div>
                </div>

                {/* Features List */}
                <div className="space-y-4 mb-8 flex-1">
                    {/* Included Services */}
                    {policy.services && policy.services.length > 0 && (
                        <div>
                            <h4 className="font-bold text-sm mb-2 text-black">{t('premium_policies.included_services', 'Included Services')}</h4>
                            <div className="space-y-2">
                                {policy.services.map((service) => (
                                    <div key={service.id} className="flex items-start gap-3">
                                        <div className="mt-0.5 min-w-[20px]">
                                            <div className="h-5 w-5 rounded-full bg-[#1b5e63] flex items-center justify-center">
                                                <Check className="h-3 w-3 text-white stroke-[3]" />
                                            </div>
                                        </div>
                                        <span className="text-[15px] text-gray-800 leading-tight">
                                            {language === 'fr' && service.name_fr ? service.name_fr : service.name_en}
                                        </span>
                                    </div>
                                ))}
                            </div>
                        </div>
                    )}

                    {/* Eligibility Criteria */}
                    {policy.criteria && policy.criteria.length > 0 && (
                        <div>
                            <h4 className="font-bold text-sm mb-2 text-black">{t('premium_policies.eligibility', 'Eligibility Criteria')}</h4>
                            <div className="space-y-2">
                                {policy.criteria.map((criterion) => (
                                    <div key={criterion.id} className="flex items-start gap-3">
                                        <div className="mt-0.5 min-w-[20px]">
                                            <div className="h-5 w-5 rounded-full bg-[#1b5e63] flex items-center justify-center">
                                                <Check className="h-3 w-3 text-white stroke-[3]" />
                                            </div>
                                        </div>
                                        <span className="text-[15px] text-gray-800 leading-tight">
                                            {criterion.field_name} {criterion.operator} {criterion.value}
                                        </span>
                                    </div>
                                ))}
                            </div>
                        </div>
                    )}
                </div>

                {/* Price Footer */}
                <div className="mt-auto text-center border-t border-transparent pt-4">
                    <div className="flex flex-col items-center justify-end mb-4">
                        <span className="text-3xl font-extrabold text-black tracking-tight">
                            {formatPrice(policy.price)}
                        </span>
                        <span className="text-lg font-bold text-black">{t('premium_policies.per_month', 'Per Month')}</span>
                    </div>

                    <div className="text-[10px] leading-tight text-gray-600 space-y-1">
                        <p>
                            {t('premium_policies.deposit_text')
                                .replace('{0}', formatPrice(0))
                                .replace('{1}', '12')
                                .replace('{2}', formatPrice(policy.price))}
                        </p>
                        <p>
                            {t('premium_policies.legal_note')
                                .replace('{0}', formatPrice(53))
                                .replace('{1}', formatPrice(policy.price * 12 + 53))}
                        </p>
                    </div>
                </div>
            </div>
        </Card>
    ), [handleEdit, handleDelete])

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
