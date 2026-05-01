"use client";

import { useState } from "react";
import { useForm } from "react-hook-form";
import { zodResolver } from "@hookform/resolvers/zod";
import * as z from "zod";
import { CreditCard, Banknote, Building2, Smartphone, Loader2 } from "lucide-react";
import { useLanguage } from "@/contexts/language-context";

import { Button } from "@/components/ui/button";
import {
    Form,
    FormControl,
    FormDescription,
    FormField,
    FormItem,
    FormLabel,
    FormMessage,
} from "@/components/ui/form";
import { Input } from "@/components/ui/input";
import {
    Select,
    SelectContent,
    SelectItem,
    SelectTrigger,
    SelectValue,
} from "@/components/ui/select";
import { RadioGroup, RadioGroupItem } from "@/components/ui/radio-group";
import { Card, CardContent } from "@/components/ui/card";
import { useToast } from "@/components/ui/use-toast";
import { paymentApi } from "@/lib/payment-api";

const paymentMethodSchema = z.enum(["cash", "mobile_money", "bank_transfer", "stripe"]);

const formSchema = z.object({
    amount: z.string().refine((val) => !isNaN(Number(val)) && Number(val) > 0, {
        message: "Amount must be greater than 0",
    }),
    currency: z.string(),
    payment_method: paymentMethodSchema,
    gateway: z.string().optional(),
    phone_number: z.string().optional(),
    transaction_id: z.string().optional(),
    bank_name: z.string().optional(),
    account_number: z.string().optional(),
}).superRefine((data, ctx) => {
    if (data.payment_method === "mobile_money") {
        if (!data.gateway) {
            ctx.addIssue({
                code: z.ZodIssueCode.custom,
                message: "Gateway is required",
                path: ["gateway"],
            });
        }
        if (!data.phone_number) {
            ctx.addIssue({
                code: z.ZodIssueCode.custom,
                message: "Phone number is required",
                path: ["phone_number"],
            });
        }
    }
    if (data.payment_method === "bank_transfer") {
        if (!data.bank_name) {
            ctx.addIssue({
                code: z.ZodIssueCode.custom,
                message: "Bank name is required",
                path: ["bank_name"],
            });
        }
        if (!data.account_number) {
            ctx.addIssue({
                code: z.ZodIssueCode.custom,
                message: "Account number is required",
                path: ["account_number"],
            });
        }
    }
});

interface PaymentFormProps {
    policyId: string;
    policyNumber?: string;
    defaultAmount?: number;
    onSuccess?: () => void;
}

