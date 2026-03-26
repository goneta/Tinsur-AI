"use client"

import { useState, useEffect } from 'react'
import { useForm } from 'react-hook-form'
import { zodResolver } from '@hookform/resolvers/zod'
import * as z from 'zod'
import {
    Dialog,
    DialogContent,
    DialogDescription,
    DialogHeader,
    DialogTitle,
} from '@/components/ui/dialog'
import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
import { Label } from '@/components/ui/label'
import { Checkbox } from '@/components/ui/checkbox'
import { ScrollArea } from '@/components/ui/scroll-area'
import { useToast } from '@/components/ui/use-toast'
import { Plus, Trash2, Loader2, Pencil } from 'lucide-react'
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs'
import { premiumPolicyApi, PremiumPolicyType, PremiumPolicyCriteria } from '@/lib/premium-policy-api'
import { policyServiceApi, PolicyService } from '@/lib/policy-service-api'
import { useAuth } from '@/lib/auth'
import { CriteriaForm } from './criteria-form'

const policyTypeSchema = z.object({
    name: z.string().min(1, 'Name is required'),
    description: z.string().optional(),
    price: z.coerce.number().min(0, 'Price must be positive'),
    excess: z.coerce.number().min(0, 'Excess must be positive'),
    is_active: z.boolean().default(true),
    criteria_ids: z.array(z.string()).min(1, 'At least one criteria is required'),
    service_ids: z.array(z.string()).default([]),
})

