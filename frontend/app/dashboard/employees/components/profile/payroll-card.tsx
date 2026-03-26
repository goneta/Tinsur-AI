'use client';

import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Landmark, CreditCard, Banknote, AlertCircle } from 'lucide-react';

interface PayrollCardProps {
    employeeId: string;
}

export function PayrollCard({ employeeId }: PayrollCardProps) {
    // Mock payroll stats as requested
    const stats = {
        payslips: 12,
        paidSalaries: 11,
        unpaidSalaries: 1,
    };

    return (
        <Card className="h-full">
            <CardHeader className="pb-2">
                <CardTitle className="text-lg font-medium flex items-center gap-2">
                    <Landmark className="h-4 w-4 text-primary" />
                    Payroll Status
                </CardTitle>
            </CardHeader>
            <CardContent>
                <div className="grid grid-cols-1 gap-4">
                    <div className="flex items-center justify-between p-3 rounded-lg bg-primary/5">
                        <div className="flex items-center gap-3">
                            <CreditCard className="h-4 w-4 text-primary" />
                            <span className="text-sm font-medium">Total Payslips</span>
                        </div>
                        <span className="text-lg font-bold">{stats.payslips}</span>
                    </div>

                    <div className="flex items-center justify-between p-3 rounded-lg bg-green-50">
                        <div className="flex items-center gap-3">
                            <Banknote className="h-4 w-4 text-green-600" />
                            <span className="text-sm font-medium text-green-700">Paid Salaries</span>
                        </div>
                        <span className="text-lg font-bold text-green-700">{stats.paidSalaries}</span>
                    </div>

                    <div className="flex items-center justify-between p-3 rounded-lg bg-amber-50">
                        <div className="flex items-center gap-3">
                            <AlertCircle className="h-4 w-4 text-amber-600" />
                            <span className="text-sm font-medium text-amber-700">Unpaid Salaries</span>
                        </div>
                        <span className="text-lg font-bold text-amber-700">{stats.unpaidSalaries}</span>
                    </div>
                </div>
            </CardContent>
        </Card>
    );
}
