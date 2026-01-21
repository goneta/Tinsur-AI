'use client';

import { useState } from 'react';
import { useForm } from 'react-hook-form';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select';
import { Loader2 } from 'lucide-react';
import { api } from '@/lib/api';
import { useToast } from '@/components/ui/use-toast';

interface PayrollFormProps {
    employee: any;
    onSuccess: () => void;
}

export function PayrollForm({ employee, onSuccess }: PayrollFormProps) {
    const [loading, setLoading] = useState(false);
    const { register, handleSubmit, formState: { errors }, watch, setValue } = useForm<any>({
        defaultValues: {
            employee_id: employee.id,
            amount: employee.employee_profile?.base_salary || '',
            currency: employee.employee_profile?.currency || 'XOF',
            payment_method: employee.employee_profile?.payment_method || 'bank_transfer',
            payment_month: new Date().toLocaleString('default', { month: 'long', year: 'numeric' }),
            description: `Salary Payment`
        }
    });

    const { toast } = useToast();
    const paymentMonth = watch('payment_month');

    // Generate last 6 months and next 2 months for selection
    const monthOptions = [];
    const now = new Date();
    for (let i = -6; i <= 2; i++) {
        const d = new Date(now.getFullYear(), now.getMonth() + i, 1);
        monthOptions.push(d.toLocaleString('default', { month: 'long', year: 'numeric' }));
    }

    const onSubmit = async (data: any) => {
        setLoading(true);
        // Combine description and month if needed, but we have payment_month now
        const payload = {
            ...data,
            description: `${data.description} - ${data.payment_month}`
        };
        try {
            await api.post('/payroll/', payload);
            toast({
                title: 'Success',
                description: 'Payment processed successfully.',
            });
            onSuccess();
        } catch (error: any) {
            console.error(error);
            toast({
                title: 'Error',
                description: error.response?.data?.detail || 'Failed to process payment',
                variant: 'destructive',
            });
        } finally {
            setLoading(false);
        }
    };

    return (
        <form onSubmit={handleSubmit(onSubmit)} className="space-y-4">
            <div className="rounded-md bg-muted p-4 text-sm">
                <p><strong>Paying to:</strong> {employee.first_name} {employee.last_name}</p>
                <p><strong>Method:</strong> {employee.employee_profile?.payment_method === 'mobile_money' ?
                    `Mobile Money (${employee.employee_profile?.mobile_money_provider} - ${employee.employee_profile?.mobile_money_number})` :
                    `Bank Transfer (${employee.employee_profile?.bank_name} - ${employee.employee_profile?.bank_account_number})`
                }</p>
            </div>

            <div className="grid grid-cols-2 gap-4">
                <div className="space-y-2">
                    <Label htmlFor="payment_month">Payment Month</Label>
                    <Select
                        onValueChange={(val) => setValue('payment_month', val)}
                        defaultValue={new Date().toLocaleString('default', { month: 'long', year: 'numeric' })}
                    >
                        <SelectTrigger>
                            <SelectValue placeholder="Select Month" />
                        </SelectTrigger>
                        <SelectContent>
                            {monthOptions.map((m) => (
                                <SelectItem key={m} value={m}>{m}</SelectItem>
                            ))}
                        </SelectContent>
                    </Select>
                </div>

                <div className="space-y-2">
                    <Label htmlFor="currency">Currency</Label>
                    <Select onValueChange={(val) => setValue('currency', val)} defaultValue="XOF">
                        <SelectTrigger>
                            <SelectValue placeholder="Select Currency" />
                        </SelectTrigger>
                        <SelectContent>
                            <SelectItem value="XOF">XOF</SelectItem>
                            <SelectItem value="USD">USD</SelectItem>
                            <SelectItem value="EUR">EUR</SelectItem>
                        </SelectContent>
                    </Select>
                </div>
            </div>

            <div className="space-y-2">
                <Label htmlFor="amount">Amount</Label>
                <Input id="amount" type="number" step="0.01" {...register('amount', { required: true })} />
                {errors.amount && <span className="text-sm text-red-500">Required</span>}
            </div>

            <div className="space-y-2">
                <Label htmlFor="description">Description</Label>
                <Input id="description" {...register('description')} />
            </div>

            <Button type="submit" disabled={loading} className="w-full">
                {loading && <Loader2 className="mr-2 h-4 w-4 animate-spin" />}
                Confirm Payment
            </Button>
        </form>
    );
}