export function PaymentForm({ policyId, policyNumber, defaultAmount, onSuccess }: PaymentFormProps) {
    const { t } = useLanguage();
    const [isLoading, setIsLoading] = useState(false);
    const { toast } = useToast();

    const form = useForm<z.infer<typeof formSchema>>({
        resolver: zodResolver(formSchema),
        defaultValues: {
            amount: defaultAmount ? defaultAmount.toString() : "",
            currency: "XOF",
            payment_method: "cash",
        },
    });

    const paymentMethod = form.watch("payment_method");

    async function onSubmit(values: z.infer<typeof formSchema>) {
        setIsLoading(true);
        try {
            const paymentDetails: Record<string, any> = {
                method: values.payment_method,
            };

            if (values.payment_method === "mobile_money") {
                paymentDetails.gateway = values.gateway;
                paymentDetails.phone_number = values.phone_number;
            } else if (values.payment_method === "bank_transfer") {
                paymentDetails.bank_name = values.bank_name;
                paymentDetails.account_number = values.account_number;
                paymentDetails.reference_number = values.transaction_id;
            } else if (values.payment_method === "cash") {
                paymentDetails.reference_number = values.transaction_id;
            }

            await paymentApi.processPayment({
                policy_id: policyId,
                amount: Number(values.amount),
                payment_details: paymentDetails,
            });

            toast({
                title: t('payment.processed', 'Payment processed'),
                description: t('payment.recorded_success', 'The payment has been successfully recorded.'),
            });

            form.reset();
            if (onSuccess) {
                onSuccess();
            }
        } catch (error) {
            console.error(error);
            toast({
                variant: "destructive",
                title: t('common.error', 'Error'),
                description: t('payment.process_failed', 'Failed to process payment. Please try again.'),
            });
        } finally {
            setIsLoading(false);
        }
    }

    return (
        <Form {...form}>
            <form onSubmit={form.handleSubmit(onSubmit)} className="space-y-6">
                <div className="grid gap-4 md:grid-cols-2">
                    <FormField
                        control={form.control}
                        name="amount"
                        render={({ field }) => (
                            <FormItem>
                                <FormLabel>{t('label.amount', 'Amount')}</FormLabel>
                                <FormControl>
                                    <Input placeholder="0.00" {...field} />
                                </FormControl>
                                <FormMessage />
                            </FormItem>
                        )}
                    />

                    <FormField
                        control={form.control}
                        name="currency"
                        render={({ field }) => (
                            <FormItem>
                                <FormLabel>{t('label.currency', 'Currency')}</FormLabel>
                                <Select onValueChange={field.onChange} defaultValue={field.value}>
                                    <FormControl>
                                        <SelectTrigger>
                                            <SelectValue placeholder={t('payment.currency_placeholder', 'Select currency')} />
                                        </SelectTrigger>
                                    </FormControl>
                                    <SelectContent>
                                        <SelectItem value="XOF">XOF (CFA Franc)</SelectItem>
                                        <SelectItem value="USD">USD</SelectItem>
                                        <SelectItem value="EUR">EUR</SelectItem>
                                    </SelectContent>
                                </Select>
                                <FormMessage />
                            </FormItem>
                        )}
                    />
                </div>

                <FormField
                    control={form.control}
                    name="payment_method"
                    render={({ field }) => (
                        <FormItem className="space-y-3">
                            <FormLabel>{t('label.payment_method', 'Payment Method')}</FormLabel>
                            <FormControl>
                                <RadioGroup
                                    onValueChange={field.onChange}
                                    defaultValue={field.value}
                                    className="grid grid-cols-2 md:grid-cols-4 gap-4"
                                >
                                    <FormItem>
                                        <FormControl>
                                            <RadioGroupItem value="cash" className="peer sr-only" />
                                        </FormControl>
                                        <FormLabel className="flex flex-col items-center justify-between rounded-md border-2 border-muted bg-popover p-4 hover:bg-accent hover:text-accent-foreground peer-data-[state=checked]:border-primary [&:has([data-state=checked])]:border-primary">
                                            <Banknote className="mb-3 h-6 w-6" />
                                            {t('payment.method.cash', 'Cash')}
                                        </FormLabel>
                                    </FormItem>
                                    <FormItem>
                                        <FormControl>
                                            <RadioGroupItem value="mobile_money" className="peer sr-only" />
                                        </FormControl>
                                        <FormLabel className="flex flex-col items-center justify-between rounded-md border-2 border-muted bg-popover p-4 hover:bg-accent hover:text-accent-foreground peer-data-[state=checked]:border-primary [&:has([data-state=checked])]:border-primary">
                                            <Smartphone className="mb-3 h-6 w-6" />
                                            {t('payment.method.mobile_money', 'Mobile Money')}
                                        </FormLabel>
                                    </FormItem>
                                    <FormItem>
                                        <FormControl>
                                            <RadioGroupItem value="bank_transfer" className="peer sr-only" />
                                        </FormControl>
                                        <FormLabel className="flex flex-col items-center justify-between rounded-md border-2 border-muted bg-popover p-4 hover:bg-accent hover:text-accent-foreground peer-data-[state=checked]:border-primary [&:has([data-state=checked])]:border-primary">
                                            <Building2 className="mb-3 h-6 w-6" />
                                            {t('payment.method.bank_transfer', 'Bank Transfer')}
                                        </FormLabel>
                                    </FormItem>
                                    <FormItem>
                                        <FormControl>
                                            <RadioGroupItem value="stripe" className="peer sr-only" disabled />
                                        </FormControl>
                                        <FormLabel className="flex flex-col items-center justify-between rounded-md border-2 border-muted bg-popover p-4 hover:bg-accent hover:text-accent-foreground peer-data-[state=checked]:border-primary [&:has([data-state=checked])]:border-primary opacity-50 cursor-not-allowed">
                                            <CreditCard className="mb-3 h-6 w-6" />
                                            {t('payment.method.card_online', 'Card (Online)')}
                                        </FormLabel>
                                    </FormItem>
                                </RadioGroup>
                            </FormControl>
                            <FormMessage />
                        </FormItem>
                    )}
                />

                <Card className={paymentMethod === "cash" ? "border-primary/20 bg-primary/5" : "bg-muted/50"}>
                    <CardContent className="pt-6">
                        {paymentMethod === "cash" && (
                            <div className="grid gap-4">
                                <FormField
                                    control={form.control}
                                    name="transaction_id"
                                    render={({ field }) => (
                                        <FormItem>
                                            <FormLabel>{t('payment.reference_no', 'Reference / Receipt No. (Optional)')}</FormLabel>
                                            <FormControl>
                                                <Input placeholder={t('payment.receipt_placeholder', 'Enter receipt number')} {...field} />
                                            </FormControl>
                                            <FormMessage />
                                        </FormItem>
                                    )}
                                />
                            </div>
                        )}

                        {paymentMethod === "mobile_money" && (
                            <div className="grid gap-4 md:grid-cols-2">
                                <FormField
                                    control={form.control}
                                    name="gateway"
                                    render={({ field }) => (
                                        <FormItem>
                                            <FormLabel>{t('label.provider', 'Provider')}</FormLabel>
                                            <Select onValueChange={field.onChange} defaultValue={field.value}>
                                                <FormControl>
                                                    <SelectTrigger>
                                                        <SelectValue placeholder={t('payment.provider_placeholder', 'Select provider')} />
                                                    </SelectTrigger>
                                                </FormControl>
                                                <SelectContent>
                                                    <SelectItem value="orange_money">Orange Money</SelectItem>
                                                    <SelectItem value="mtn_money">MTN Money</SelectItem>
                                                    <SelectItem value="moov_money">Moov Money</SelectItem>
                                                    <SelectItem value="wave">Wave</SelectItem>
                                                </SelectContent>
                                            </Select>
                                            <FormMessage />
                                        </FormItem>
                                    )}
                                />
                                <FormField
                                    control={form.control}
                                    name="phone_number"
                                    render={({ field }) => (
                                        <FormItem>
                                            <FormLabel>{t('label.phone_number', 'Phone Number')}</FormLabel>
                                            <FormControl>
                                                <Input placeholder="0102030405" {...field} />
                                            </FormControl>
                                            <FormMessage />
                                        </FormItem>
                                    )}
                                />
                            </div>
                        )}

                        {paymentMethod === "bank_transfer" && (
                            <div className="grid gap-4">
                                <FormField
                                    control={form.control}
                                    name="bank_name"
                                    render={({ field }) => (
                                        <FormItem>
                                            <FormLabel>{t('label.bank_name', 'Bank Name')}</FormLabel>
                                            <FormControl>
                                                <Input placeholder={t('payment.bank_placeholder', 'Enter bank name')} {...field} />
                                            </FormControl>
                                            <FormMessage />
                                        </FormItem>
                                    )}
                                />
                                <FormField
                                    control={form.control}
                                    name="account_number"
                                    render={({ field }) => (
                                        <FormItem>
                                            <FormLabel>{t('label.account_number', 'Account Number')}</FormLabel>
                                            <FormControl>
                                                <Input placeholder={t('payment.account_placeholder', 'Enter account number')} {...field} />
                                            </FormControl>
                                            <FormMessage />
                                        </FormItem>
                                    )}
                                />
                                <FormField
                                    control={form.control}
                                    name="transaction_id"
                                    render={({ field }) => (
                                        <FormItem>
                                            <FormLabel>{t('payment.transaction_reference', 'Transaction Reference')}</FormLabel>
                                            <FormControl>
                                                <Input placeholder={t('payment.reference_placeholder', 'Enter reference number')} {...field} />
                                            </FormControl>
                                            <FormMessage />
                                        </FormItem>
                                    )}
                                />
                            </div>
                        )}
                    </CardContent>
                </Card>

                <Button type="submit" className="w-full" disabled={isLoading}>
                    {isLoading ? (
                        <>
                            <Loader2 className="mr-2 h-4 w-4 animate-spin" />
                            {t('common.processing', 'Processing...')}
                        </>
                    ) : (
                        t('payment.process_btn', 'Process Payment')
                    )}
                </Button>
            </form>
        </Form>
    );
}
