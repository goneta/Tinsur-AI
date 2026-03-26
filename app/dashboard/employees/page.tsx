'use client';

import { useEffect, useState, useMemo } from 'react';
import { useRouter } from 'next/navigation';
import { Plus, Search, Camera, Pencil, Eye, Loader2 } from 'lucide-react';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Dialog, DialogContent, DialogDescription, DialogHeader, DialogTitle, DialogTrigger } from '@/components/ui/dialog';
import { api, getProfileImageUrl } from '@/lib/api';
import { EmployeeForm } from './components/employee-form';
import { Badge } from '@/components/ui/badge';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select';
import { UserAvatar } from '@/components/shared/user-avatar';
import { ProfileUploader } from '@/components/shared/profile-uploader';
import { DataView } from '@/components/ui/data-view';
import { columns as getColumns, Employee } from './columns';
import { useToast } from '@/components/ui/use-toast';
import { useLanguage } from '@/contexts/language-context';

export default function EmployeesPage() {
    const router = useRouter();
    const { t } = useLanguage();
    const [employees, setEmployees] = useState<Employee[]>([]);
    const [loading, setLoading] = useState(true);
    const [open, setOpen] = useState(false);
    const [selectedEmployee, setSelectedEmployee] = useState<Employee | null>(null);
    const [editOpen, setEditOpen] = useState(false);
    const [mounted, setMounted] = useState(false);
    const { toast } = useToast();

    useEffect(() => {
        setMounted(true);
        fetchEmployees();
    }, []);

    const fetchEmployees = async () => {
        try {
            const res = await api.get('/employees/');
            setEmployees(res.data);
        } catch (error) {
            console.error("Failed to fetch employees", error);
        } finally {
            setLoading(false);
        }
    };

    // DataView handles filtering, so we pass raw employees

    const handleEdit = (employee: Employee) => {
        setSelectedEmployee(employee);
        setEditOpen(true);
    };

    const handleSuccess = () => {
        // Delay closing to prevent race conditions with form unmounting
        setTimeout(() => {
            setOpen(false);
            setEditOpen(false);
            setSelectedEmployee(null);
            fetchEmployees();
        }, 100);
    };


    const columns = useMemo(() => getColumns(handleEdit, fetchEmployees), [handleEdit, fetchEmployees]);

    if (!mounted) return null;

    const renderEmployeeCard = (employee: Employee) => (
        <Card className="relative overflow-hidden hover:shadow-md transition-shadow">
            <div className="absolute top-2 right-2 flex items-center gap-1 z-10">
                <Button
                    variant="ghost"
                    size="icon"
                    className="h-8 w-8 text-muted-foreground hover:text-foreground"
                    onClick={() => router.push(`/dashboard/employees/${employee.id}`)}
                    title={t('employees.action_view')}
                >
                    <Eye className="h-4 w-4" />
                </Button>
                <Button
                    variant="ghost"
                    size="icon"
                    className="h-8 w-8 text-muted-foreground hover:text-foreground"
                    onClick={() => handleEdit(employee)}
                >
                    <Pencil className="h-4 w-4" />
                    <span className="sr-only">Edit</span>
                </Button>
            </div>
            <CardHeader className="flex flex-col items-center gap-4 bg-muted/20 p-6 pb-2">
                <ProfileUploader
                    entityId={employee.id}
                    entityType="user"
                    currentImageUrl={employee.profile_picture}
                    name={`${employee.first_name} ${employee.last_name}`}
                    className="h-20 w-20 border-4 border-white shadow-sm"
                    size="lg"
                    onUploadSuccess={fetchEmployees}
                />
                <div className="text-center grid gap-1 w-full mt-4">
                    <CardTitle className="text-xl truncate">{employee.first_name} {employee.last_name}</CardTitle>
                    <div className="text-sm text-muted-foreground break-all px-4">{employee.email}</div>
                </div>
            </CardHeader>
            <CardContent className="p-6 grid gap-3 pt-4">
                <div className="flex items-center justify-between text-sm py-1 border-b">
                    <span className="text-muted-foreground">{t('employees.role')}</span>
                    <Badge variant="outline" className="capitalize">{
                        employee.role === 'agent' ? t('employees.role_agent') :
                            employee.role === 'manager' ? t('employees.role_manager') :
                                employee.role
                    }</Badge>
                </div>
                <div className="flex items-center justify-between text-sm py-1 border-b">
                    <span className="text-muted-foreground">{t('employees.job_title')}</span>
                    <span className="font-medium text-right">{employee.employee_profile?.job_title || t('employees.na')}</span>
                </div>
                <div className="flex items-center justify-between text-sm py-1 border-b">
                    <span className="text-muted-foreground">{t('employees.department')}</span>
                    <span className="font-medium text-right">{employee.employee_profile?.department || t('employees.na')}</span>
                </div>
                {employee.phone && (
                    <div className="flex items-center justify-between text-sm py-1 border-b">
                        <span className="text-muted-foreground">{t('employees.phone')}</span>
                        <span className="font-medium text-right">{employee.phone}</span>
                    </div>
                )}
                {employee.pos_location?.city && (
                    <div className="flex items-center justify-between text-sm py-1 border-b">
                        <span className="text-muted-foreground">POS City</span>
                        <span className="font-medium text-right">{employee.pos_location.city}</span>
                    </div>
                )}
            </CardContent>
        </Card>
    );

    return (
        <div className="space-y-6 max-w-7xl mx-auto p-6">
            <div className="flex items-center justify-between">
                <div>
                    <h2 className="text-3xl font-bold tracking-tight">{t('employees.title')}</h2>
                    <p className="text-muted-foreground">{t('employees.desc')}</p>
                </div>
                <Button onClick={() => setOpen(true)}>
                    <Plus className="mr-2 h-4 w-4" /> {t('employees.add_employee')}
                </Button>
            </div>

            <DataView
                columns={columns}
                data={employees}
                renderCard={renderEmployeeCard}
                defaultView="card"
                getRowId={(row) => row.id}
            />

            {/* Dialogs rendered persistently */}
            <Dialog open={open} onOpenChange={setOpen}>
                <DialogContent className="max-w-2xl max-h-[90vh] overflow-y-auto">
                    <DialogHeader>
                        <DialogTitle>{t('employees.add_employee')}</DialogTitle>
                        <DialogDescription>
                            Create a new employee account. They will receive an email with login instructions.
                        </DialogDescription>
                    </DialogHeader>
                    <EmployeeForm onSuccess={handleSuccess} />
                </DialogContent>
            </Dialog>

            <Dialog open={editOpen} onOpenChange={(val) => {
                setEditOpen(val);
                if (!val) setSelectedEmployee(null);
            }}>
                <DialogContent className="max-w-2xl max-h-[90vh] overflow-y-auto">
                    <DialogHeader>
                        <DialogTitle>Edit Employee</DialogTitle>
                    </DialogHeader>
                    <EmployeeForm
                        mode="edit"
                        initialData={selectedEmployee}
                        onSuccess={handleSuccess}
                    />
                </DialogContent>
            </Dialog>
        </div>
    );
}
