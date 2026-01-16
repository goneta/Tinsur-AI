'use client';

import { useEffect, useState } from 'react';
import { useRouter, useParams } from 'next/navigation';
import { api } from '@/lib/api';
import { Button } from '@/components/ui/button';
import { ArrowLeft, Loader2 } from 'lucide-react';
import { EmployeeInfoCard } from '../components/profile/employee-info-card';
import { PerformanceStats } from '../components/profile/performance-stats';
import { AdvancedFilter, FilterPeriod } from '../components/profile/advanced-filter';
import { PayrollCard } from '../components/profile/payroll-card';
import { CommunicationCard } from '../components/profile/communication-card';
import { Separator } from '@/components/ui/separator';
import { Employee } from '../columns';
import { ProfileUploader } from '@/components/shared/profile-uploader';

export default function EmployeeDetailsPage() {
    const router = useRouter();
    const params = useParams();
    const [employee, setEmployee] = useState<Employee | null>(null);
    const [loading, setLoading] = useState(true);
    const [filterPeriod, setFilterPeriod] = useState<FilterPeriod>('month');
    const [filterValue, setFilterValue] = useState<any>(new Date());

    const fetchEmployee = async () => {
        if (!params?.id) return;
        try {
            const id = Array.isArray(params.id) ? params.id[0] : params.id;
            const res = await api.get(`/employees/${id}`);
            setEmployee(res.data);
        } catch (error) {
            console.error("Failed to fetch employee", error);
        } finally {
            setLoading(false);
        }
    };

    useEffect(() => {
        fetchEmployee();
    }, [params]);

    const handleFilterChange = (period: FilterPeriod, value: any) => {
        setFilterPeriod(period);
        setFilterValue(value);
    };

    if (loading) {
        return <div className="flex justify-center p-10"><Loader2 className="h-8 w-8 animate-spin" /></div>;
    }

    if (!employee) {
        return <div className="p-10 text-center">Employee not found.</div>;
    }

    return (
        <div className="min-h-screen bg-slate-50/50 p-6 lg:p-10">
            <div className="max-w-7xl mx-auto space-y-8">
                {/* Header Section */}
                <div className="flex flex-col md:flex-row md:items-center justify-between gap-4">
                    <div className="flex items-center gap-4">
                        <Button variant="outline" size="icon" onClick={() => router.back()} className="rounded-full h-10 w-10 shadow-sm bg-white">
                            <ArrowLeft className="h-5 w-5" />
                        </Button>
                        <div>
                            <h2 className="text-3xl font-extrabold tracking-tight text-slate-900">{employee.first_name} {employee.last_name}</h2>
                            <p className="text-muted-foreground flex items-center gap-2">
                                <span className="capitalize">{employee.role}</span>
                                <span>•</span>
                                <span>Employee ID: {employee.id.slice(0, 8).toUpperCase()}</span>
                            </p>
                        </div>
                    </div>

                    <div className="flex items-center gap-4">
                        <ProfileUploader
                            entityId={employee.id}
                            entityType="user"
                            currentImageUrl={employee.profile_picture}
                            name={`${employee.first_name} ${employee.last_name}`}
                            className="h-20 w-20 border-2 border-white shadow-md rounded-full"
                            size="lg"
                            onUploadSuccess={fetchEmployee}
                        />
                    </div>
                </div>

                <Separator className="bg-slate-200" />

                {/* Advanced Filter Section */}
                <AdvancedFilter onFilterChange={handleFilterChange} />

                {/* Dashboard Grid */}
                <div className="grid grid-cols-1 lg:grid-cols-12 gap-8">

                    {/* Left Column - Consolidated Info Card & Stats */}
                    <div className="lg:col-span-4 space-y-8">
                        <EmployeeInfoCard employee={employee} onRefresh={fetchEmployee} />

                        {/* Summary Stats moved here */}
                        <div className="space-y-8">
                            <PayrollCard employeeId={employee.id} />
                            <CommunicationCard employeeId={employee.id} />
                        </div>
                    </div>

                    {/* Right Column - Performance & Stats */}
                    <div className="lg:col-span-8 space-y-8">
                        {/* Performance Stats with Tabs, Charts and DataView */}
                        <PerformanceStats
                            employeeId={employee.id}
                            period={filterPeriod}
                            filterValue={filterValue}
                        />
                    </div>
                </div>
            </div>
        </div>
    );
}
