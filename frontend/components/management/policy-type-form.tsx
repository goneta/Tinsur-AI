"use client";

import { useState } from "react";
import { useForm } from "react-hook-form";
import { useToast } from "@/components/ui/use-toast";
import { QuoteAPI } from "@/lib/api/quotes";
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
import { Textarea } from "@/components/ui/textarea";
import { Loader2 } from "lucide-react";

interface PolicyTypeFormValues {
    name: string;
    code: string;
    description?: string;
}

interface PolicyTypeFormProps {
    onSuccess?: (newType: any) => void;
    onCancel?: () => void;
}

export function PolicyTypeForm({ onSuccess, onCancel }: PolicyTypeFormProps) {
    const { toast } = useToast();
    const [loading, setLoading] = useState(false);

    const form = useForm<PolicyTypeFormValues>({
        defaultValues: {
            name: "",
            code: "",
            description: "",
        },
    });

    const onSubmit = async (data: PolicyTypeFormValues) => {
        setLoading(true);
        try {
            const newType = await QuoteAPI.createPolicyType(data);
            toast({
                title: "Success",
                description: "Policy Type created successfully",
            });
            form.reset();
            if (onSuccess) {
                onSuccess(newType);
            }
        } catch (error) {
            toast({
                title: "Error",
                description: "Failed to create policy type",
                variant: "destructive",
            });
        } finally {
            setLoading(false);
        }
    };

    return (
        <Form {...form}>
            <form onSubmit={form.handleSubmit(onSubmit)} className="space-y-4">
                <FormField
                    control={form.control}
                    name="name"
                    rules={{ required: "Name is required" }}
                    render={({ field }) => (
                        <FormItem>
                            <FormLabel>Name</FormLabel>
                            <FormControl>
                                <Input placeholder="e.g. Comprehensive Auto" {...field} />
                            </FormControl>
                            <FormMessage />
                        </FormItem>
                    )}
                />

                <FormField
                    control={form.control}
                    name="code"
                    rules={{ required: "Code is required" }}
                    render={({ field }) => (
                        <FormItem>
                            <FormLabel>Code</FormLabel>
                            <FormControl>
                                <Input placeholder="e.g. AUTO_COMP" {...field} />
                            </FormControl>
                            <FormMessage />
                        </FormItem>
                    )}
                />

                <FormField
                    control={form.control}
                    name="description"
                    render={({ field }) => (
                        <FormItem>
                            <FormLabel>Description</FormLabel>
                            <FormControl>
                                <Textarea placeholder="Optional description..." {...field} />
                            </FormControl>
                            <FormMessage />
                        </FormItem>
                    )}
                />

                <div className="flex justify-end gap-2 pt-2">
                    {onCancel && (
                        <Button type="button" variant="outline" onClick={onCancel}>
                            Cancel
                        </Button>
                    )}
                    <Button type="submit" disabled={loading}>
                        {loading && <Loader2 className="mr-2 h-4 w-4 animate-spin" />}
                        Create Policy Type
                    </Button>
                </div>
            </form>
        </Form>
    );
}
