'use client';

import { useState, useEffect, useCallback } from 'react';
import {
    Plus,
    Search,
    Edit,
    Trash,
    ShieldCheck
} from 'lucide-react';
import { useAuth } from '@/lib/auth';
import { useLanguage } from '@/contexts/language-context';

import { Button } from '@/components/ui/button';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Input } from '@/components/ui/input';
import {
    Table,
    TableBody,
    TableCell,
    TableHead,
    TableHeader,
    TableRow,
} from '@/components/ui/table';
import { Badge } from '@/components/ui/badge';
import { ServiceFormDialog } from '@/components/policies/policy-service-form-dialog';
import { policyServiceApi, PolicyService } from '@/lib/policy-service-api';

export default function PolicyServicesPage() {
    const { t, formatPrice } = useLanguage();
    const { user } = useAuth();
    const [services, setServices] = useState<PolicyService[]>([]);
    const [loading, setLoading] = useState(true);
    const [search, setSearch] = useState('');
    const [isCreateOpen, setIsCreateOpen] = useState(false);
    const [editingService, setEditingService] = useState<PolicyService | null>(null);

    const loadServices = useCallback(async () => {
        if (!user?.company_id) return;
        setLoading(true);
        try {
            const data = await policyServiceApi.getAll({
                company_id: user.company_id,
                search: search || undefined
            });
            setServices(data);
        } catch (error) {
            console.error('Failed to load services:', error);
        } finally {
            setLoading(false);
        }
    }, [user?.company_id, search]);

    useEffect(() => {
        loadServices();
    }, [loadServices]);

    const handleDelete = async (id: string) => {
        if (confirm('Are you sure you want to delete this service?')) {
            try {
                await policyServiceApi.delete(id);
                loadServices();
            } catch (error) {
                console.error('Failed to delete service:', error);
            }
        }
    };

    return (
        <div className="space-y-6">
            <div className="flex items-center justify-between">
                <div>
                    <h2 className="text-3xl font-bold tracking-tight">{t('admin.tabs.services', 'Policy Services')}</h2>
                    <p className="text-muted-foreground">Manage optional services and add-ons for policies.</p>
                </div>
                <Button onClick={() => setIsCreateOpen(true)}>
                    <Plus className="mr-2 h-4 w-4" />
                    {t('common.add_new', 'Add Service')}
                </Button>
            </div>

            <Card>
                <CardHeader>
                    <div className="flex items-center justify-between">
                        <CardTitle>{t('services.available_services', 'Available Services')}</CardTitle>
                        <div className="relative w-64">
                            <Search className="absolute left-2 top-2.5 h-4 w-4 text-muted-foreground" />
                            <Input
                                placeholder={t('services.search_placeholder', 'Search services...')}
                                value={search}
                                onChange={(e) => setSearch(e.target.value)}
                                className="pl-8"
                            />
                        </div>
                    </div>
                </CardHeader>
                <CardContent>
                    {loading ? (
                        <div className="text-center py-8 text-muted-foreground">{t('common.loading', 'Loading...')}</div>
                    ) : services.length === 0 ? (
                        <div className="text-center py-8 text-muted-foreground">
                            {t('services.no_services', 'No services found. Create one to get started.')}
                        </div>
                    ) : (
                        <Table>
                            <TableHeader>
                                <TableRow>
                                    <TableHead>{t('common.column.name', 'Name')} (EN)</TableHead>
                                    <TableHead>{t('common.column.name', 'Name')} (FR)</TableHead>
                                    <TableHead>{t('services.price', 'Price')}</TableHead>
                                    <TableHead>{t('common.column.status', 'Status')}</TableHead>
                                    <TableHead className="text-right">{t('common.column.actions', 'Actions')}</TableHead>
                                </TableRow>
                            </TableHeader>
                            <TableBody>
                                {services.map((service) => (
                                    <TableRow key={service.id}>
                                        <TableCell className="font-medium">
                                            <div className="flex items-center gap-2">
                                                <ShieldCheck className="h-4 w-4 text-primary" />
                                                {service.name_en}
                                            </div>
                                        </TableCell>
                                        <TableCell>{service.name_fr || '-'}</TableCell>
                                        <TableCell>
                                            {formatPrice(service.default_price)}
                                        </TableCell>
                                        <TableCell>
                                            <Badge variant={service.is_active ? 'default' : 'secondary'}>
                                                {service.is_active ? 'Active' : 'Inactive'}
                                            </Badge>
                                        </TableCell>
                                        <TableCell className="text-right">
                                            <Button
                                                variant="ghost"
                                                size="sm"
                                                onClick={() => setEditingService(service)}
                                            >
                                                <Edit className="h-4 w-4" />
                                            </Button>
                                            <Button
                                                variant="ghost"
                                                size="sm"
                                                className="text-red-500"
                                                onClick={() => handleDelete(service.id)}
                                            >
                                                <Trash className="h-4 w-4" />
                                            </Button>
                                        </TableCell>
                                    </TableRow>
                                ))}
                            </TableBody>
                        </Table>
                    )}
                </CardContent>
            </Card>

            <ServiceFormDialog
                open={isCreateOpen}
                onOpenChange={setIsCreateOpen}
                companyId={user?.company_id || ''}
                onSuccess={loadServices}
            />

            {editingService && (
                <ServiceFormDialog
                    open={!!editingService}
                    onOpenChange={(open) => !open && setEditingService(null)}
                    service={editingService}
                    companyId={user?.company_id || ''}
                    onSuccess={() => {
                        setEditingService(null);
                        loadServices();
                    }}
                />
            )}
        </div>
    );
}
