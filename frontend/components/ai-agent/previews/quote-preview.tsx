import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { Check, Edit2 } from "lucide-react";
import { QuoteData } from "@/types/ai-agent";
import { formatCurrency } from "@/lib/utils";

export function QuotePreview({ data, onAction }: { data: QuoteData, onAction?: (action: string, data: any) => void }) {
    if (!data) return null;

    const formatAmount = (amount?: number) => {
        if (amount === undefined) return formatCurrency(0);
        return formatCurrency(amount);
    };

    return (
        <div className="space-y-4 w-full max-w-2xl mx-auto">
            {/* Top Card: Quote Details */}
            <Card className="shadow-sm border-gray-100">
                <CardHeader className="pb-3 border-b border-gray-50">
                    <CardTitle className="text-lg font-semibold text-gray-700">Quote Details</CardTitle>
                </CardHeader>
                <CardContent className="pt-4 space-y-3">
                    <div className="flex justify-between items-center text-sm">
                        <span className="text-gray-400">Quote Number:</span>
                        <span className="font-medium text-gray-600">{data.quote_number || 'PENDING'}</span>
                    </div>
                    <div className="flex justify-between items-center text-sm">
                        <span className="text-gray-400">Status:</span>
                        <Badge className="bg-black text-white hover:bg-black/80 font-bold px-3 py-0.5 rounded-full text-[10px]">
                            {data.status?.toUpperCase() || 'DRAFT'}
                        </Badge>
                    </div>
                    <div className="flex justify-between items-center text-sm">
                        <span className="text-gray-400">Client Name:</span>
                        <span className="font-medium text-gray-600">{data.client_name}</span>
                    </div>
                    <div className="flex justify-between items-center text-sm">
                        <span className="text-gray-400">Policy Type:</span>
                        <span className="font-medium text-gray-600 capitalize">{data.policy_type}</span>
                    </div>
                    <div className="flex justify-between items-center text-sm">
                        <span className="text-gray-400">Duration:</span>
                        <span className="font-medium text-gray-600">{data.duration_months} Months</span>
                    </div>

                    {data.vehicle_value !== undefined && (
                        <div className="flex justify-between items-center text-sm">
                            <span className="text-gray-400">Vehicle Value:</span>
                        <span className="font-medium text-gray-600">{formatAmount(data.vehicle_value)}</span>
                        </div>
                    )}
                    {data.vehicle_age !== undefined && (
                        <div className="flex justify-between items-center text-sm">
                            <span className="text-gray-400">Vehicle Year:</span>
                            <span className="font-medium text-gray-600">{data.vehicle_age}</span>
                        </div>
                    )}
                    {data.vehicle_mileage !== undefined && (
                        <div className="flex justify-between items-center text-sm">
                            <span className="text-gray-400">Mileage:</span>
                            <span className="font-medium text-gray-600">{data.vehicle_mileage.toLocaleString()} km</span>
                        </div>
                    )}
                    {data.vehicle_registration && (
                        <div className="flex justify-between items-center text-sm">
                            <span className="text-gray-400">Registration #:</span>
                            <span className="font-medium text-gray-600">{data.vehicle_registration}</span>
                        </div>
                    )}
                    {data.license_number && (
                        <div className="flex justify-between items-center text-sm">
                            <span className="text-gray-400">License #:</span>
                            <span className="font-medium text-gray-600">{data.license_number}</span>
                        </div>
                    )}
                    {data.driver_dob && (
                        <div className="flex justify-between items-center text-sm">
                            <span className="text-gray-400">Driver DOB:</span>
                            <span className="font-medium text-gray-600">{data.driver_dob}</span>
                        </div>
                    )}

                    <div className="flex justify-between items-center text-sm">
                        <span className="text-gray-400">Values Valid Until:</span>
                        <span className="font-medium text-gray-600">{data.valid_until || 'N/A'}</span>
                    </div>
                </CardContent>
            </Card>

            {/* Bottom Card: Premium Breakdown */}
            <Card className="shadow-sm border-gray-100">
                <CardHeader className="pb-3 border-b border-gray-50">
                    <CardTitle className="text-lg font-semibold text-gray-700">Premium Breakdown</CardTitle>
                </CardHeader>
                <CardContent className="pt-4 space-y-4">
                    <div className="space-y-2">
                        <div className="flex justify-between items-center text-sm">
                            <span className="text-gray-400">Coverage Amount</span>
                        <span className="font-medium text-gray-600">{formatAmount(data.coverage_amount)}</span>
                        </div>
                        <div className="flex justify-between items-center text-sm">
                            <span className="text-gray-400">Base Premium</span>
                        <span className="font-medium text-gray-600">{formatAmount(data.base_premium)}</span>
                        </div>
                        <div className="flex justify-between items-center text-sm">
                            <span className="text-gray-400">Risk Adjustment</span>
                            <span className="font-bold text-red-500">
                                {typeof data.risk_adjustment === 'number' ? formatAmount(data.risk_adjustment) : (data.risk_adjustment || 'Included')}
                            </span>
                        </div>
                        <div className="flex justify-between items-center text-sm">
                            <span className="text-gray-400">Discount ({data.discount_percent?.toFixed(2) || '0.00'}%)</span>
                            <span className="font-bold text-green-500">{formatAmount(data.discount_amount)}</span>
                        </div>
                    </div>

                    <div className="pt-4 border-t flex flex-col items-end">
                        <div className="flex items-baseline gap-4">
                            <span className="text-lg font-bold text-gray-800">Final Premium</span>
                            <span className="text-2xl font-black text-gray-900">{formatAmount(data.premium_amount)}</span>
                        </div>
                        <span className="text-[10px] text-gray-400 mt-1 lowercase italic">
                            {data.payment_frequency || 'monthly payment'}
                        </span>
                    </div>
                </CardContent>
            </Card>

            {/* Actions */}
            {onAction && (
                <div className="flex gap-4 pt-2">
                    <Button
                        className="flex-1 bg-black text-white hover:bg-black/90 h-11"
                        onClick={() => onAction('validate', data)}
                    >
                        <Check className="mr-2 h-5 w-5" />
                        Validate Quote
                    </Button>
                    <Button
                        variant="outline"
                        className="flex-1 border-gray-200 h-11 text-gray-600 hover:bg-gray-50"
                        onClick={() => onAction('modify', data)}
                    >
                        <Edit2 className="mr-2 h-4 w-4" />
                        Modify Quote
                    </Button>
                </div>
            )}
        </div>
    );
}
