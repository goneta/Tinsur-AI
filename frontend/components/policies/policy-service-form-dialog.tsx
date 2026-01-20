'use client';

import { useState, useEffect } from 'react';
import { useForm } from 'react-hook-form';
import { zodResolver } from '@hookform/resolvers/zod';
import * as z from 'zod';


import {
    Dialog,
    DialogContent,
    DialogDescription,
    DialogHeader,
    DialogTitle,
    DialogFooter
} from '@/components/ui/dialog';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { Textarea } from '@/components/ui/textarea';
import { Switch } from '@/components/ui/switch';
import { policyServiceApi, PolicyService } from '@/lib/policy-service-api';

const serviceSchema = z.object({
    name_en: z.string().min(1, 'Name (EN) is required'),
    name_fr: z.string().optional(),
    description: z.string().optional(),
    default_price: z.coerce.number().min(0, 'Price must be positive'),
    is_active: z.boolean().optional(),
});

type ServiceFormData = z.infer<typeof serviceSchema>;

interface ServiceFormDialogProps {
    open: boolean;
    onOpenChange: (open: boolean) => void;
    service?: PolicyService | null;
    companyId: string;
    onSuccess: () => void;
}

export function ServiceFormDialog({
    open,
    onOpenChange,
    service,
    companyId,
    onSuccess
}: ServiceFormDialogProps) {
    const isEdit = !!service;
    const [loading, setLoading] = useState(false);
    const [error, setError] = useState('');

    const {
        register,
        handleSubmit,
        reset,
        setValue,
        watch,
        formState: { errors },
    } = useForm<ServiceFormData>({
        resolver: zodResolver(serviceSchema),
        defaultValues: {
            is_active: true,
            default_price: 0,
        },
    });

    useEffect(() => {
        if (service) {
            reset({
                name_en: service.name_en,
                name_fr: service.name_fr || '',
                description: service.description || '',
                default_price: service.default_price,
                is_active: service.is_active,
            });
        } else {
            reset({
                name_en: '',
                name_fr: '',
                description: '',
                default_price: 0,
                is_active: true,
            });
        }
    }, [service, reset]);

    const onSubmit = async (data: ServiceFormData) => {
        setLoading(true);
        setError('');
        try {
            if (isEdit && service) {
                await policyServiceApi.update(service.id, {
                    ...data,
                });
            } else {
                await policyServiceApi.create({
                    ...data,
                    is_active: data.is_active ?? true,
                    company_id: companyId,
                });
            }
            onSuccess();
            onOpenChange(false);
        } catch (err: any) {
            console.error(err);
            setError('Failed to save service');
        } finally {
            setLoading(false);
        }
    };

    return (
        <Dialog open={open} onOpenChange={onOpenChange}>
            <DialogContent>
                <DialogHeader>
                    <DialogTitle>{isEdit ? 'Edit Service' : 'Add New Service'}</DialogTitle>
                    <DialogDescription>
                        Configuration for policy optional services.
                    </DialogDescription>
                </DialogHeader>

                <form onSubmit={handleSubmit(onSubmit)} className="space-y-4">
                    {error && <div className="text-sm text-red-500">{error}</div>}

                    <div className="space-y-2">
                        <Label htmlFor="name_en">Name (English) *</Label>
                        <Input id="name_en" {...register('name_en')} />
                        {errors.name_en && <p className="text-sm text-red-500">{errors.name_en.message}</p>}
                    </div>

                    <div className="space-y-2">
                        <Label htmlFor="name_fr">Name (French)</Label>
                        <Input id="name_fr" {...register('name_fr')} />
                    </div>

                    <div className="space-y-2">
                        <Label htmlFor="default_price">Default Price *</Label>
                        <Input
                            id="default_price"
                            type="number"
                            step="0.01"
                            {...register('default_price')}
                        />
                        {errors.default_price && <p className="text-sm text-red-500">{errors.default_price.message}</p>}
                    </div>

                    <div className="space-y-2">
                        <Label htmlFor="description">Description</Label>
                        <Textarea id="description" {...register('description')} />
                    </div>

                    <div className="flex items-center space-x-2">
                        <Switch
                            id="is_active"
                            checked={watch('is_active')}
                            onCheckedChange={(checked) => setValue('is_active', checked)}
                        />
                        <Label htmlFor="is_active">Active</Label>
                    </div>

                    <DialogFooter>
                        <Button type="button" variant="outline" onClick={() => onOpenChange(false)}>
                            Cancel
                        </Button>
                        <Button type="submit" disabled={loading}>
                            {loading ? 'Saving...' : 'Save'}
                        </Button>
                    </DialogFooter>
                </form>
            </DialogContent>
        </Dialog>
    );
}
