'use client';

import {
    Dialog,
    DialogContent,
    DialogHeader,
    DialogTitle,
} from "@/components/ui/dialog";
import { Badge } from "@/components/ui/badge";
import { Separator } from "@/components/ui/separator";
import { Printer } from "lucide-react";
import { Button } from "@/components/ui/button";

interface PayslipDialogProps {
    isOpen: boolean;
    onOpenChange: (open: boolean) => void;
    data: any;
}

export function PayslipDialog({ isOpen, onOpenChange, data }: PayslipDialogProps) {
    if (!data) return null;

    const formatCurrency = (amount: number) => {
        return new Intl.NumberFormat('fr-FR', {
            style: 'currency',
            currency: data.currency || 'XOF'
        }).format(amount);
    };

    const deductions = (Number(data.tax_is) || 0) +
        (Number(data.tax_cn) || 0) +
        (Number(data.tax_igr) || 0) +
        (Number(data.social_security_cnps) || 0);

    return (
        <Dialog open={isOpen} onOpenChange={onOpenChange}>
            <DialogContent className="max-w-2xl print:max-w-none">
                <DialogHeader className="print:hidden">
                    <DialogTitle className="flex items-center justify-between">
                        Payslip Breakdown
                        <Button variant="outline" size="sm" onClick={() => window.print()}>
                            <Printer className="h-4 w-4 mr-2" /> Print
                        </Button>
                    </DialogTitle>
                </DialogHeader>

                <div className="space-y-6 py-4 print:p-8">
                    {/* Header */}
                    <div className="flex justify-between items-start border-b pb-6">
                        <div>
                            <h2 className="text-2xl font-bold">PAYSLIP</h2>
                            <p className="text-muted-foreground uppercase tracking-widest text-sm font-semibold mt-1">
                                {data.payment_month}
                            </p>
                        </div>
                        <div className="text-right">
                            <h3 className="font-bold">{data.employee_name || 'Employee Name'}</h3>
                            <p className="text-sm text-muted-foreground">Reference: {data.id.slice(0, 8)}</p>
                            <p className="text-sm text-muted-foreground">Date: {new Date(data.payment_date).toLocaleDateString()}</p>
                        </div>
                    </div>

                    {/* Earnings */}
                    <div className="space-y-4">
                        <h3 className="font-bold text-sm uppercase text-muted-foreground">Earnings</h3>
                        <div className="space-y-2">
                            <div className="flex justify-between text-sm">
                                <span>Base Salary</span>
                                <span>{formatCurrency(data.base_salary)}</span>
                            </div>
                            {Number(data.commissions_total) > 0 && (
                                <div className="flex justify-between text-sm">
                                    <span>Commissions</span>
                                    <span>{formatCurrency(data.commissions_total)}</span>
                                </div>
                            )}
                            {Number(data.transport_allowance) > 0 && (
                                <div className="flex justify-between text-sm">
                                    <span>Transport Allowance</span>
                                    <span>{formatCurrency(data.transport_allowance)}</span>
                                </div>
                            )}
                            <Separator />
                            <div className="flex justify-between font-bold">
                                <span>Gross Salary</span>
                                <span>{formatCurrency(data.amount)}</span>
                            </div>
                        </div>
                    </div>

                    {/* Deductions */}
                    <div className="space-y-4">
                        <h3 className="font-bold text-sm uppercase text-muted-foreground">Deductions</h3>
                        <div className="space-y-2">
                            <div className="flex justify-between text-sm">
                                <span>IS (Impôt sur le Salaire)</span>
                                <span className="text-destructive">-{formatCurrency(data.tax_is)}</span>
                            </div>
                            <div className="flex justify-between text-sm">
                                <span>CN (Contribution Nationale)</span>
                                <span className="text-destructive">-{formatCurrency(data.tax_cn)}</span>
                            </div>
                            <div className="flex justify-between text-sm">
                                <span>IGR (Impôt Général sur le Revenu)</span>
                                <span className="text-destructive">-{formatCurrency(data.tax_igr)}</span>
                            </div>
                            <div className="flex justify-between text-sm">
                                <span>Social Security (CNPS)</span>
                                <span className="text-destructive">-{formatCurrency(data.social_security_cnps)}</span>
                            </div>
                            <Separator />
                            <div className="flex justify-between font-bold">
                                <span>Total Deductions</span>
                                <span className="text-destructive">-{formatCurrency(deductions)}</span>
                            </div>
                        </div>
                    </div>

                    {/* Net Pay */}
                    <div className="bg-primary/5 p-4 rounded-lg flex justify-between items-center border border-primary/10">
                        <div>
                            <p className="text-sm font-medium text-primary">Net Payable</p>
                            <p className="text-xs text-muted-foreground italic">Paid via {data.payment_method?.replace('_', ' ')}</p>
                        </div>
                        <div className="text-2xl font-black text-primary">
                            {formatCurrency(data.net_pay)}
                        </div>
                    </div>

                    <div className="text-[10px] text-muted-foreground text-center mt-8 border-t pt-4">
                        This is a computer generated document. No signature is required.
                    </div>
                </div>
            </DialogContent>
        </Dialog>
    );
}
