"use client"

import { useState, useEffect } from 'react'
import { Loader2, ExternalLink, Filter, ShieldCheck } from 'lucide-react'
import Link from 'next/link'
import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
import { Label } from '@/components/ui/label'
import { Textarea } from '@/components/ui/textarea'
import { Switch } from '@/components/ui/switch'
import { Checkbox } from '@/components/ui/checkbox'
import { Badge } from '@/components/ui/badge'
import { useToast } from '@/components/ui/use-toast'
import { useLanguage } from '@/contexts/language-context'
import {
    Dialog,
    DialogContent,
    DialogDescription,
    DialogFooter,
    DialogHeader,
    DialogTitle,
} from '@/components/ui/dialog'
import {
    premiumPolicyApi,
    PremiumPolicyType,
    PremiumPolicyTypeCreate,
    PremiumPolicyCriteria,
} from '@/lib/premium-policy-api'
import { policyServiceApi, PolicyService } from '@/lib/policy-service-api'

interface PremiumPolicyFormProps {
    open: boolean
    onOpenChange: (open: boolean) => void
    policyType?: PremiumPolicyType
    onSuccess: () => void
}

export function PremiumPolicyForm({
    open,
    onOpenChange,
    policyType,
    onSuccess,
}: PremiumPolicyFormProps) {
    const { t, formatPrice } = useLanguage()
    const { toast } = useToast()
    const isEditing = !!policyType

    // Form state
    const [name, setName] = useState('')
    const [description, setDescription] = useState('')
    const [price, setPrice] = useState('')
    const [excess, setExcess] = useState('')
    const [isActive, setIsActive] = useState(true)
    const [selectedCriteriaIds, setSelectedCriteriaIds] = useState<string[]>([])
    const [selectedServiceIds, setSelectedServiceIds] = useState<string[]>([])

    // Data
    const [criteria, setCriteria] = useState<PremiumPolicyCriteria[]>([])
    const [services, setServices] = useState<PolicyService[]>([])
    const [loadingData, setLoadingData] = useState(false)
    const [saving, setSaving] = useState(false)

    // Load criteria and services when dialog opens
    useEffect(() => {
        if (open) {
            loadFormData()
        }
    }, [open])

    // Populate form when editing
    useEffect(() => {
        if (policyType) {
            setName(policyType.name || '')
            setDescription(policyType.description || '')
            setPrice(String(policyType.price || 0))
            setExcess(String(policyType.excess || 0))
            setIsActive(policyType.is_active ?? true)
            setSelectedCriteriaIds(
                (policyType.criteria || []).map((c) => c.id)
            )
            setSelectedServiceIds(
                (policyType.services || []).map((s) => s.id)
            )
        } else {
            resetForm()
        }
    }, [policyType, open])

    const resetForm = () => {
        setName('')
        setDescription('')
        setPrice('')
        setExcess('')
        setIsActive(true)
        setSelectedCriteriaIds([])
        setSelectedServiceIds([])
    }

    const loadFormData = async () => {
        setLoadingData(true)
        try {
            const [criteriaData, servicesData] = await Promise.all([
                premiumPolicyApi.getCriteria(),
                policyServiceApi.getAll(),
            ])
            setCriteria(Array.isArray(criteriaData) ? criteriaData : [])
            setServices(Array.isArray(servicesData) ? servicesData : [])
        } catch (error) {
            console.error('Failed to load form data:', error)
        } finally {
            setLoadingData(false)
        }
    }

    const toggleCriteria = (id: string) => {
        setSelectedCriteriaIds((prev) =>
            prev.includes(id) ? prev.filter((c) => c !== id) : [...prev, id]
        )
    }

    const toggleService = (id: string) => {
        setSelectedServiceIds((prev) =>
            prev.includes(id) ? prev.filter((s) => s !== id) : [...prev, id]
        )
    }

    const handleSubmit = async () => {
        if (!name.trim()) {
            toast({
                title: t('common.error', 'Error'),
                description: t('premium_policies.name_required', 'Policy name is required'),
                variant: 'destructive',
            })
            return
        }

        setSaving(true)
        try {
            const payload: PremiumPolicyTypeCreate = {
                name: name.trim(),
                description: description.trim() || undefined,
                price: parseFloat(price) || 0,
                excess: parseFloat(excess) || 0,
                is_active: isActive,
                criteria_ids: selectedCriteriaIds,
                service_ids: selectedServiceIds,
            }

            if (isEditing && policyType) {
                await premiumPolicyApi.updatePolicyType(policyType.id, payload)
                toast({
                    title: t('common.success', 'Success'),
                    description: t('premium_policies.updated', 'Premium policy updated successfully'),
                })
            } else {
                await premiumPolicyApi.createPolicyType(payload)
                toast({
                    title: t('common.success', 'Success'),
                    description: t('premium_policies.created', 'Premium policy created successfully'),
                })
            }

            onSuccess()
        } catch (error: any) {
            toast({
                title: t('common.error', 'Error'),
                description:
                    error?.response?.data?.detail ||
                    t('premium_policies.save_failed', 'Failed to save premium policy'),
                variant: 'destructive',
            })
        } finally {
            setSaving(false)
        }
    }

    return (
        <Dialog open={open} onOpenChange={onOpenChange}>
            <DialogContent className="sm:max-w-[640px] max-h-[90vh] overflow-y-auto">
                <DialogHeader>
                    <DialogTitle>
                        {isEditing
                            ? t('premium_policies.edit_policy', 'Edit Premium Policy')
                            : t('premium_policies.new_policy', 'New Premium Policy')}
                    </DialogTitle>
                    <DialogDescription>
                        {isEditing
                            ? t('premium_policies.edit_desc', 'Update the details for this premium policy type.')
                            : t('premium_policies.create_desc', 'Create a new premium policy type with criteria and services.')}
                    </DialogDescription>
                </DialogHeader>

                {loadingData ? (
                    <div className="flex items-center justify-center py-8">
                        <Loader2 className="h-6 w-6 animate-spin text-primary" />
                    </div>
                ) : (
                    <div className="grid gap-5 py-4">
                        {/* Name */}
                        <div className="grid gap-2">
                            <Label htmlFor="name">{t('common.name', 'Name')} *</Label>
                            <Input
                                id="name"
                                value={name}
                                onChange={(e) => setName(e.target.value)}
                                placeholder={t('premium_policies.name_placeholder', 'e.g. Gold Plan')}
                            />
                        </div>

                        {/* Description */}
                        <div className="grid gap-2">
                            <Label htmlFor="description">{t('common.description', 'Description')}</Label>
                            <Textarea
                                id="description"
                                value={description}
                                onChange={(e) => setDescription(e.target.value)}
                                placeholder={t('premium_policies.desc_placeholder', 'Describe this policy type...')}
                                rows={3}
                            />
                        </div>

                        {/* Price & Excess */}
                        <div className="grid grid-cols-2 gap-4">
                            <div className="grid gap-2">
                                <Label htmlFor="price">{t('common.price', 'Base Price')} *</Label>
                                <Input
                                    id="price"
                                    type="number"
                                    min="0"
                                    step="0.01"
                                    value={price}
                                    onChange={(e) => setPrice(e.target.value)}
                                    placeholder="0.00"
                                />
                            </div>
                            <div className="grid gap-2">
                                <Label htmlFor="excess">{t('premium_policies.excess', 'Excess')}</Label>
                                <Input
                                    id="excess"
                                    type="number"
                                    min="0"
                                    step="0.01"
                                    value={excess}
                                    onChange={(e) => setExcess(e.target.value)}
                                    placeholder="0.00"
                                />
                            </div>
                        </div>

                        {/* Active Toggle */}
                        <div className="flex items-center justify-between">
                            <Label htmlFor="is-active">{t('common.active', 'Active')}</Label>
                            <Switch id="is-active" checked={isActive} onCheckedChange={setIsActive} />
                        </div>

                        {/* ─── Eligibility Criteria ─── */}
                        <div className="grid gap-2">
                            <div className="flex items-center justify-between">
                                <Label className="flex items-center gap-1.5">
                                    <Filter className="h-4 w-4 text-violet-500" />
                                    {t('premium_policies.criteria', 'Eligibility Criteria')}
                                    <Badge variant="secondary" className="ml-1 text-[10px]">
                                        {selectedCriteriaIds.length} {t('common.selected', 'selected')}
                                    </Badge>
                                </Label>
                                <Link
                                    href="/dashboard/admin/policy-criteria"
                                    target="_blank"
                                    className="text-xs text-primary hover:underline flex items-center gap-1"
                                >
                                    {t('premium_policies.manage_criteria', 'Manage Criteria')}
                                    <ExternalLink className="h-3 w-3" />
                                </Link>
                            </div>
                            {criteria.length > 0 ? (
                                <div className="border rounded-md p-3 max-h-48 overflow-y-auto space-y-2">
                                    {criteria.map((c) => (
                                        <div key={c.id} className="flex items-center space-x-2 py-0.5">
                                            <Checkbox
                                                id={`criteria-${c.id}`}
                                                checked={selectedCriteriaIds.includes(c.id)}
                                                onCheckedChange={() => toggleCriteria(c.id)}
                                            />
                                            <label htmlFor={`criteria-${c.id}`} className="text-sm cursor-pointer flex-1">
                                                <span className="font-medium">{c.name || c.field_name}</span>
                                                <span className="text-muted-foreground ml-1.5">
                                                    ({c.field_name} {c.operator} {c.value})
                                                </span>
                                            </label>
                                        </div>
                                    ))}
                                </div>
                            ) : (
                                <div className="border rounded-md p-4 text-center text-sm text-muted-foreground">
                                    {t('premium_policies.no_criteria', 'No criteria defined yet.')}
                                    <Link
                                        href="/dashboard/admin/policy-criteria"
                                        target="_blank"
                                        className="text-primary hover:underline ml-1"
                                    >
                                        {t('premium_policies.create_criteria_link', 'Create criteria first')}
                                    </Link>
                                </div>
                            )}
                        </div>

                        {/* ─── Included Services ─── */}
                        <div className="grid gap-2">
                            <div className="flex items-center justify-between">
                                <Label className="flex items-center gap-1.5">
                                    <ShieldCheck className="h-4 w-4 text-blue-500" />
                                    {t('premium_policies.services', 'Included Services')}
                                    <Badge variant="secondary" className="ml-1 text-[10px]">
                                        {selectedServiceIds.length} {t('common.selected', 'selected')}
                                    </Badge>
                                </Label>
                                <Link
                                    href="/dashboard/admin/services"
                                    target="_blank"
                                    className="text-xs text-primary hover:underline flex items-center gap-1"
                                >
                                    {t('premium_policies.manage_services', 'Manage Services')}
                                    <ExternalLink className="h-3 w-3" />
                                </Link>
                            </div>
                            {services.length > 0 ? (
                                <div className="border rounded-md p-3 max-h-48 overflow-y-auto space-y-2">
                                    {services.map((s) => (
                                        <div key={s.id} className="flex items-center justify-between py-0.5">
                                            <div className="flex items-center space-x-2">
                                                <Checkbox
                                                    id={`service-${s.id}`}
                                                    checked={selectedServiceIds.includes(s.id)}
                                                    onCheckedChange={() => toggleService(s.id)}
                                                />
                                                <label htmlFor={`service-${s.id}`} className="text-sm cursor-pointer">
                                                    {s.name_en}
                                                    {s.name_fr && (
                                                        <span className="text-muted-foreground ml-1">/ {s.name_fr}</span>
                                                    )}
                                                </label>
                                            </div>
                                            <Badge variant="outline" className="text-xs font-mono">
                                                {formatPrice(s.default_price)}
                                            </Badge>
                                        </div>
                                    ))}
                                </div>
                            ) : (
                                <div className="border rounded-md p-4 text-center text-sm text-muted-foreground">
                                    {t('premium_policies.no_services', 'No services defined yet.')}
                                    <Link
                                        href="/dashboard/admin/services"
                                        target="_blank"
                                        className="text-primary hover:underline ml-1"
                                    >
                                        {t('premium_policies.create_services_link', 'Create services first')}
                                    </Link>
                                </div>
                            )}
                        </div>
                    </div>
                )}

                <DialogFooter>
                    <Button variant="outline" onClick={() => onOpenChange(false)} disabled={saving}>
                        {t('common.cancel', 'Cancel')}
                    </Button>
                    <Button onClick={handleSubmit} disabled={saving || loadingData}>
                        {saving && <Loader2 className="mr-2 h-4 w-4 animate-spin" />}
                        {isEditing
                            ? t('common.save_changes', 'Save Changes')
                            : t('common.create', 'Create')}
                    </Button>
                </DialogFooter>
            </DialogContent>
        </Dialog>
    )
}
