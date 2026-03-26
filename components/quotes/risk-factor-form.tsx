"use client";

import { useFormContext } from "react-hook-form";
import {
    FormControl,
    FormField,
    FormItem,
    FormLabel,
    FormMessage,
} from "@/components/ui/form";
import { Input } from "@/components/ui/input";
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select";

interface RiskFactorFormProps {
    policyTypeCode: string;
}

export function RiskFactorForm({ policyTypeCode }: RiskFactorFormProps) {
    const { control } = useFormContext();

    const code = policyTypeCode.toUpperCase();

    if (code === "AUTO") {
        return (
            <div className="grid gap-4 md:grid-cols-2">
                <FormField
                    control={control}
                    name="risk_factors.vehicle_value"
                    render={({ field }) => (
                        <FormItem>
                            <FormLabel>Vehicle Value (XOF)</FormLabel>
                            <FormControl>
                                <Input type="number" {...field} onChange={e => field.onChange(parseFloat(e.target.value))} />
                            </FormControl>
                            <FormMessage />
                        </FormItem>
                    )}
                />
                <FormField
                    control={control}
                    name="risk_factors.vehicle_age"
                    render={({ field }) => (
                        <FormItem>
                            <FormLabel>Vehicle Age (Years)</FormLabel>
                            <FormControl>
                                <Input type="number" {...field} onChange={e => field.onChange(parseInt(e.target.value))} />
                            </FormControl>
                            <FormMessage />
                        </FormItem>
                    )}
                />
                <FormField
                    control={control}
                    name="risk_factors.driver_age"
                    render={({ field }) => (
                        <FormItem>
                            <FormLabel>Driver Age</FormLabel>
                            <FormControl>
                                <Input type="number" {...field} onChange={e => field.onChange(parseInt(e.target.value))} />
                            </FormControl>
                            <FormMessage />
                        </FormItem>
                    )}
                />
            </div>
        );
    }

    if (code === "HOME") {
        return (
            <div className="grid gap-4 md:grid-cols-2">
                <FormField
                    control={control}
                    name="risk_factors.property_value"
                    render={({ field }) => (
                        <FormItem>
                            <FormLabel>Property Value (XOF)</FormLabel>
                            <FormControl>
                                <Input type="number" {...field} onChange={e => field.onChange(parseFloat(e.target.value))} />
                            </FormControl>
                            <FormMessage />
                        </FormItem>
                    )}
                />
                <FormField
                    control={control}
                    name="risk_factors.construction_year"
                    render={({ field }) => (
                        <FormItem>
                            <FormLabel>Construction Year</FormLabel>
                            <FormControl>
                                <Input type="number" {...field} onChange={e => field.onChange(parseInt(e.target.value))} />
                            </FormControl>
                            <FormMessage />
                        </FormItem>
                    )}
                />
                <FormField
                    control={control}
                    name="risk_factors.location_risk"
                    render={({ field }) => (
                        <FormItem>
                            <FormLabel>Location Risk Zone</FormLabel>
                            <Select onValueChange={field.onChange} defaultValue={field.value}>
                                <FormControl>
                                    <SelectTrigger>
                                        <SelectValue placeholder="Select zone" />
                                    </SelectTrigger>
                                </FormControl>
                                <SelectContent>
                                    <SelectItem value="low">Low Risk</SelectItem>
                                    <SelectItem value="medium">Medium Risk</SelectItem>
                                    <SelectItem value="high">High Risk</SelectItem>
                                </SelectContent>
                            </Select>
                            <FormMessage />
                        </FormItem>
                    )}
                />
            </div>
        );
    }

    // Generic/Fallback Form
    return (
        <div className="space-y-4">
            <div className="p-4 bg-muted rounded-md text-sm text-muted-foreground">
                Standard risk assessment fields for {policyTypeCode}.
            </div>
            <FormField
                control={control}
                name="risk_factors.generic_value"
                render={({ field }) => (
                    <FormItem>
                        <FormLabel>Insured Value</FormLabel>
                        <FormControl>
                            <Input type="number" {...field} onChange={e => field.onChange(parseFloat(e.target.value))} />
                        </FormControl>
                        <FormMessage />
                    </FormItem>
                )}
            />
        </div>
    );
}
