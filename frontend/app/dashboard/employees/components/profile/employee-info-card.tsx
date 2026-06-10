'use client';

import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import {
    User, Phone, MapPin, Briefcase, DollarSign, ShieldCheck,
    GraduationCap, Award, ScrollText
} from 'lucide-react';
import { Badge } from '@/components/ui/badge';
import { Separator } from '@/components/ui/separator';
import { ProfileUploader } from '@/components/shared/profile-uploader';
import { Employee } from '../../columns';

interface EmployeeInfoCardProps {
    employee: Employee;
    onRefresh: () => void;
}

export function EmployeeInfoCard({ employee, onRefresh }: EmployeeInfoCardProps) {
    const formatSalary = (amount?: number, currency?: string) => {
        if (!amount) return 'Not set';
        return new Intl.NumberFormat('fr-FR', {
            style: 'currency',
            currency: currency || 'XOF'
        }).format(amount);
    };

    // Mock education data as requested
    const educationItems = [
        { type: 'Degree', title: 'Master in Management', institution: 'ESSEC Business School', year: '2018', icon: <GraduationCap className="h-4 w-4" /> },
        { type: 'Diploma', title: 'Insurance Professional', institution: 'Insurance Institute', year: '2016', icon: <ScrollText className="h-4 w-4" /> },
        { type: 'Certificate', title: 'Risk Analysis Expert', institution: 'Global Risk Org', year: '2020', icon: <Award className="h-4 w-4" /> },
    ];

    return (
        <Card className="relative overflow-hidden">
            <CardHeader className="pb-2">
                <CardTitle className="text-xl font-bold flex items-center gap-2">
                    <User className="h-5 w-5 text-primary" />
                    Employee Details
                </CardTitle>
            </CardHeader>

            <CardContent className="space-y-6">
                {/* 1. Employee Details Section */}
                <div className="space-y-4">
                    <div className="space-y-1">
                        <div className="text-xs text-muted-foreground uppercase tracking-wider font-semibold">Full Name</div>
                        <div className="font-bold text-lg">{employee.first_name} {employee.last_name}</div>
                    </div>

                    <div className="flex items-center gap-2 text-sm">
                        <Phone className="h-4 w-4 text-muted-foreground" />
                        <span className="font-medium text-slate-700">{employee.phone || 'Not provided'}</span>
                    </div>

                    <div className="flex items-center gap-2 text-sm">
                        <MapPin className="h-4 w-4 text-muted-foreground" />
                        <span className="font-medium text-slate-700">{employee.pos_location?.city || 'Not provided'}</span>
                    </div>
                </div>

                <Separator className="bg-slate-100" />

                {/* 2. Employee Position Section */}
                <div className="space-y-4">
                    <div className="flex items-center gap-2 text-sm font-bold text-slate-900 uppercase tracking-tighter">
                        <Briefcase className="h-4 w-4 text-primary" />
                        Position Details
                    </div>

                    <div className="grid grid-cols-2 gap-4">
                        <div className="space-y-1">
                            <div className="text-xs text-muted-foreground">Role</div>
                            <Badge variant="secondary" className="capitalize">{employee.role}</Badge>
                        </div>
                        <div className="space-y-1">
                            <div className="text-xs text-muted-foreground">Job Type</div>
                            <div className="font-semibold text-sm">{employee.employee_profile?.job_title || 'N/A'}</div>
                        </div>
                    </div>

                    <div className="grid grid-cols-2 gap-4">
                        <div className="space-y-1">
                            <div className="text-xs text-muted-foreground">Salary</div>
                            <div className="text-lg font-bold text-primary">
                                {formatSalary(employee.employee_profile?.base_salary, employee.employee_profile?.currency)}
                            </div>
                        </div>
                        <div className="space-y-1">
                            <div className="text-xs text-muted-foreground">POS / Work Location</div>
                            <div className="font-semibold text-sm">{employee.pos_location?.name || 'Main Office'}</div>
                        </div>
                    </div>
                </div>

                <Separator className="bg-slate-100" />

                {/* 3. Employee Education Section */}
                <div className="space-y-4">
                    <div className="flex items-center gap-2 text-sm font-bold text-slate-900 uppercase tracking-tighter">
                        <GraduationCap className="h-4 w-4 text-primary" />
                        Education
                    </div>

                    <div className="space-y-3">
                        {educationItems.map((item, idx) => (
                            <div key={idx} className="flex gap-3 items-start group">
                                <div className="mt-1 p-1.5 rounded-full bg-slate-100 text-slate-600 group-hover:bg-primary/10 group-hover:text-primary transition-colors">
                                    {item.icon}
                                </div>
                                <div className="flex-1 min-w-0">
                                    <div className="flex justify-between items-center gap-2">
                                        <span className="font-bold text-sm truncate">{item.title}</span>
                                        <span className="text-xs font-medium text-slate-400 shrink-0">{item.year}</span>
                                    </div>
                                    <div className="text-xs text-muted-foreground truncate">{item.institution}</div>
                                </div>
                            </div>
                        ))}
                    </div>
                </div>
            </CardContent>
        </Card>
    );
}
