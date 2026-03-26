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
import {
    Select,
    SelectContent,
    SelectItem,
    SelectTrigger,
    SelectValue,
} from '@/components/ui/select'
import { useToast } from '@/components/ui/use-toast'
import { Loader2 } from 'lucide-react'
import { premiumPolicyApi, PremiumPolicyCriteria } from '@/lib/premium-policy-api'

const criteriaSchema = z.object({
    name: z.string().min(1, 'Name is required'),
    description: z.string().optional(),
    field_name: z.string().min(1, 'Field name is required'),
    operator: z.string().min(1, 'Operator is required'),
    value: z.string().min(1, 'Value is required'),
})

type CriteriaFormData = z.infer<typeof criteriaSchema>

interface CriteriaFormProps {
    open: boolean
    onOpenChange: (open: boolean) => void
    criteria?: PremiumPolicyCriteria
    onSuccess: () => void
}

export function CriteriaForm({
    open,
    onOpenChange,
    criteria,
    onSuccess,
}: CriteriaFormProps) {
    const [loading, setLoading] = useState(false)
    const { toast } = useToast()
    const isEdit = !!criteria

    const {
        register,
        handleSubmit,
        setValue,
        watch,
        reset,
        formState: { errors },
    } = useForm<CriteriaFormData>({
        resolver: zodResolver(criteriaSchema),
        defaultValues: {
            name: '',
            description: '',
            field_name: '',
            operator: '=',
            value: '',
        },
    })

    useEffect(() => {
        if (open) {
            if (criteria) {
                reset({
                    name: criteria.name,
                    description: criteria.description || '',
                    field_name: criteria.field_name,
                    operator: criteria.operator,
                    value: criteria.value,
                })
            } else {
                reset({
                    name: '',
                    description: '',
                    field_name: '',
                    operator: '=',
                    value: '',
                })
            }
        }
    }, [open, criteria, reset])

    const onSubmit = async (data: CriteriaFormData) => {
        setLoading(true)
        try {
            if (isEdit && criteria) {
                await premiumPolicyApi.updateCriteria(criteria.id, data)
                toast({ title: 'Success', description: 'Criteria updated successfully' })
            } else {
                await premiumPolicyApi.createCriteria(data)
                toast({ title: 'Success', description: 'Criteria created successfully' })
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

    return (
        <Dialog open={open} onOpenChange={onOpenChange}>
            <DialogContent className="max-w-md">
                <DialogHeader>
                    <DialogTitle>{isEdit ? 'Edit Criteria' : 'Add New Criteria'}</DialogTitle>
                    <DialogDescription>
                        Define a reusable eligibility rule.
                    </DialogDescription>
                </DialogHeader>

                <form onSubmit={handleSubmit(onSubmit)} className="space-y-4">
                    <div className="space-y-2">
                        <Label>Criteria Name</Label>
                        <Input {...register('name')} placeholder="e.g. Low Accident Count" />
                        {errors.name && <p className="text-sm text-red-500">{errors.name.message}</p>}
                    </div>

                    <div className="grid grid-cols-2 gap-4">
                        <div className="space-y-2">
                            <Label>Field Name</Label>
                            <Select
                                value={watch('field_name')}
                                onValueChange={(val) => setValue('field_name', val)}
                            >
                                <SelectTrigger>
                                    <SelectValue placeholder="Select field" />
                                </SelectTrigger>
                                <SelectContent>
                                    <SelectItem value="accidents_not_fault">Accidents (Not Fault)</SelectItem>
                                    <SelectItem value="accidents_fault">Accidents (At Fault)</SelectItem>
                                    <SelectItem value="car_age">Car Age (Years)</SelectItem>
                                    <SelectItem value="mileage">Mileage (KM)</SelectItem>
                                    <SelectItem value="no_claims_bonus">No-Claims Bonus (Years)</SelectItem>
                                    <SelectItem value="license_years">License Duration (Years)</SelectItem>
                                </SelectContent>
                            </Select>
                            {errors.field_name && <p className="text-sm text-red-500">{errors.field_name.message}</p>}
                        </div>
                        <div className="space-y-2">
                            <Label>Operator</Label>
                            <Select
                                value={watch('operator')}
                                onValueChange={(val) => setValue('operator', val)}
                            >
                                <SelectTrigger>
                                    <SelectValue placeholder="Select operator" />
                                </SelectTrigger>
                                <SelectContent>
                                    <SelectItem value="=">Equals (=)</SelectItem>
                                    <SelectItem value=">">Greater than (&gt;)</SelectItem>
                                    <SelectItem value="<">Less than (&lt;)</SelectItem>
                                    <SelectItem value=">=">Greater or Equal (&gt;=)</SelectItem>
                                    <SelectItem value="<=">Less or Equal (&lt;=)</SelectItem>
                                    <SelectItem value="between">Between (low,high)</SelectItem>
                                </SelectContent>
                            </Select>
                        </div>
                    </div>

                    <div className="space-y-2">
                        <Label>Value</Label>
                        <Input {...register('value')} placeholder="e.g. 5, or 0,1 for between" />
                        <p className="text-[10px] text-muted-foreground">Use comma separation for 'between' operator (e.g. 0,2)</p>
                        {errors.value && <p className="text-sm text-red-500">{errors.value.message}</p>}
                    </div>

                    <div className="flex justify-end gap-3 pt-4">
                        <Button type="button" variant="outline" onClick={() => onOpenChange(false)}>
                            Cancel
                        </Button>
                        <Button type="submit" disabled={loading}>
                            {loading ? <Loader2 className="h-4 w-4 animate-spin mr-2" /> : null}
                            {isEdit ? 'Update' : 'Add Criteria'}
                        </Button>
                    </div>
                </form>
            </DialogContent>
        </Dialog>
    )
}
