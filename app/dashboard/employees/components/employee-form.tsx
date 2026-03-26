'use client';

import { useState, useEffect } from 'react';
import { useForm } from 'react-hook-form';
import { zodResolver } from '@hookform/resolvers/zod';
import * as z from 'zod';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select';
import { Loader2 } from 'lucide-react';
import { api } from '@/lib/api';
import { useToast } from '@/components/ui/use-toast';

const employeeSchema = z.object({
    first_name: z.string().min(2, "First name is required"),
    last_name: z.string().min(2, "Last name is required"),
    email: z.string().email("Invalid email address"),
    phone: z.string().optional().or(z.literal('')),
    role: z.string().optional().default("agent"),
    created_by: z.string().optional().or(z.literal('')),
    pos_location_id: z.string().optional().or(z.literal('')),
    profile: z.object({
        job_title: z.string().optional().or(z.literal('')),
        department: z.string().optional().or(z.literal('')),
        base_salary: z.preprocess((val) => Number(val), z.number().min(0).optional()),
        payment_method: z.string().optional().default("bank_transfer"),
        mobile_money_provider: z.string().optional().or(z.literal('')),
        mobile_money_number: z.string().optional().or(z.literal('')),
        bank_name: z.string().optional().or(z.literal('')),
        bank_account_number: z.string().optional().or(z.literal('')),
        bank_account_holder_name: z.string().optional().or(z.literal('')),
        iban: z.string().optional().or(z.literal('')),
        swift_bic: z.string().optional().or(z.literal('')),
        currency: z.string().optional().default("XOF")
    }).optional()
});

type EmployeeFormValues = z.infer<typeof employeeSchema>;

interface EmployeeFormProps {
    onSuccess: () => void;
    initialData?: any;
    mode?: 'create' | 'edit';
}

