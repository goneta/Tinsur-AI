"use client";

import { useState, useEffect } from "react";
import { useForm } from "react-hook-form";
import { zodResolver } from "@hookform/resolvers/zod";
import * as z from "zod";
import { Smartphone, Building2, Banknote, Loader2, CreditCard } from "lucide-react";
import { portalApi } from "@/lib/portal-api";

import { Button } from "@/components/ui/button";
import {
    Form,
    FormControl,
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
import {
    Dialog,
    DialogContent,
    DialogDescription,
    DialogHeader,
    DialogTitle,
} from "@/components/ui/dialog";

const paymentMethodSchema = z.enum(["mobile_money", "bank_transfer", "cash", "stripe"]);

const formSchema = z.object({
    policy_id: z.string().min(1, "Policy is required"),
    amount: z.string().refine((val) => !isNaN(Number(val)) && Number(val) > 0, {
        message: "Amount must be greater than 0",
    }),
    currency: z.string(),
    payment_method: paymentMethodSchema,
    gateway: z.string().optional(),
    phone_number: z.string().optional(),
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
});

interface PortalPaymentDialogProps {
    open: boolean;
    onOpenChange: (open: boolean) => void;
    onSuccess?: () => void;
}

export function PortalPaymentDialog({ open, onOpenChange, onSuccess }: PortalPaymentDialogProps) {
    const [isLoading, setIsLoading] = useState(false);
    const [fetchingPolicies, setFetchingPolicies] = useState(false);
    const [policies, setPolicies] = useState<any[]>([]);
    const { toast } = useToast();

    const form = useForm<z.infer<typeof formSchema>>({
        resolver: zodResolver(formSchema) as any,
        defaultValues: {
            amount: "",
            currency: "XOF",
            payment_method: "mobile_money",
        },
    });

    const paymentMethod = form.watch("payment_method");

    useEffect(() => {
        if (open) {
            const fetchPolicies = async () => {
                setFetchingPolicies(true);
                try {
                    const data = await portalApi.getMyPolicies();
                    setPolicies(data || []);
                } catch (err) {
                    toast({
                        variant: "destructive",
                        title: "Error",
                        description: "Failed to load policies.",
                    });
                } finally {
                    setFetchingPolicies(false);
                }
            };
            fetchPolicies();
        }
    }, [open, toast]);

    async function onSubmit(values: z.infer<typeof formSchema>) {
        setIsLoading(true);
        try {
            const paymentDetails: Record<string, any> = {
                method: values.payment_method,
            };

            if (values.payment_method === "mobile_money") {
                paymentDetails.gateway = values.gateway;
                paymentDetails.phone_number = values.phone_number;
            }

            await portalApi.processPayment({
                policy_id: values.policy_id,
                amount: Number(values.amount),
                payment_details: paymentDetails,
            });

            toast({
                title: "Payment Processed",
                description: "Your payment has been successfully recorded.",
            });

            form.reset();
            if (onSuccess) onSuccess();
            onOpenChange(false);
        } catch (error: any) {
            console.error(error);
            toast({
                variant: "destructive",
                title: "Payment Error",
                description: error.response?.data?.detail || "Failed to process payment. Please try again.",
            });
        } finally {
            setIsLoading(false);
        }
    }

    return (
        <Dialog open={open} onOpenChange={onOpenChange}>
            <DialogContent className="sm:max-w-[600px]">
                <DialogHeader>
                    <DialogTitle>Make a Payment</DialogTitle>
                    <DialogDescription>
                        Pay your insurance premiums securely using our various payment options.
                    </DialogDescription>
                </DialogHeader>

                <Form {...form}>
                    <form onSubmit={form.handleSubmit(onSubmit)} className="space-y-6 pt-4">
                        <FormField
                            control={form.control}
                            name="policy_id"
                            render={({ field }) => (
                                <FormItem>
                                    <FormLabel>Policy to Pay</FormLabel>
                                    <Select
                                        disabled={fetchingPolicies}
                                        onValueChange={field.onChange}
                                        defaultValue={field.value}
                                    >
                                        <FormControl>
                                            <SelectTrigger>
                                                <SelectValue placeholder={fetchingPolicies ? "Loading..." : "Select policy"} />
                                            </SelectTrigger>
                                        </FormControl>
                                        <SelectContent>
                                            {policies.map(p => (
                                                <SelectItem key={p.id} value={p.id}>
                                                    {p.policy_number} - {p.policy_type?.name} ({p.premium_amount} XOF)
                                                </SelectItem>
                                            ))}
                                        </SelectContent>
                                    </Select>
                                    <FormMessage />
                                </FormItem>
                            )}
                        />

                        <div className="grid gap-4 md:grid-cols-2">
                            <FormField
                                control={form.control}
                                name="amount"
                                render={({ field }) => (
                                    <FormItem>
                                        <FormLabel>Amount</FormLabel>
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
                                        <FormLabel>Currency</FormLabel>
                                        <Select onValueChange={field.onChange} defaultValue={field.value}>
                                            <FormControl>
                                                <SelectTrigger>
                                                    <SelectValue placeholder="Currency" />
                                                </SelectTrigger>
                                            </FormControl>
                                            <SelectContent>
                                                <SelectItem value="XOF">XOF (CFA Franc)</SelectItem>
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
                                    <FormLabel>Payment Method</FormLabel>
                                    <FormControl>
                                        <RadioGroup
                                            onValueChange={field.onChange}
                                            defaultValue={field.value}
                                            className="grid grid-cols-2 gap-4"
                                        >
                                            <FormItem>
                                                <FormControl>
                                                    <RadioGroupItem value="mobile_money" className="peer sr-only" />
                                                </FormControl>
                                                <FormLabel className="flex flex-col items-center justify-between rounded-md border-2 border-muted bg-popover p-4 hover:bg-accent hover:text-accent-foreground peer-data-[state=checked]:border-primary [&:has([data-state=checked])]:border-primary cursor-pointer">
                                                    <Smartphone className="mb-2 h-6 w-6" />
                                                    Mobile Money
                                                </FormLabel>
                                            </FormItem>
                                            <FormItem>
                                                <FormControl>
                                                    <RadioGroupItem value="bank_transfer" className="peer sr-only" />
                                                </FormControl>
                                                <FormLabel className="flex flex-col items-center justify-between rounded-md border-2 border-muted bg-popover p-4 hover:bg-accent hover:text-accent-foreground peer-data-[state=checked]:border-primary [&:has([data-state=checked])]:border-primary cursor-pointer">
                                                    <Building2 className="mb-2 h-6 w-6" />
                                                    Bank Transfer
                                                </FormLabel>
                                            </FormItem>
                                            <FormItem>
                                                <FormControl>
                                                    <RadioGroupItem value="stripe" className="peer sr-only" />
                                                </FormControl>
                                                <FormLabel className="flex flex-col items-center justify-between rounded-md border-2 border-muted bg-popover p-4 hover:bg-accent hover:text-accent-foreground peer-data-[state=checked]:border-primary [&:has([data-state=checked])]:border-primary cursor-pointer">
                                                    <CreditCard className="mb-2 h-6 w-6" />
                                                    Visa debit card
                                                </FormLabel>
                                            </FormItem>
                                        </RadioGroup>
                                    </FormControl>
                                    <FormMessage />
                                </FormItem>
                            )}
                        />

                        {paymentMethod === "mobile_money" && (
                            <Card className="bg-primary/5 border-primary/20">
                                <CardContent className="pt-6 grid gap-4 md:grid-cols-2">
                                    <FormField
                                        control={form.control}
                                        name="gateway"
                                        render={({ field }) => (
                                            <FormItem>
                                                <FormLabel>Provider</FormLabel>
                                                <Select onValueChange={field.onChange} defaultValue={field.value}>
                                                    <FormControl>
                                                        <SelectTrigger>
                                                            <SelectValue placeholder="Select provider" />
                                                        </SelectTrigger>
                                                    </FormControl>
                                                    <SelectContent>
                                                        <SelectItem value="orange_money">Orange Money</SelectItem>
                                                        <SelectItem value="mtn_money">MTN Money</SelectItem>
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
                                                <FormLabel>Phone Number</FormLabel>
                                                <FormControl>
                                                    <Input placeholder="0700000000" {...field} />
                                                </FormControl>
                                                <FormMessage />
                                            </FormItem>
                                        )}
                                    />
                                </CardContent>
                            </Card>
                        )}

                        <div className="flex justify-end gap-2 pt-4">
                            <Button type="button" variant="outline" onClick={() => onOpenChange(false)}>Cancel</Button>
                            <Button type="submit" className="w-full sm:w-auto" disabled={isLoading}>
                                {isLoading ? <Loader2 className="mr-2 h-4 w-4 animate-spin" /> : null}
                                {isLoading ? "Processing..." : "Pay Now"}
                            </Button>
                        </div>
                    </form>
                </Form>
            </DialogContent>
        </Dialog>
    );
}
