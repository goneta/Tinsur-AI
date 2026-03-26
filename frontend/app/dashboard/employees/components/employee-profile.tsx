'use client';

import { Employee } from '../columns';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Avatar, AvatarFallback, AvatarImage } from '@/components/ui/avatar';
import { Badge } from '@/components/ui/badge';
import { getProfileImageUrl } from '@/lib/api';
import { Label } from '@/components/ui/label';
import { Separator } from '@/components/ui/separator';

interface EmployeeProfileProps {
    employee: Employee;
}

export function EmployeeProfile({ employee }: EmployeeProfileProps) {
    return (
        <div className="space-y-6">
            <div className="flex flex-col items-center gap-4 py-4">
                <Avatar className="h-24 w-24 border-4 border-white shadow-sm ring-1 ring-muted">
                    <AvatarImage
                        src={getProfileImageUrl(employee.profile_picture)}
                        className="object-cover"
                    />
                    <AvatarFallback className="bg-gray-100 text-gray-600 text-xl font-bold">
                        {employee.first_name?.[0]}{employee.last_name?.[0]}
                    </AvatarFallback>
                </Avatar>
                <div className="text-center">
                    <h3 className="text-2xl font-bold">{employee.first_name} {employee.last_name}</h3>
                    <p className="text-muted-foreground">{employee.role.toUpperCase()}</p>
                </div>
            </div>

            <Separator />

            <div className="grid gap-6 md:grid-cols-2">
                <div className="space-y-4">
                    <h4 className="font-semibold text-sm uppercase text-muted-foreground tracking-wider">Contact Information</h4>
                    <div className="space-y-1">
                        <Label className="text-xs text-muted-foreground">Email</Label>
                        <div className="font-medium">{employee.email}</div>
                    </div>
                    <div className="space-y-1">
                        <Label className="text-xs text-muted-foreground">Phone</Label>
                        <div className="font-medium">{employee.phone || 'Not provided'}</div>
                    </div>
                </div>

                <div className="space-y-4">
                    <h4 className="font-semibold text-sm uppercase text-muted-foreground tracking-wider">Job Details</h4>
                    <div className="space-y-1">
                        <Label className="text-xs text-muted-foreground">Department</Label>
                        <div className="font-medium">{employee.employee_profile?.department || 'Not set'}</div>
                    </div>
                    <div className="space-y-1">
                        <Label className="text-xs text-muted-foreground">Job Title</Label>
                        <div className="font-medium">{employee.employee_profile?.job_title || 'Not set'}</div>
                    </div>
                </div>
            </div>

            <Separator />

            <div className="space-y-4">
                <h4 className="font-semibold text-sm uppercase text-muted-foreground tracking-wider">Payroll Information</h4>
                <div className="grid gap-6 md:grid-cols-3">
                    <div className="space-y-1">
                        <Label className="text-xs text-muted-foreground">Base Salary</Label>
                        <div className="font-medium text-primary">
                            {employee.employee_profile?.base_salary ? new Intl.NumberFormat('fr-FR', { style: 'currency', currency: employee.employee_profile.currency || 'XOF' }).format(employee.employee_profile.base_salary) : 'Not set'}
                        </div>
                    </div>
                    <div className="space-y-1">
                        <Label className="text-xs text-muted-foreground">Payment Method</Label>
                        <div className="font-medium capitalize">{employee.employee_profile?.payment_method?.replace('_', ' ') || 'Not set'}</div>
                    </div>
                    <div className="space-y-1">
                        <Label className="text-xs text-muted-foreground">Currency</Label>
                        <div className="font-medium">{employee.employee_profile?.currency || 'XOF'}</div>
                    </div>
                </div>
            </div>
        </div>
    );
}
