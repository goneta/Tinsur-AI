/**
 * Policy form dialog for create/edit.
 */
'use client';

import { useState, useEffect, useMemo } from 'react';
import { useForm } from 'react-hook-form';
import { zodResolver } from '@hookform/resolvers/zod';
import * as z from 'zod';
import { format } from 'date-fns';
import { Check, Plus, X, Search } from 'lucide-react';

import { policyApi } from '@/lib/policy-api';
import { clientApi } from '@/lib/client-api';
import { policyTypeApi } from '@/lib/policy-type-api';
import { api } from '@/lib/api';
import { policyServiceApi, PolicyService } from '@/lib/policy-service-api';
import { useAuth } from '@/lib/auth';
import { useLanguage } from '@/contexts/language-context';
import { formatCurrency } from '@/lib/utils';

import { Policy, PolicyCreateRequest } from '@/types/policy';
import { Client } from '@/types/client';
import { PolicyType } from '@/types/policy-type';

import { Button } from '@/components/ui/button';
import {
    Dialog,
    DialogContent,
    DialogDescription,
    DialogHeader,
    DialogTitle,
} from '@/components/ui/dialog';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import {
    Select,
    SelectContent,
    SelectItem,
    SelectTrigger,
    SelectValue,
} from '@/components/ui/select';
import { Textarea } from '@/components/ui/textarea';
import { Popover, PopoverContent, PopoverTrigger } from '@/components/ui/popover';
import { Checkbox } from '@/components/ui/checkbox';
import { ScrollArea } from '@/components/ui/scroll-area';
import { Badge } from '@/components/ui/badge';
import { ServiceFormDialog } from './policy-service-form-dialog';

const policySchema = z.object({
    client_id: z.string().min(1, 'Client is required'),
    policy_type_id: z.string().min(1, 'Policy Type is required'),
    policy_number: z.string().optional(),
    coverage_amount: z.coerce.number().min(0).optional(),
    premium_amount: z.coerce.number().min(0, 'Premium amount is required'),
    premium_frequency: z.enum(['monthly', 'quarterly', 'semi-annual', 'annual']),
    start_date: z.string().min(1, 'Start date is required'),
    end_date: z.string().min(1, 'End date is required'),
    sales_agent_id: z.string().optional(),
    pos_location_id: z.string().optional(),
    notes: z.string().optional(),
});

type PolicyFormData = z.infer<typeof policySchema>;

interface PolicyFormDialogProps {
    open: boolean;
    onOpenChange: (open: boolean) => void;
    policy?: Policy;
    onSuccess: () => void;
}