export function EmployeeForm({ onSuccess, initialData, mode = 'create' }: EmployeeFormProps) {
    const [loading, setLoading] = useState(false);
    const [employees, setEmployees] = useState<any[]>([]);
    const [posLocations, setPosLocations] = useState<any[]>([]);
    const { toast } = useToast();

    const form = useForm({
        resolver: zodResolver(employeeSchema),
        defaultValues: {
            first_name: initialData?.first_name || "",
            last_name: initialData?.last_name || "",
            email: initialData?.email || "",
            phone: initialData?.phone || "",
            role: initialData?.role || "agent",
            created_by: initialData?.created_by || "",
            pos_location_id: initialData?.pos_location?.id || initialData?.pos_location_id || "",
            profile: {
                payment_method: initialData?.profile?.payment_method || initialData?.employee_profile?.payment_method || "bank_transfer",
                currency: initialData?.profile?.currency || initialData?.employee_profile?.currency || "XOF",
                base_salary: (initialData?.profile?.base_salary || initialData?.employee_profile?.base_salary) || 0,
                job_title: initialData?.profile?.job_title || initialData?.employee_profile?.job_title || "",
                department: initialData?.profile?.department || initialData?.employee_profile?.department || "",
                mobile_money_provider: initialData?.profile?.mobile_money_provider || initialData?.employee_profile?.mobile_money_provider || "",
                mobile_money_number: initialData?.profile?.mobile_money_number || initialData?.employee_profile?.mobile_money_number || "",
                bank_name: initialData?.profile?.bank_name || initialData?.employee_profile?.bank_name || "",
                bank_account_number: initialData?.profile?.bank_account_number || initialData?.employee_profile?.bank_account_number || "",
                bank_account_holder_name: initialData?.profile?.bank_account_holder_name || initialData?.employee_profile?.bank_account_holder_name || "",
                iban: initialData?.profile?.iban || initialData?.employee_profile?.iban || "",
                swift_bic: initialData?.profile?.swift_bic || initialData?.employee_profile?.swift_bic || ""
            }
        }
    });

    const paymentMethod = form.watch('profile.payment_method');

    useEffect(() => {
        const loadData = async () => {
            try {
                const [empRes, posRes] = await Promise.all([
                    api.get('/employees/'),
                    api.get('/pos/locations')
                ]);
                setEmployees(empRes.data);
                setPosLocations(posRes.data);
            } catch (e) {
                console.error("Failed to load form data:", e);
            }
        };
        loadData();
    }, []);

    const onSubmit = async (data: any) => {
        setLoading(true);

        try {
            // Prepare payload
            const payload = {
                ...data,
                // Handle optional/empty fields
                created_by: data.created_by === 'none' || !data.created_by ? null : data.created_by,
                pos_location_id: data.pos_location_id === 'none' || !data.pos_location_id ? null : data.pos_location_id,
                profile: {
                    ...data.profile,
                    base_salary: Number(data.profile?.base_salary || 0)
                }
            };

            if (mode === 'create') {
                await api.post('/employees/', {
                    ...payload,
                    password: "Password123!" // Default password
                });
            } else {
                await api.put(`/employees/${initialData.id}`, payload);
            }

            toast({
                title: 'Success',
                description: `Employee ${mode === 'create' ? 'created' : 'updated'} successfully.`,
            });
            onSuccess();
        } catch (error: any) {
            console.error("Employee Submission Error:", error);
            const msg = error.response?.data?.detail || error.message || 'Failed to save employee';
            toast({
                title: 'Error',
                description: msg,
                variant: 'destructive',
            });
        } finally {
            setLoading(false);
        }
    };

    return (
        <form onSubmit={form.handleSubmit(onSubmit)} className="space-y-6">
            <div className="grid gap-4 md:grid-cols-2">
                <div className="space-y-2">
                    <Label htmlFor="first_name">First Name</Label>
                    <Input id="first_name" {...form.register('first_name')} />
                    {form.formState.errors.first_name && (
                        <p className="text-sm text-red-500">{form.formState.errors.first_name.message}</p>
                    )}
                </div>

                <div className="space-y-2">
                    <Label htmlFor="last_name">Last Name</Label>
                    <Input id="last_name" {...form.register('last_name')} />
                    {form.formState.errors.last_name && (
                        <p className="text-sm text-red-500">{form.formState.errors.last_name.message}</p>
                    )}
                </div>

                <div className="space-y-2">
                    <Label htmlFor="email">Email</Label>
                    <Input id="email" type="email" {...form.register('email')} disabled={mode === 'edit'} />
                    {form.formState.errors.email && (
                        <p className="text-sm text-red-500">{form.formState.errors.email.message}</p>
                    )}
                </div>

                <div className="space-y-2">
                    <Label htmlFor="phone">Phone</Label>
                    <Input id="phone" {...form.register('phone')} />
                </div>

                <div className="space-y-2">
                    <Label htmlFor="role">Role</Label>
                    <Select
                        onValueChange={(val) => form.setValue('role', val)}
                        defaultValue={form.getValues('role')}
                    >
                        <SelectTrigger>
                            <SelectValue placeholder="Select Role" />
                        </SelectTrigger>
                        <SelectContent>
                            <SelectItem value="admin">Admin</SelectItem>
                            <SelectItem value="manager">Manager</SelectItem>
                            <SelectItem value="agent">Agent</SelectItem>
                            <SelectItem value="receptionist">Receptionist</SelectItem>
                        </SelectContent>
                    </Select>
                </div>

                <div className="space-y-2">
                    <Label htmlFor="pos_location">POS Location</Label>
                    <Select
                        onValueChange={(val) => form.setValue('pos_location_id', val)}
                        defaultValue={form.getValues('pos_location_id')}
                    >
                        <SelectTrigger>
                            <SelectValue placeholder="Select POS Location" />
                        </SelectTrigger>
                        <SelectContent>
                            <SelectItem value="none">None</SelectItem>
                            {posLocations.map(pos => (
                                <SelectItem key={pos.id} value={pos.id}>
                                    {pos.name} ({pos.city || 'No City'})
                                </SelectItem>
                            ))}
                        </SelectContent>
                    </Select>
                </div>

                <div className="space-y-2">
                    <Label htmlFor="created_by">Recruited By</Label>
                    <Select
                        onValueChange={(val) => form.setValue('created_by', val)}
                        defaultValue={form.getValues('created_by')}
                    >
                        <SelectTrigger>
                            <SelectValue placeholder="Select Recruiter" />
                        </SelectTrigger>
                        <SelectContent>
                            <SelectItem value="none">None</SelectItem>
                            {employees.map(emp => (
                                <SelectItem key={emp.id} value={emp.id}>
                                    {emp.first_name} {emp.last_name}
                                </SelectItem>
                            ))}
                        </SelectContent>
                    </Select>
                </div>

                {/* Profile Fields */}
                <div className="space-y-2">
                    <Label htmlFor="job_title">Job Title</Label>
                    <Input id="job_title" {...form.register('profile.job_title')} />
                </div>
                <div className="space-y-2">
                    <Label htmlFor="department">Department</Label>
                    <Input id="department" {...form.register('profile.department')} />
                </div>
                <div className="space-y-2">
                    <Label htmlFor="base_salary">Base Salary (XOF)</Label>
                    <Input
                        id="base_salary"
                        type="number"
                        {...form.register('profile.base_salary')}
                    />
                </div>
            </div>

            <div className="rounded-md border p-4 bg-muted/20">
                <h3 className="mb-4 text-lg font-medium">Payment Details</h3>
                <div className="grid gap-4 md:grid-cols-2">
                    <div className="space-y-2">
                        <Label htmlFor="payment_method">Payment Method</Label>
                        <Select
                            onValueChange={(val) => form.setValue('profile.payment_method', val)}
                            defaultValue={form.getValues('profile.payment_method')}
                        >
                            <SelectTrigger>
                                <SelectValue placeholder="Select Method" />
                            </SelectTrigger>
                            <SelectContent>
                                <SelectItem value="bank_transfer">Bank Transfer</SelectItem>
                                <SelectItem value="mobile_money">Mobile Money</SelectItem>
                            </SelectContent>
                        </Select>
                    </div>

                    {paymentMethod === 'mobile_money' && (
                        <>
                            <div className="space-y-2">
                                <Label htmlFor="mm_provider">Provider</Label>
                                <Select
                                    onValueChange={(val) => form.setValue('profile.mobile_money_provider', val)}
                                    defaultValue={form.getValues('profile.mobile_money_provider')}
                                >
                                    <SelectTrigger>
                                        <SelectValue placeholder="Select Provider" />
                                    </SelectTrigger>
                                    <SelectContent>
                                        <SelectItem value="orange">Orange Money</SelectItem>
                                        <SelectItem value="mtn">MTN Mobile Money</SelectItem>
                                        <SelectItem value="wave">Wave</SelectItem>
                                        <SelectItem value="moov">Moov Money</SelectItem>
                                    </SelectContent>
                                </Select>
                            </div>
                            <div className="space-y-2">
                                <Label htmlFor="mm_number">Number</Label>
                                <Input {...form.register('profile.mobile_money_number')} />
                            </div>
                        </>
                    )}

                    {paymentMethod === 'bank_transfer' && (
                        <>
                            <div className="space-y-2">
                                <Label htmlFor="bank_name">Bank Name</Label>
                                <Input {...form.register('profile.bank_name')} />
                            </div>
                            <div className="space-y-2">
                                <Label htmlFor="account_number">Account Number</Label>
                                <Input {...form.register('profile.bank_account_number')} />
                            </div>
                            <div className="space-y-2">
                                <Label htmlFor="holder_name">Holder Name</Label>
                                <Input {...form.register('profile.bank_account_holder_name')} />
                            </div>
                            <div className="space-y-2">
                                <Label htmlFor="iban">IBAN</Label>
                                <Input {...form.register('profile.iban')} placeholder="International Bank Account Number" />
                            </div>
                            <div className="space-y-2">
                                <Label htmlFor="swift_bic">SWIFT/BIC</Label>
                                <Input {...form.register('profile.swift_bic')} placeholder="SWIFT/BIC Code" />
                            </div>
                        </>
                    )}
                </div>
            </div>

            <Button type="submit" disabled={loading} className="w-full">
                {loading && <Loader2 className="mr-2 h-4 w-4 animate-spin" />}
                {mode === 'create' ? 'Create Employee' : 'Update Employee'}
            </Button>
        </form>
    );
}