type PolicyTypeFormData = z.infer<typeof policyTypeSchema>

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
    const [loading, setLoading] = useState(false)
    const [criteria, setCriteria] = useState<PremiumPolicyCriteria[]>([])
    const [isCriteriaFormOpen, setIsCriteriaFormOpen] = useState(false)
    const [editingCriteria, setEditingCriteria] = useState<PremiumPolicyCriteria | undefined>()
    const [services, setServices] = useState<PolicyService[]>([])
    const { user } = useAuth()
    const { toast } = useToast()
    const isEdit = !!policyType

    const {
        register,
        handleSubmit,
        setValue,
        watch,
        reset,
        formState: { errors },
    } = useForm({
        resolver: zodResolver(policyTypeSchema),
        defaultValues: {
            name: '',
            description: '',
            price: 0,
            excess: 0,
            is_active: true,
            criteria_ids: [],
            service_ids: [],
        },
    })

    const selectedCriteriaIds = watch('criteria_ids')
    const selectedServiceIds = watch('service_ids')

    useEffect(() => {
        if (open) {
            loadCriteria()
            loadServices()
            if (policyType) {
                reset({
                    name: policyType.name,
                    description: policyType.description || '',
                    price: policyType.price,
                    excess: policyType.excess,
                    is_active: policyType.is_active,
                    criteria_ids: policyType.criteria.map(c => c.id),
                    service_ids: policyType.services?.map(s => s.id) || [],
                })
            } else {
                reset({
                    name: '',
                    description: '',
                    price: 0,
                    excess: 0,
                    is_active: true,
                    criteria_ids: [],
                    service_ids: [],
                })
            }
        }
    }, [open, policyType, reset])

    const loadServices = async () => {
        if (!user?.company_id) return
        try {
            const data = await policyServiceApi.getAll({ company_id: user.company_id })
            setServices(data)
        } catch (error) {
            console.error('Failed to load services:', error)
        }
    }

    const loadCriteria = async () => {
        try {
            const data = await premiumPolicyApi.getCriteria()
            setCriteria(data)
        } catch (error) {
            console.error('Failed to load criteria:', error)
        }
    }

    const onSubmit = async (data: PolicyTypeFormData) => {
        setLoading(true)
        try {
            if (isEdit && policyType) {
                await premiumPolicyApi.updatePolicyType(policyType.id, data)
                toast({ title: 'Success', description: 'Policy type updated successfully' })
            } else {
                await premiumPolicyApi.createPolicyType(data)
                toast({ title: 'Success', description: 'Policy type created successfully' })
            }
            onSuccess()
            onOpenChange(false)
        } catch (error: any) {
            toast({
                title: 'Error',
                description: error.response?.data?.detail || 'Operation failed',
                variant: 'destructive',
            })
        } finally {
            setLoading(false)
        }
    }

    const toggleCriteria = (id: string, checked: boolean) => {
        const current = [...selectedCriteriaIds]
        if (checked) {
            setValue('criteria_ids', [...current, id])
        } else {
            setValue('criteria_ids', current.filter((i) => i !== id))
        }
    }

    const handleDeleteCriteria = async (id: string) => {
        if (!confirm('Are you sure you want to delete this criteria? It will be removed from all policy types.')) return
        try {
            await premiumPolicyApi.deleteCriteria(id)
            setCriteria(criteria.filter(c => c.id !== id))
            setValue('criteria_ids', selectedCriteriaIds.filter(i => i !== id))
            toast({ title: 'Success', description: 'Criteria deleted' })
        } catch (error) {
            toast({ title: 'Error', description: 'Failed to delete criteria', variant: 'destructive' })
        }
    }

    const toggleService = (id: string, checked: boolean) => {
        const current = [...(selectedServiceIds || [])]
        if (checked) {
            setValue('service_ids', [...current, id])
        } else {
            setValue('service_ids', current.filter((i) => i !== id))
        }
    }

    return (
        <Dialog open={open} onOpenChange={onOpenChange}>
            <DialogContent className="max-w-2xl max-h-[90vh] flex flex-col">
                <DialogHeader>
                    <DialogTitle>{isEdit ? 'Edit Premium Policy Type' : 'Create Premium Policy Type'}</DialogTitle>
                    <DialogDescription>
                        Configure pricing and eligibility criteria for this policy type.
                    </DialogDescription>
                </DialogHeader>

                <form onSubmit={handleSubmit(onSubmit)} className="flex-1 overflow-hidden flex flex-col">
                    <Tabs defaultValue="general" className="flex-1 flex flex-col overflow-hidden">
                        <div className="px-6">
                            <TabsList className="grid w-full grid-cols-3">
                                <TabsTrigger value="general">General</TabsTrigger>
                                <TabsTrigger value="criteria">Eligibility Criteria</TabsTrigger>
                                <TabsTrigger value="services">Included Services</TabsTrigger>
                            </TabsList>
                        </div>

                        <ScrollArea className="flex-1 p-6">
                            <TabsContent value="general" className="space-y-6 mt-0">
                                <div className="grid grid-cols-2 gap-4">
                                    <div className="space-y-2">
                                        <Label>Name</Label>
                                        <Input {...register('name')} placeholder="e.g. Premium Gold" />
                                        {errors.name && <p className="text-sm text-red-500">{errors.name.message}</p>}
                                    </div>
                                    <div className="space-y-2">
                                        <Label>Price (FCFA)</Label>
                                        <Input type="number" {...register('price')} placeholder="50000" />
                                        {errors.price && <p className="text-sm text-red-500">{errors.price.message}</p>}
                                    </div>
                                    <div className="space-y-2">
                                        <Label>Excess</Label>
                                        <Input type="number" {...register('excess')} placeholder="0" />
                                        {errors.excess && <p className="text-sm text-red-500">{errors.excess.message}</p>}
                                    </div>
                                </div>

                                <div className="space-y-2">
                                    <Label>Description</Label>
                                    <Input {...register('description')} placeholder="Description of this policy level" />
                                </div>
                            </TabsContent>

                            <TabsContent value="criteria" className="space-y-4 mt-0">
                                <div className="flex items-center justify-between">
                                    <Label className="text-base font-semibold">Eligibility Criteria</Label>
                                    <Button
                                        type="button"
                                        variant="outline"
                                        size="sm"
                                        onClick={() => {
                                            setEditingCriteria(undefined)
                                            setIsCriteriaFormOpen(true)
                                        }}
                                    >
                                        <Plus className="h-4 w-4 mr-2" />
                                        Add Criteria
                                    </Button>
                                </div>
                                {errors.criteria_ids && <p className="text-sm text-red-500">{errors.criteria_ids.message}</p>}

                                <Card className="p-0 overflow-hidden border">
                                    <div className="space-y-0 divide-y">
                                        {criteria.length === 0 && (
                                            <p className="text-center text-muted-foreground py-8">No criteria defined yet.</p>
                                        )}
                                        {criteria.map((c) => (
                                            <div key={c.id} className="flex items-center justify-between group p-3 hover:bg-muted/50 transition-colors">
                                                <div className="flex items-center space-x-3">
                                                    <Checkbox
                                                        id={`criteria-${c.id}`}
                                                        checked={selectedCriteriaIds.includes(c.id)}
                                                        onCheckedChange={(checked) => toggleCriteria(c.id, !!checked)}
                                                    />
                                                    <label
                                                        htmlFor={`criteria-${c.id}`}
                                                        className="text-sm font-medium leading-none cursor-pointer select-none"
                                                    >
                                                        <div className="font-bold">{c.name}</div>
                                                        <div className="text-xs text-muted-foreground">
                                                            {c.field_name} {c.operator} {c.value}
                                                        </div>
                                                    </label>
                                                </div>
                                                <div className="flex items-center opacity-0 group-hover:opacity-100 transition-opacity">
                                                    <Button
                                                        type="button"
                                                        variant="ghost"
                                                        size="icon"
                                                        className="h-8 w-8"
                                                        onClick={() => {
                                                            setEditingCriteria(c)
                                                            setIsCriteriaFormOpen(true)
                                                        }}
                                                    >
                                                        <Pencil className="h-3.5 w-3.5" />
                                                    </Button>
                                                    <Button
                                                        type="button"
                                                        variant="ghost"
                                                        size="icon"
                                                        className="h-8 w-8 text-destructive"
                                                        onClick={() => handleDeleteCriteria(c.id)}
                                                    >
                                                        <Trash2 className="h-3.5 w-3.5" />
                                                    </Button>
                                                </div>
                                            </div>
                                        ))}
                                    </div>
                                </Card>
                            </TabsContent>

                            <TabsContent value="services" className="space-y-4 mt-0">
                                <div className="space-y-2">
                                    <Label className="text-base font-semibold">Included Services</Label>
                                    <p className="text-sm text-muted-foreground">Select services that are automatically included in this policy.</p>
                                </div>
                                <Card className="p-0 overflow-hidden border">
                                    <div className="space-y-0 divide-y">
                                        {services.length === 0 && (
                                            <div className="text-center py-8 text-muted-foreground">
                                                No policy services found. Add them in Settings.
                                            </div>
                                        )}
                                        {services.map((service) => (
                                            <div key={service.id} className="flex items-center justify-between p-3 hover:bg-muted/50 transition-colors">
                                                <div className="flex items-center space-x-3">
                                                    <Checkbox
                                                        id={`service-${service.id}`}
                                                        checked={selectedServiceIds?.includes(service.id)}
                                                        onCheckedChange={(checked) => toggleService(service.id, !!checked)}
                                                    />
                                                    <label
                                                        htmlFor={`service-${service.id}`}
                                                        className="text-sm font-medium leading-none cursor-pointer select-none"
                                                    >
                                                        <div className="font-bold">{service.name_en}</div>
                                                        {service.name_fr && (
                                                            <div className="text-xs text-muted-foreground">{service.name_fr}</div>
                                                        )}
                                                    </label>
                                                </div>
                                                <div className="text-sm font-medium">
                                                    {new Intl.NumberFormat('en-US', { style: 'currency', currency: 'GBP' }).format(service.default_price)}
                                                </div>
                                            </div>
                                        ))}
                                    </div>
                                </Card>
                            </TabsContent>
                        </ScrollArea>
                    </Tabs>

                    <div className="flex justify-end gap-3 pt-4">
                        <Button type="button" variant="outline" onClick={() => onOpenChange(false)}>
                            Cancel
                        </Button>
                        <Button type="submit" disabled={loading}>
                            {loading ? <Loader2 className="h-4 w-4 animate-spin mr-2" /> : null}
                            {isEdit ? 'Update Policy' : 'Create Policy'}
                        </Button>
                    </div>
                </form>
            </DialogContent>

            <CriteriaForm
                open={isCriteriaFormOpen}
                onOpenChange={setIsCriteriaFormOpen}
                criteria={editingCriteria}
                onSuccess={() => {
                    loadCriteria()
                    setIsCriteriaFormOpen(false)
                }}
            />
        </Dialog>
    )
}

function Card({ children, className, ...props }: React.HTMLAttributes<HTMLDivElement>) {
    return (
        <div className={`rounded-lg border bg-card text-card-foreground shadow-sm ${className}`} {...props}>
            {children}
        </div>
    )
}