export function PolicyFormDialog({
    open,
    onOpenChange,
    policy,
    onSuccess,
}: PolicyFormDialogProps) {
    const { t } = useLanguage();
    const { user } = useAuth();
    const [loading, setLoading] = useState(false);
    const [error, setError] = useState('');

    // Data Sources
    const [clients, setClients] = useState<Client[]>([]);
    const [policyTypes, setPolicyTypes] = useState<PolicyType[]>([]);
    const [employees, setEmployees] = useState<any[]>([]);
    const [posLocations, setPosLocations] = useState<any[]>([]);
    const [availableServices, setAvailableServices] = useState<PolicyService[]>([]);
    const [isLoadingData, setIsLoadingData] = useState(false);

    // Filter Logic
    const [serviceSearch, setServiceSearch] = useState('');
    const [isServiceOpen, setIsServiceOpen] = useState(false);
    const [isCreateServiceOpen, setIsCreateServiceOpen] = useState(false);

    // Selection State: Map of service_id -> price (initially default_price)
    // Using simple array of objects for easier handling
    const [selectedServices, setSelectedServices] = useState<{ id: string; price: number; name: string }[]>([]);

    const isEdit = !!policy;

    const {
        register,
        handleSubmit,
        setValue,
        watch,
        reset,
        formState: { errors },
    } = useForm<PolicyFormData>({
        resolver: zodResolver(policySchema),
        defaultValues: {
            premium_frequency: 'annual',
            start_date: new Date().toISOString().split('T')[0],
            end_date: new Date(new Date().setFullYear(new Date().getFullYear() + 1)).toISOString().split('T')[0],
        },
    });

    // Fetch initial data
    useEffect(() => {
        if (open) {
            const fetchData = async () => {
                setIsLoadingData(true);
                try {
                    const [clientsData, typesData, employeesRes, posRes] = await Promise.all([
                        clientApi.getClients({ limit: 100, status: 'active' }),
                        policyTypeApi.getPolicyTypes({ limit: 100, is_active: true }),
                        api.get('/employees/').then(res => res.data),
                        api.get('/pos/locations').then(res => res.data).catch(() => [])
                    ]);
                    setClients(clientsData || []);
                    setPolicyTypes(typesData || []);
                    setEmployees(employeesRes || []);
                    setPosLocations(posRes || []);

                    // Load Services
                    if (user?.company_id) {
                        const servicesData = await policyServiceApi.getAll({
                            company_id: user.company_id,
                            is_active: true
                        });
                        setAvailableServices(servicesData);
                    }
                } catch (err) {
                    console.error('Failed to load form data:', err);
                    setError('Failed to load required data');
                } finally {
                    setIsLoadingData(false);
                }
            };
            fetchData();
        }
    }, [open, user?.company_id]);

    // Reset/Set Form Values
    useEffect(() => {
        if (policy) {
            reset({
                client_id: policy.client_id,
                policy_type_id: policy.policy_type_id,
                policy_number: policy.policy_number,
                coverage_amount: policy.coverage_amount,
                premium_amount: policy.premium_amount,
                premium_frequency: policy.premium_frequency,
                start_date: policy.start_date,
                end_date: policy.end_date,
                sales_agent_id: policy.sales_agent_id,
                pos_location_id: policy.pos_location_id,
                notes: policy.notes,
            });
            // TODO: Load existing services if editing? 
            // Current backend schema update didn't include services in Policy Response fully yet
            // Assuming for now Create flow is main target for "Selection"
        } else {
            reset({
                premium_frequency: 'annual',
                start_date: new Date().toISOString().split('T')[0],
                end_date: new Date(new Date().setFullYear(new Date().getFullYear() + 1)).toISOString().split('T')[0],
            });
            setSelectedServices([]);
        }
    }, [policy, reset]);

    const refreshServices = async () => {
        if (user?.company_id) {
            const servicesData = await policyServiceApi.getAll({
                company_id: user.company_id,
                is_active: true
            });
            setAvailableServices(servicesData);
        }
    };

    const toggleService = (service: PolicyService) => {
        const exists = selectedServices.find(s => s.id === service.id);
        if (exists) {
            setSelectedServices(prev => prev.filter(s => s.id !== service.id));
        } else {
            setSelectedServices(prev => [...prev, {
                id: service.id,
                price: service.default_price,
                name: service.name_en
            }]);
        }
    };

    const filteredServices = useMemo(() => {
        return availableServices.filter(s =>
            s.name_en.toLowerCase().includes(serviceSearch.toLowerCase()) ||
            (s.name_fr && s.name_fr.toLowerCase().includes(serviceSearch.toLowerCase()))
        );
    }, [availableServices, serviceSearch]);

    const onSubmit = async (data: PolicyFormData) => {
        setError('');
        setLoading(true);

        try {
            const payload = {
                ...data,
                services: selectedServices.map(s => ({
                    service_id: s.id,
                    price: s.price
                }))
            };

            if (isEdit) {
                await policyApi.updatePolicy(policy.id, payload);
            } else {
                await policyApi.createPolicy(payload as unknown as PolicyCreateRequest);
            }
            onSuccess();
        } catch (err: any) {
            console.error(err);
            setError(err.response?.data?.detail || err.message || 'Operation failed');
        } finally {
            setLoading(false);
        }
    };

    return (
        <Dialog open={open} onOpenChange={onOpenChange}>
            <DialogContent className="max-w-3xl max-h-[90vh] overflow-y-auto">
                <DialogHeader>
                    <DialogTitle>{isEdit ? 'Edit Policy' : 'Create New Policy'}</DialogTitle>
                    <DialogDescription>
                        {isEdit ? 'Update policy details' : 'Issue a new insurance policy'}
                    </DialogDescription>
                </DialogHeader>

                <form onSubmit={handleSubmit(onSubmit)} className="space-y-6">
                    {error && (
                        <div className="rounded-md bg-red-50 p-3 text-sm text-red-800">
                            {error}
                        </div>
                    )}

                    {/* Standard Fields */}
                    <div className="grid grid-cols-2 gap-6">
                        <div className="space-y-2">
                            <Label htmlFor="client_id">Client *</Label>
                            <Select
                                value={watch('client_id')}
                                onValueChange={(value) => setValue('client_id', value)}
                                disabled={isLoadingData}
                            >
                                <SelectTrigger>
                                    <SelectValue placeholder={isLoadingData ? "Loading..." : "Select client"} />
                                </SelectTrigger>
                                <SelectContent>
                                    {clients.map((client) => (
                                        <SelectItem key={client.id} value={client.id}>
                                            {client.client_type === 'individual'
                                                ? `${client.first_name} ${client.last_name}`
                                                : client.business_name}
                                        </SelectItem>
                                    ))}
                                </SelectContent>
                            </Select>
                            {errors.client_id && <p className="text-sm text-red-600">{errors.client_id.message}</p>}
                        </div>

                        <div className="space-y-2">
                            <Label htmlFor="policy_type_id">Policy Type *</Label>
                            <Select
                                value={watch('policy_type_id')}
                                onValueChange={(value) => setValue('policy_type_id', value)}
                                disabled={isLoadingData}
                            >
                                <SelectTrigger>
                                    <SelectValue placeholder={isLoadingData ? "Loading..." : "Select type"} />
                                </SelectTrigger>
                                <SelectContent>
                                    {policyTypes.map((type) => (
                                        <SelectItem key={type.id} value={type.id}>
                                            {type.name} ({type.code})
                                        </SelectItem>
                                    ))}
                                </SelectContent>
                            </Select>
                            {errors.policy_type_id && <p className="text-sm text-red-600">{errors.policy_type_id.message}</p>}
                        </div>
                    </div>

                    <div className="grid grid-cols-2 gap-6">
                        <div className="space-y-2">
                            <Label htmlFor="sales_agent_id">Sales Agent</Label>
                            <Select
                                value={watch('sales_agent_id') || ''}
                                onValueChange={(value) => setValue('sales_agent_id', value)}
                            >
                                <SelectTrigger>
                                    <SelectValue placeholder="Select Agent" />
                                </SelectTrigger>
                                <SelectContent>
                                    {employees.map((emp) => (
                                        <SelectItem key={emp.id} value={emp.id}>
                                            {emp.first_name} {emp.last_name}
                                        </SelectItem>
                                    ))}
                                </SelectContent>
                            </Select>
                        </div>

                        <div className="space-y-2">
                            <Label htmlFor="pos_location_id">POS Location</Label>
                            <Select
                                value={watch('pos_location_id') || ''}
                                onValueChange={(value) => setValue('pos_location_id', value)}
                            >
                                <SelectTrigger>
                                    <SelectValue placeholder="Select POS" />
                                </SelectTrigger>
                                <SelectContent>
                                    {posLocations.map((pos) => (
                                        <SelectItem key={pos.id} value={pos.id}>
                                            {pos.name}
                                        </SelectItem>
                                    ))}
                                </SelectContent>
                            </Select>
                        </div>
                    </div>

                    {/* Policy Services Section */}
                    <div className="space-y-4 rounded-lg border p-4 bg-gray-50/50">
                        <div className="flex items-center justify-between">
                            <Label className="text-base font-semibold text-gray-900">{t('policyServices.title', 'Policy Services')}</Label>
                            <Popover open={isServiceOpen} onOpenChange={setIsServiceOpen}>
                                <PopoverTrigger asChild>
                                    <Button variant="outline" size="sm" className="h-8 border-dashed">
                                        <Plus className="mr-2 h-4 w-4" />
                                        {t('policyServices.add_service', 'Add Service')}
                                    </Button>
                                </PopoverTrigger>
                                <PopoverContent className="p-0 w-80" align="end">
                                    <div className="flex items-center border-b px-3">
                                        <Search className="mr-2 h-4 w-4 shrink-0 opacity-50" />
                                        <Input
                                            className="flex h-10 w-full rounded-md bg-transparent py-3 text-sm outline-none placeholder:text-muted-foreground disabled:cursor-not-allowed disabled:opacity-50 border-none shadow-none focus-visible:ring-0"
                                            placeholder={t('policyServices.search_placeholder', 'Search services...')}
                                            value={serviceSearch}
                                            onChange={(e) => setServiceSearch(e.target.value)}
                                        />
                                    </div>
                                    <ScrollArea className="h-60">
                                        <div className="p-2 space-y-1">
                                            {filteredServices.length === 0 ? (
                                                <div className="py-6 text-center text-sm text-muted-foreground">
                                                    No services found.
                                                    <Button
                                                        variant="link"
                                                        size="sm"
                                                        onClick={() => {
                                                            setIsCreateServiceOpen(true);
                                                            setIsServiceOpen(false);
                                                        }}
                                                        className="mt-2 text-primary"
                                                    >
                                                        {t('policyServices.add_custom', 'Add Custom Service')}
                                                    </Button>
                                                </div>
                                            ) : (
                                                filteredServices.map(service => {
                                                    const isSelected = selectedServices.some(s => s.id === service.id);
                                                    return (
                                                        <div
                                                            key={service.id}
                                                            className="flex items-center space-x-2 rounded-sm px-2 py-1.5 hover:bg-accent cursor-pointer"
                                                            onClick={() => toggleService(service)}
                                                        >
                                                            <Checkbox checked={isSelected} id={`svc-${service.id}`} />
                                                            <div className="flex-1 text-sm">
                                                                <p className="font-medium leading-none">{service.name_en}</p>
                                                                {service.name_fr && <p className="text-xs text-muted-foreground">{service.name_fr}</p>}
                                                            </div>
                                                            <Badge variant="secondary" className="text-xs">
                                                                +{formatCurrency(service.default_price)}
                                                            </Badge>
                                                        </div>
                                                    );
                                                })
                                            )}
                                        </div>
                                    </ScrollArea>
                                </PopoverContent>
                            </Popover>
                        </div>

                        {/* Selected Services Tags */}
                        {selectedServices.length > 0 && (
                            <div className="flex flex-wrap gap-2">
                                {selectedServices.map(s => (
                                    <Badge key={s.id} variant="secondary" className="pl-2 pr-1 py-1 flex items-center gap-1">
                                        <span>{s.name}</span>
                                        <span className="ml-1 text-xs text-muted-foreground">
                                            ({formatCurrency(s.price)})
                                        </span>
                                        <Button
                                            variant="ghost"
                                            size="icon"
                                            className="h-4 w-4 ml-1 hover:bg-transparent hover:text-destructive"
                                            onClick={() => toggleService({ id: s.id } as PolicyService)}
                                        >
                                            <X className="h-3 w-3" />
                                        </Button>
                                    </Badge>
                                ))}
                            </div>
                        )}
                        <p className="text-sm text-muted-foreground">{t('subtitle')}</p>
                    </div>

                    <div className="grid grid-cols-3 gap-4">
                        <div className="space-y-2">
                            <Label htmlFor="premium_amount">Premium Amount *</Label>
                            <Input
                                id="premium_amount"
                                type="number"
                                step="0.01"
                                {...register('premium_amount')}
                            />
                            {errors.premium_amount && (
                                <p className="text-sm text-red-600">{errors.premium_amount.message}</p>
                            )}
                        </div>

                        <div className="space-y-2">
                            <Label htmlFor="coverage_amount">Coverage Amount</Label>
                            <Input
                                id="coverage_amount"
                                type="number"
                                step="0.01"
                                {...register('coverage_amount')}
                            />
                        </div>

                        <div className="space-y-2">
                            <Label htmlFor="premium_frequency">Frequency</Label>
                            <Select
                                value={watch('premium_frequency')}
                                onValueChange={(value) => setValue('premium_frequency', value as any)}
                            >
                                <SelectTrigger>
                                    <SelectValue />
                                </SelectTrigger>
                                <SelectContent>
                                    <SelectItem value="monthly">Monthly</SelectItem>
                                    <SelectItem value="quarterly">Quarterly</SelectItem>
                                    <SelectItem value="semi-annual">Semi-Annual</SelectItem>
                                    <SelectItem value="annual">Annual</SelectItem>
                                </SelectContent>
                            </Select>
                        </div>
                    </div>

                    <div className="grid grid-cols-2 gap-6">
                        <div className="space-y-2">
                            <Label htmlFor="start_date">Start Date</Label>
                            <Input
                                id="start_date"
                                type="date"
                                {...register('start_date')}
                            />
                            {errors.start_date && <p className="text-sm text-red-600">{errors.start_date.message}</p>}
                        </div>

                        <div className="space-y-2">
                            <Label htmlFor="end_date">End Date</Label>
                            <Input
                                id="end_date"
                                type="date"
                                {...register('end_date')}
                            />
                            {errors.end_date && <p className="text-sm text-red-600">{errors.end_date.message}</p>}
                        </div>
                    </div>

                    <div className="space-y-2">
                        <Label htmlFor="notes">Notes</Label>
                        <Textarea
                            id="notes"
                            {...register('notes')}
                            placeholder="Additional notes..."
                        />
                    </div>

                    <div className="flex justify-end gap-2 pt-4 border-t">
                        <Button
                            type="button"
                            variant="outline"
                            onClick={() => onOpenChange(false)}
                            disabled={loading}
                        >
                            Cancel
                        </Button>
                        <Button type="submit" disabled={loading}>
                            {loading ? 'Saving...' : isEdit ? 'Update Policy' : 'Create Policy'}
                        </Button>
                    </div>
                </form>
            </DialogContent>

            <ServiceFormDialog
                open={isCreateServiceOpen}
                onOpenChange={setIsCreateServiceOpen}
                companyId={user?.company_id || ''}
                onSuccess={() => {
                    refreshServices();
                    // Optionally auto-select the new service?
                    // For now, just refresh the list.
                }}
            />
        </Dialog >
    );
}
