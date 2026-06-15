'use client';

import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Briefcase, DollarSign, MapPin, ShieldCheck } from 'lucide-react';
import { Badge } from '@/components/ui/badge';
import { Employee } from '../../columns';

interface PositionCardProps {
    employee: Employee;
}

export function PositionCard({ employee }: PositionCardProps) {
    const formatSalary = (amount?: number, currency?: string) => {
        if (!amount) return 'Not set';
        return new Intl.NumberFormat('fr-FR', {
            style: 'currency',
            currency: currency || 'XOF'
        }).format(amount);
    };

    return (
        <Card className="h-full">
            <CardHeader className="pb-2">
                <CardTitle className="text-lg font-medium flex items-center gap-2">
                    <Briefcase className="h-4 w-4 text-primary" />
                    Employee Position
                </CardTitle>
            </CardHeader>
            <CardContent className="space-y-4">
                <div className="grid grid-cols-2 gap-4">
                    <div className="space-y-1">
                        <div className="text-sm text-muted-foreground flex items-center gap-1">
                            <ShieldCheck className="h-3 w-3" /> Role
                        </div>
                        <Badge variant="secondary" className="capitalize">{employee.role}</Badge>
                    </div>
                    <div className="space-y-1">
                        <div className="text-sm text-muted-foreground">Job Type</div>
                        <div className="font-medium">{employee.employee_profile?.job_title || 'N/A'}</div>
                    </div>
                </div>

                <div className="space-y-1">
                    <div className="text-sm text-muted-foreground flex items-center gap-1">
                        <DollarSign className="h-3 w-3" /> Salary
                    </div>
                    <div className="text-xl font-bold text-primary">
                        {formatSalary(employee.employee_profile?.base_salary, employee.employee_profile?.currency)}
                    </div>
                </div>

                <div className="space-y-1">
                    <div className="text-sm text-muted-foreground flex items-center gap-1">
                        <MapPin className="h-3 w-3" /> POS / Work Location
                    </div>
                    <div className="font-medium bg-muted/50 p-2 rounded-md text-sm">
                        {employee.pos_location?.name || 'Main Office'} - {employee.pos_location?.city || 'Primary City'}
                    </div>
                </div>
            </CardContent>
        </Card>
    );
}
