'use client';

import { useEffect, useState, useMemo } from 'react';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs';
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { UserAvatar } from '@/components/shared/user-avatar';
import { Badge } from '@/components/ui/badge';
import { Dialog, DialogContent, DialogDescription, DialogHeader, DialogTitle, DialogTrigger } from '@/components/ui/dialog';
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from '@/components/ui/table';
import { api, getProfileImageUrl } from '@/lib/api';
import { PayrollForm } from './components/payroll-form';
import { DataView } from '@/components/ui/data-view';
import { columns as getColumns, Employee } from './columns';
import { EmployeeProfile } from '../employees/components/employee-profile';
import { ProcessPayrollDialog } from './components/process-payroll-dialog';
import { PayslipDialog } from './components/payslip-dialog';
import { Eye, CircleDollarSign, History, Users } from 'lucide-react';
import { useLanguage } from '@/contexts/language-context';
import { formatDate } from '@/lib/utils';

export default function PayrollPage() {
    const { t } = useLanguage();
    const [employees, setEmployees] = useState<Employee[]>([]);
    const [transactions, setTransactions] = useState<any[]>([]);
    const [loading, setLoading] = useState(true);
    const [selectedEmployee, setSelectedEmployee] = useState<Employee | null>(null);
    const [selectedTransaction, setSelectedTransaction] = useState<any | null>(null);
    const [dialogOpen, setDialogOpen] = useState(false);
    const [processDialogOpen, setProcessDialogOpen] = useState(false);
    const [payslipDialogOpen, setPayslipDialogOpen] = useState(false);
    const [profileDialogOpen, setProfileDialogOpen] = useState(false);
    const [mounted, setMounted] = useState(false);

    const fetchData = async () => {
        setLoading(true);
        try {
            const [empRes, transRes] = await Promise.all([
                api.get('/employees/'),
                api.get('/payroll/')
            ]);

            // Map last paid month to employees
            const enhancedEmployees = empRes.data.map((emp: Employee) => {
                const lastTransaction = transRes.data
                    .filter((t: any) => t.employee_id === emp.id)
                    .sort((a: any, b: any) => new Date(b.payment_date).getTime() - new Date(a.payment_date).getTime())[0];
                return {
                    ...emp,
                    last_paid_month: lastTransaction?.payment_month
                };
            });

            setEmployees(enhancedEmployees);
            setTransactions(transRes.data);
        } catch (error) {
            console.error("Failed to fetch data", error);
        } finally {
            setLoading(false);
        }
    };

    useEffect(() => {
        setMounted(true);
        fetchData();
    }, []);

    const handleSuccess = () => {
        setDialogOpen(false);
        fetchData(); // Refresh history
    };

    // DataView handles filtering, so we pass raw employees

    const columns = useMemo(() => getColumns(
        (employee) => {
            setSelectedEmployee(employee);
            setDialogOpen(true);
        },
        (employee) => {
            setSelectedEmployee(employee);
            setProfileDialogOpen(true);
        }
    ), []);

    if (!mounted) return null;

    const renderEmployeeCard = (employee: Employee) => (
        <Card className="relative overflow-hidden hover:shadow-md transition-shadow">
            <CardHeader className="flex flex-col items-center gap-4 bg-muted/20 p-6 pb-2">
                <div className="relative group cursor-pointer" onClick={() => { setSelectedEmployee(employee); setProfileDialogOpen(true); }} title="View Profile">
                    <UserAvatar
                        src={getProfileImageUrl(employee.profile_picture)}
                        alt={`${employee.first_name} ${employee.last_name}`}
                        className="h-20 w-20 border-4 border-white shadow-sm"
                        size="lg"
                        fallback={
                            <div className="text-xl font-bold text-muted-foreground">
                                {employee.first_name?.[0]}{employee.last_name?.[0]}
                            </div>
                        }
                    />
                </div>
                <div className="text-center grid gap-1 w-full mt-4">
                    <CardTitle className="text-xl truncate hover:text-primary cursor-pointer" onClick={() => { setSelectedEmployee(employee); setProfileDialogOpen(true); }}>
                        {employee.first_name} {employee.last_name}
                    </CardTitle>
                    <div className="text-sm text-muted-foreground">
                        {employee.last_paid_month ? t('payroll.last_paid', 'Last Paid: {0}').replace('{0}', employee.last_paid_month) : t('payroll.not_paid', "Not paid yet")}
                    </div>
                </div>
            </CardHeader>
            <CardContent className="p-6 grid gap-3 pt-4">
                <div className="flex items-center justify-between text-sm py-1 border-b">
                    <span className="text-muted-foreground">{t('payroll.salary', 'Salary')}</span>
                    <span className="font-semibold text-primary">
                        {employee.employee_profile?.base_salary ? new Intl.NumberFormat('fr-FR', { style: 'currency', currency: employee.employee_profile.currency || 'XOF' }).format(employee.employee_profile.base_salary) : 'Not set'}
                    </span>
                </div>
                <div className="flex items-center justify-between text-sm py-1 border-b">
                    <span className="text-muted-foreground">{t('payroll.method', 'Method')}</span>
                    <span className="capitalize">{employee.employee_profile?.payment_method?.replace('_', ' ') || 'Not set'}</span>
                </div>
                <div className="flex items-center justify-between text-sm py-1 border-b">
                    <span className="text-muted-foreground">{t('payroll.role', 'Role')}</span>
                    <Badge variant="outline" className="capitalize">{employee.role}</Badge>
                </div>
                <Button className="mt-4 w-full" onClick={() => { setSelectedEmployee(employee); setDialogOpen(true); }}>
                    <CircleDollarSign className="mr-2 h-4 w-4" /> {t('payroll.pay_now', 'Pay Now')}
                </Button>
            </CardContent>
        </Card>
    );

    return (
        <div className="space-y-6 max-w-7xl mx-auto p-6">
            <div className="flex items-center justify-between">
                <div>
                    <h2 className="text-3xl font-bold tracking-tight">{t('payroll.title', 'Payroll')}</h2>
                    <p className="text-muted-foreground">{t('payroll.desc', 'Process salaries and view payment history.')}</p>
                </div>
                <Button onClick={() => setProcessDialogOpen(true)}>
                    <CircleDollarSign className="mr-2 h-4 w-4" /> {t('payroll.process_monthly', 'Process Monthly Payroll')}
                </Button>
            </div>

            <Tabs defaultValue="process" className="space-y-4">
                <TabsList>
                    <TabsTrigger value="process" className="flex items-center gap-2"><Users className="h-4 w-4" /> {t('payroll.tab_process', 'Process Payroll')}</TabsTrigger>
                    <TabsTrigger value="history" className="flex items-center gap-2"><History className="h-4 w-4" /> {t('payroll.tab_history', 'Transaction History')}</TabsTrigger>
                </TabsList>

                <TabsContent value="process" className="space-y-4">
                    <DataView
                        columns={columns}
                        data={employees}
                        renderCard={renderEmployeeCard}
                        defaultView="card"
                    />
                </TabsContent>

                <TabsContent value="history">
                    <Card>
                        <CardHeader>
                            <CardTitle>{t('payroll.transactions_title', 'Transactions')}</CardTitle>
                            <CardDescription>{t('payroll.transactions_desc', 'Recent payroll payments processed.')}</CardDescription>
                        </CardHeader>
                        <CardContent>
                            <Table>
                                <TableHeader>
                                    <TableRow>
                                        <TableHead>{t('payroll.date', 'Date')}</TableHead>
                                        <TableHead>{t('payroll.month', 'Month')}</TableHead>
                                        <TableHead>{t('payroll.employee', 'Employee')}</TableHead>
                                        <TableHead>{t('payroll.description', 'Description')}</TableHead>
                                        <TableHead>{t('payroll.method', 'Method')}</TableHead>
                                        <TableHead>{t('payroll.amount', 'Amount')}</TableHead>
                                        <TableHead>{t('payroll.status', 'Status')}</TableHead>
                                        <TableHead className="text-right">{t('payroll.action', 'Action')}</TableHead>
                                    </TableRow>
                                </TableHeader>
                                <TableBody>
                                    {transactions.map((tItem) => {
                                        const emp = employees.find(e => e.id === tItem.employee_id);
                                        const empName = emp ? `${emp.first_name} ${emp.last_name}` : 'Unknown';

                                        return (
                                            <TableRow key={tItem.id}>
                                                <TableCell>{formatDate(tItem.payment_date)}</TableCell>
                                                <TableCell><Badge variant="outline">{tItem.payment_month || '-'}</Badge></TableCell>
                                                <TableCell className="font-medium hover:text-primary cursor-pointer" onClick={() => {
                                                    const e = employees.find(emp => emp.id === tItem.employee_id);
                                                    if (e) { setSelectedEmployee(e); setProfileDialogOpen(true); }
                                                }}>{empName}</TableCell>
                                                <TableCell>{tItem.description}</TableCell>
                                                <TableCell className="capitalize">{tItem.payment_method?.replace('_', ' ')}</TableCell>
                                                <TableCell className="font-bold">{new Intl.NumberFormat('fr-FR', { style: 'currency', currency: tItem.currency }).format(tItem.net_pay || tItem.amount)}</TableCell>
                                                <TableCell><Badge variant={tItem.status === 'paid' ? 'default' : 'secondary'}>{tItem.status}</Badge></TableCell>
                                                <TableCell className="text-right">
                                                    <Button variant="ghost" size="sm" onClick={() => { setSelectedTransaction(tItem); setPayslipDialogOpen(true); }}>
                                                        <Eye className="h-4 w-4 mr-2" /> {t('payroll.view_details', 'Details')}
                                                    </Button>
                                                </TableCell>
                                            </TableRow>
                                        )
                                    })}
                                    {transactions.length === 0 && (
                                        <TableRow>
                                            <TableCell colSpan={8} className="text-center text-muted-foreground">{t('common.no_results', 'No transactions found.')}</TableCell>
                                        </TableRow>
                                    )}
                                </TableBody>
                            </Table>
                        </CardContent>
                    </Card>
                </TabsContent>
            </Tabs>

            <Dialog open={dialogOpen} onOpenChange={setDialogOpen}>
                <DialogContent>
                    <DialogHeader>
                        <DialogTitle>{t('payroll.dialog_process_title', 'Process Payment')}</DialogTitle>
                        <DialogDescription>{t('payroll.dialog_process_desc', 'Enter payment details for {0}.').replace('{0}', selectedEmployee?.first_name || '')}</DialogDescription>
                    </DialogHeader>
                    {selectedEmployee && <PayrollForm employee={selectedEmployee} onSuccess={handleSuccess} />}
                </DialogContent>
            </Dialog>

            <Dialog open={profileDialogOpen} onOpenChange={setProfileDialogOpen}>
                <DialogContent className="max-w-2xl">
                    <DialogHeader>
                        <DialogTitle>Employee Profile</DialogTitle>
                    </DialogHeader>
                    {selectedEmployee && <EmployeeProfile employee={selectedEmployee} />}
                </DialogContent>
            </Dialog>

            <ProcessPayrollDialog
                isOpen={processDialogOpen}
                onOpenChange={setProcessDialogOpen}
                onSuccess={() => { setProcessDialogOpen(false); fetchData(); }}
            />

            <PayslipDialog
                isOpen={payslipDialogOpen}
                onOpenChange={setPayslipDialogOpen}
                data={selectedTransaction ? {
                    ...selectedTransaction,
                    employee_name: employees.find(e => e.id === selectedTransaction.employee_id)?.first_name + ' ' + employees.find(e => e.id === selectedTransaction.employee_id)?.last_name
                } : null}
            />
        </div >
    );
}
