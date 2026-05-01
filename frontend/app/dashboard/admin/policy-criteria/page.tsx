'use client';

import { useState, useEffect, useCallback } from 'react';
import {
    Plus,
    Search,
    Edit,
    Trash,
    Filter as FilterIcon,
    Loader2,
} from 'lucide-react';
import { useAuth } from '@/lib/auth';
import { useLanguage } from '@/contexts/language-context';

import { Button } from '@/components/ui/button';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { Textarea } from '@/components/ui/textarea';
import {
    Table,
    TableBody,
    TableCell,
    TableHead,
    TableHeader,
    TableRow,
} from '@/components/ui/table';
import { Badge } from '@/components/ui/badge';
import {
    Dialog,
    DialogContent,
    DialogDescription,
    DialogFooter,
    DialogHeader,
    DialogTitle,
} from '@/components/ui/dialog';
import {
    Select,
    SelectContent,
    SelectItem,
    SelectTrigger,
    SelectValue,
} from '@/components/ui/select';
import { useToast } from '@/components/ui/use-toast';
import {
    premiumPolicyApi,
    PremiumPolicyCriteria,
} from '@/lib/premium-policy-api';

export default function PolicyCriteriaPage() {
    const { t } = useLanguage();
    const { user } = useAuth();
    const { toast } = useToast();
    const [criteria, setCriteria] = useState<PremiumPolicyCriteria[]>([]);
    const [loading, setLoading] = useState(true);
    const [search, setSearch] = useState('');
    const [saving, setSaving] = useState(false);

    // Define field and operator options with translations
    const FIELD_OPTIONS = [
        { value: 'driver_age', label: t('criteria.fields.driver_age', 'Driver Age') },
        { value: 'vehicle_age', label: t('criteria.fields.vehicle_age', 'Vehicle Age') },
        { value: 'vehicle_value', label: t('criteria.fields.vehicle_value', 'Vehicle Value') },
        { value: 'number_of_accidents_at_fault', label: t('criteria.fields.accident_count', 'Accidents at Fault') },
        { value: 'driving_experience_years', label: t('criteria.fields.driving_experience', 'Driving Experience (Years)') },
        { value: 'license_type', label: t('criteria.fields.license_type', 'License Type') },
        { value: 'vehicle_type', label: t('criteria.fields.vehicle_type', 'Vehicle Type') },
        { value: 'engine_capacity', label: t('criteria.fields.engine_capacity', 'Engine Capacity (cc)') },
        { value: 'number_of_seats', label: t('criteria.fields.seat_count', 'Number of Seats') },
        { value: 'mileage', label: t('criteria.fields.mileage', 'Mileage (km)') },
    ];

    const OPERATOR_OPTIONS = [
        { value: '==', label: t('criteria.operators.equals', '= (equals)') },
        { value: '!=', label: t('criteria.operators.not_equal', '≠ (not equal)') },
        { value: '>', label: t('criteria.operators.greater_than', '> (greater than)') },
        { value: '>=', label: t('criteria.operators.greater_equal', '≥ (greater or equal)') },
        { value: '<', label: t('criteria.operators.less_than', '< (less than)') },
        { value: '<=', label: t('criteria.operators.less_equal', '≤ (less or equal)') },
        { value: 'in', label: t('criteria.operators.in', 'in (one of)') },
    ];

    // Form state
    const [dialogOpen, setDialogOpen] = useState(false);
    const [editingCriteria, setEditingCriteria] = useState<PremiumPolicyCriteria | null>(null);
    const [formName, setFormName] = useState('');
    const [formDescription, setFormDescription] = useState('');
    const [formField, setFormField] = useState('');
    const [formOperator, setFormOperator] = useState('');
    const [formValue, setFormValue] = useState('');

    const loadCriteria = useCallback(async () => {
        setLoading(true);
        try {
            const data = await premiumPolicyApi.getCriteria();
            setCriteria(Array.isArray(data) ? data : []);
        } catch (error) {
            console.error('Failed to load criteria:', error);
        } finally {
            setLoading(false);
        }
    }, []);

    useEffect(() => {
        loadCriteria();
    }, [loadCriteria]);

    const resetForm = () => {
        setFormName('');
        setFormDescription('');
        setFormField('');
        setFormOperator('');
        setFormValue('');
        setEditingCriteria(null);
    };

    const openCreate = () => {
        resetForm();
        setDialogOpen(true);
    };

    const openEdit = (c: PremiumPolicyCriteria) => {
        setEditingCriteria(c);
        setFormName(c.name || '');
        setFormDescription(c.description || '');
        setFormField(c.field_name);
        setFormOperator(c.operator);
        setFormValue(c.value);
        setDialogOpen(true);
    };

    const handleSave = async () => {
        if (!formField || !formOperator || !formValue) {
            toast({
                title: t('common.error', 'Error'),
                description: t('criteria.fill_required', 'Please fill in field, operator, and value.'),
                variant: 'destructive',
            });
            return;
        }

        setSaving(true);
        try {
            const payload = {
                name: formName.trim() || `${formField} ${formOperator} ${formValue}`,
                description: formDescription.trim() || undefined,
                field_name: formField,
                operator: formOperator,
                value: formValue.trim(),
            };

            if (editingCriteria) {
                await premiumPolicyApi.updateCriteria(editingCriteria.id, payload);
                toast({ title: t('common.success', 'Success'), description: t('criteria.updated', 'Criteria updated.') });
            } else {
                await premiumPolicyApi.createCriteria(payload);
                toast({ title: t('common.success', 'Success'), description: t('criteria.created', 'Criteria created.') });
            }

            setDialogOpen(false);
            resetForm();
            loadCriteria();
        } catch (error: any) {
            toast({
                title: t('common.error', 'Error'),
                description: error?.response?.data?.detail || t('criteria.save_failed', 'Failed to save criteria.'),
                variant: 'destructive',
            });
        } finally {
            setSaving(false);
        }
    };

    const handleDelete = async (id: string) => {
        if (!confirm(t('criteria.confirm_delete', 'Are you sure you want to delete this criteria?'))) return;
        try {
            await premiumPolicyApi.deleteCriteria(id);
            toast({ title: t('common.success', 'Success'), description: t('criteria.deleted', 'Criteria deleted.') });
            loadCriteria();
        } catch (error) {
            toast({
                title: t('common.error', 'Error'),
                description: t('criteria.delete_failed', 'Failed to delete criteria.'),
                variant: 'destructive',
            });
        }
    };

    const filtered = criteria.filter((c) => {
        if (!search) return true;
        const q = search.toLowerCase();
        return (
            c.name?.toLowerCase().includes(q) ||
            c.field_name.toLowerCase().includes(q) ||
            c.value.toLowerCase().includes(q)
        );
    });

    return (
        <div className="space-y-6">
            <div className="flex items-center justify-between">
                <div>
                    <h2 className="text-3xl font-bold tracking-tight">
                        {t('criteria.title', 'Policy Criteria')}
                    </h2>
                    <p className="text-muted-foreground">
                        {t('criteria.description', 'Define eligibility criteria that match client details to premium policies for quote generation.')}
                    </p>
                </div>
                <Button onClick={openCreate}>
                    <Plus className="mr-2 h-4 w-4" />
                    {t('criteria.add_new', 'Add Criteria')}
                </Button>
            </div>

            <Card>
                <CardHeader>
                    <div className="flex items-center justify-between">
                        <CardTitle className="flex items-center gap-2">
                            <FilterIcon className="h-5 w-5 text-primary" />
                            {t('criteria.all_criteria', 'All Criteria')}
                        </CardTitle>
                        <div className="relative w-64">
                            <Search className="absolute left-2 top-2.5 h-4 w-4 text-muted-foreground" />
                            <Input
                                placeholder={t('criteria.search_placeholder', 'Search criteria...')}
                                value={search}
                                onChange={(e) => setSearch(e.target.value)}
                                className="pl-8"
                            />
                        </div>
                    </div>
                </CardHeader>
                <CardContent>
                    {loading ? (
                        <div className="flex items-center justify-center py-8">
                            <Loader2 className="h-6 w-6 animate-spin text-primary" />
                        </div>
                    ) : filtered.length === 0 ? (
                        <div className="text-center py-8 text-muted-foreground">
                            {t('criteria.no_criteria', 'No criteria found. Create one to get started.')}
                        </div>
                    ) : (
                        <Table>
                            <TableHeader>
                                <TableRow>
                                    <TableHead>{t('criteria.col_name', 'Name')}</TableHead>
                                    <TableHead>{t('criteria.col_field', 'Field')}</TableHead>
                                    <TableHead>{t('criteria.col_operator', 'Operator')}</TableHead>
                                    <TableHead>{t('criteria.col_value', 'Value')}</TableHead>
                                    <TableHead>{t('criteria.col_description', 'Description')}</TableHead>
                                    <TableHead className="text-right">{t('common.column.actions', 'Actions')}</TableHead>
                                </TableRow>
                            </TableHeader>
                            <TableBody>
                                {filtered.map((c) => (
                                    <TableRow key={c.id}>
                                        <TableCell className="font-medium">{c.name || '-'}</TableCell>
                                        <TableCell>
                                            <Badge variant="outline">{c.field_name}</Badge>
                                        </TableCell>
                                        <TableCell>
                                            <Badge variant="secondary">{c.operator}</Badge>
                                        </TableCell>
                                        <TableCell>{c.value}</TableCell>
                                        <TableCell className="max-w-[200px] truncate text-muted-foreground">
                                            {c.description || '-'}
                                        </TableCell>
                                        <TableCell className="text-right">
                                            <Button variant="ghost" size="sm" onClick={() => openEdit(c)}>
                                                <Edit className="h-4 w-4" />
                                            </Button>
                                            <Button
                                                variant="ghost"
                                                size="sm"
                                                className="text-red-500"
                                                onClick={() => handleDelete(c.id)}
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

            {/* Create / Edit Dialog */}
            <Dialog open={dialogOpen} onOpenChange={setDialogOpen}>
                <DialogContent className="sm:max-w-[500px]">
                    <DialogHeader>
                        <DialogTitle>
                            {editingCriteria
                                ? t('criteria.edit_title', 'Edit Criteria')
                                : t('criteria.create_title', 'Create Criteria')}
                        </DialogTitle>
                        <DialogDescription>
                            {t('criteria.form_desc', 'Define a condition that client data must match for policy eligibility.')}
                        </DialogDescription>
                    </DialogHeader>

                    <div className="grid gap-4 py-4">
                        <div className="grid gap-2">
                            <Label htmlFor="criteria-name">{t('common.name', 'Name')}</Label>
                            <Input
                                id="criteria-name"
                                value={formName}
                                onChange={(e) => setFormName(e.target.value)}
                                placeholder={t('criteria.name_placeholder', 'e.g. Young Driver')}
                            />
                        </div>

                        <div className="grid gap-2">
                            <Label htmlFor="criteria-field">{t('criteria.field', 'Field')} *</Label>
                            <Select value={formField} onValueChange={setFormField}>
                                <SelectTrigger>
                                    <SelectValue placeholder={t('criteria.select_field', 'Select a field...')} />
                                </SelectTrigger>
                                <SelectContent>
                                    {FIELD_OPTIONS.map((f) => (
                                        <SelectItem key={f.value} value={f.value}>
                                            {f.label}
                                        </SelectItem>
                                    ))}
                                </SelectContent>
                            </Select>
                        </div>

                        <div className="grid grid-cols-2 gap-4">
                            <div className="grid gap-2">
                                <Label htmlFor="criteria-operator">{t('criteria.operator', 'Operator')} *</Label>
                                <Select value={formOperator} onValueChange={setFormOperator}>
                                    <SelectTrigger>
                                        <SelectValue placeholder={t('criteria.select_op', 'Select...')} />
                                    </SelectTrigger>
                                    <SelectContent>
                                        {OPERATOR_OPTIONS.map((op) => (
                                            <SelectItem key={op.value} value={op.value}>
                                                {op.label}
                                            </SelectItem>
                                        ))}
                                    </SelectContent>
                                </Select>
                            </div>
                            <div className="grid gap-2">
                                <Label htmlFor="criteria-value">{t('criteria.value', 'Value')} *</Label>
                                <Input
                                    id="criteria-value"
                                    value={formValue}
                                    onChange={(e) => setFormValue(e.target.value)}
                                    placeholder={t('criteria.value_placeholder', 'e.g. 25')}
                                />
                            </div>
                        </div>

                        <div className="grid gap-2">
                            <Label htmlFor="criteria-desc">{t('common.description', 'Description')}</Label>
                            <Textarea
                                id="criteria-desc"
                                value={formDescription}
                                onChange={(e) => setFormDescription(e.target.value)}
                                placeholder={t('criteria.desc_placeholder', 'Describe what this criteria evaluates...')}
                                rows={2}
                            />
                        </div>
                    </div>

                    <DialogFooter>
                        <Button variant="outline" onClick={() => setDialogOpen(false)} disabled={saving}>
                            {t('common.cancel', 'Cancel')}
                        </Button>
                        <Button onClick={handleSave} disabled={saving}>
                            {saving && <Loader2 className="mr-2 h-4 w-4 animate-spin" />}
                            {editingCriteria ? t('common.save_changes', 'Save Changes') : t('common.create', 'Create')}
                        </Button>
                    </DialogFooter>
                </DialogContent>
            </Dialog>
        </div>
    );
}
