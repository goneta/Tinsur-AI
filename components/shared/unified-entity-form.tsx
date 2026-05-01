'use client';

import React, { useState, useEffect } from 'react';
// import { Client, ClientDriver } from '@/types/client';
import { clientApi } from '@/lib/client-api';
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from "@/components/ui/table";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select";
import { Loader2, Pencil, Check, X, ArrowLeft, Upload, FileText, Scan } from "lucide-react";
import { useToast } from "@/components/ui/use-toast";
import { UNIFIED_ENTITY_FIELDS, CLIENT_ADMIN_FIELDS, FieldDefinition } from '@/config/field-definitions';
import { formatApiError } from '@/lib/api';
import { useRouter } from 'next/navigation';

type EntityType = 'client' | 'driver';

// Maps unified form field keys to Client model field names.
// Driver fields match directly, but Client uses different names for some fields.
const CLIENT_FIELD_MAP: Record<string, string> = {
    'phone_number': 'phone',
    'license_number': 'driving_licence_number',
};

// Reverse map: Client model field names → unified form field keys (for edit mode display)
const CLIENT_FIELD_REVERSE_MAP: Record<string, string> = {
    'phone': 'phone_number',
    'driving_licence_number': 'license_number',
};

/**
 * Convert form field key to the correct API field name based on entity type.
 */
function toApiField(field: string, type: EntityType): string {
    if (type === 'client' && CLIENT_FIELD_MAP[field]) {
        return CLIENT_FIELD_MAP[field];
    }
    return field;
}

/**
 * Convert entity data from API format to form display format.
 * Ensures unified field keys like 'phone_number' are populated from 'phone', etc.
 */
function mapEntityToFormData(entity: any, type: EntityType): any {
    if (!entity || type !== 'client') return { ...entity };
    const mapped = { ...entity };
    // Populate form field keys from client model fields
    if (entity.phone && !mapped.phone_number) mapped.phone_number = entity.phone;
    if (entity.driving_licence_number && !mapped.license_number) mapped.license_number = entity.driving_licence_number;
    return mapped;
}

interface UnifiedEntityFormProps {
    type: EntityType;
    mode: 'create' | 'edit';
    entity?: any; // Partial<Client> or Partial<ClientDriver>
    clientId?: string;
    onUpdate: () => void;
    onBack: () => void;
}

export function UnifiedEntityForm({ type, mode, entity, clientId, onUpdate, onBack }: UnifiedEntityFormProps) {
    const { toast } = useToast();
    const router = useRouter();
    const [loading, setLoading] = useState(false);
    const [isScanning, setIsScanning] = useState(false);
    const [editingField, setEditingField] = useState<string | null>(null);
    const [tempValue, setTempValue] = useState<any>(null);
    const [formData, setFormData] = useState<any>({
        ...mapEntityToFormData(entity, type),
        ...(type === 'client' ? { country: "Côte d'Ivoire", client_type: 'individual' } : { client_id: clientId })
    });

    // Decide which fields to show
    const baseFields = UNIFIED_ENTITY_FIELDS;
    const adminFields = type === 'client' ? CLIENT_ADMIN_FIELDS : [];
    const allFields = [...baseFields, ...adminFields];

    useEffect(() => {
        if (entity) {
            setFormData((prev: any) => ({ ...prev, ...mapEntityToFormData(entity, type) }));
        }
    }, [entity, type]);

    const handleInputChange = (field: string, value: any) => {
        setFormData((prev: any) => ({ ...prev, [field]: value }));
    };

    const startEditing = (field: string, value: any) => {
        setEditingField(field);
        setTempValue(value);
    };

    const cancelEditing = () => {
        setEditingField(null);
        setTempValue(null);
    };

    // EDIT MODE: Save single field
    const saveField = async (field: string) => {
        setLoading(true);
        try {
            // Map form field key to API field name (e.g., phone_number → phone for clients)
            const apiField = toApiField(field, type);
            const payload = { [apiField]: tempValue };
            if (type === 'client' && entity.id) {
                await clientApi.updateClient(entity.id, payload);
            } else if (type === 'driver' && entity.id && clientId) {
                await clientApi.updateDriver(clientId, entity.id, payload);
            }
            toast({ title: "Success", description: "Updated successfully." });
            onUpdate();
            setEditingField(null);
        } catch (error: any) {
            const msg = formatApiError(error.response?.data?.detail) || "Failed to update";
            toast({ title: "Error", description: msg, variant: "destructive" });
        } finally {
            setLoading(false);
        }
    };

    // CREATE MODE: Save entire entity
    const saveNewEntity = async () => {
        if (type === 'client' && (!formData.email || !formData.phone_number)) {
            toast({ title: "Error", description: "Email and Phone are required for clients.", variant: "destructive" });
            return;
        }

        setLoading(true);
        try {
            if (type === 'client') {
                const payload = { ...formData, risk_profile: 'medium', kyc_status: 'pending' };
                if (payload.date_of_birth === '') payload.date_of_birth = null;
                // Remove File if accidentally present in JSON payload
                if (payload.driving_license_url instanceof File) delete payload.driving_license_url;

                // Map unified form field names to Client model field names
                if (payload.phone_number && !payload.phone) {
                    payload.phone = payload.phone_number;
                }
                delete payload.phone_number; // Not a Client model field

                if (payload.license_number && !payload.driving_licence_number) {
                    payload.driving_licence_number = payload.license_number;
                }
                delete payload.license_number; // Not a Client model field

                // Map additional driver-only fields that exist on Client model
                // postal_code is a driver field, not on Client - remove to avoid API error
                delete payload.postal_code;

                const newClient = await clientApi.createClient(payload);
                toast({
                    title: "Client created",
                    description: "Would you like to view the full profile?",
                    action: <Button variant="outline" size="sm" onClick={() => router.push(`/dashboard/clients/${newClient.id}`)}>View Profile</Button>
                });
            } else {
                if (!clientId) {
                    toast({ title: "Error", description: "Internal error: Client ID is missing.", variant: "destructive" });
                    return;
                }

                // Sanitize payload for JSON
                const payload = { ...formData };
                if (payload.driving_license_url instanceof File) delete payload.driving_license_url;

                const createdDriver = await clientApi.createDriver(clientId, payload);

                // Upload license if present in create mode
                if (formData.driving_license_url instanceof File) {
                    await clientApi.uploadDriverLicense(clientId, createdDriver.id, formData.driving_license_url);
                }
                toast({ title: "Success", description: "Driver added successfully." });
            }
            onUpdate();
        } catch (error: any) {
            console.error(`Failed to create ${type}:`, error);
            const msg = formatApiError(error.response?.data?.detail) || error.message || `Failed to create ${type}`;
            toast({ title: "Error", description: msg, variant: "destructive" });
        } finally {
            setLoading(false);
        }
    };

    const handleFileUpload = async (e: React.ChangeEvent<HTMLInputElement>) => {
        const file = e.target.files?.[0];
        if (!file) return;

        if (mode === 'edit' && entity.id) {
            setLoading(true);
            try {
                if (type === 'driver' && clientId) {
                    await clientApi.uploadDriverLicense(clientId, entity.id, file);
                } else if (type === 'client') {
                    // Clients also have driving_licence_url in schema
                    await clientApi.uploadDriverLicense(entity.id, entity.id, file); // For now, client.id acts as both
                }
                toast({ title: "Success", description: "File uploaded successfully." });
                onUpdate();
            } catch (error: any) {
                toast({ title: "Error", description: formatApiError(error.response?.data?.detail) || "Upload failed", variant: "destructive" });
            } finally {
                setLoading(false);
            }
        } else {
            handleInputChange('driving_license_url', file);
        }
    };

    const handleScan = async (e: React.ChangeEvent<HTMLInputElement>, scanType: 'identity_document' | 'car_papers') => {
        const file = e.target.files?.[0];
        if (!file) return;

        setIsScanning(true);
        try {
            const result = await clientApi.uploadAndParseKycDocument(file, scanType);
            if (scanType === 'identity_document') {
                if (result.full_name) {
                    const parts = result.full_name.split(' ');
                    if (parts.length > 1) {
                        handleInputChange('first_name', parts[0]);
                        handleInputChange('last_name', parts.slice(1).join(' '));
                    } else {
                        handleInputChange('first_name', result.full_name);
                    }
                }
                if (result.id_number) handleInputChange('license_number', result.id_number);
                if (result.dob) handleInputChange('date_of_birth', result.dob);
            }
            toast({ title: "Scan Complete", description: "Successfully extracted information." });
        } catch (err: any) {
            toast({ title: "Scan Failed", description: formatApiError(err.response?.data?.detail) || "AI parsing failed", variant: "destructive" });
        } finally {
            setIsScanning(false);
        }
    };

    const renderInput = (field: FieldDefinition) => {
        const value = mode === 'create' ? formData[field.key] : tempValue;
        const onChange = (val: any) => {
            if (mode === 'create') handleInputChange(field.key, val);
            else setTempValue(val);
        };

        switch (field.type) {
            case 'select':
                return (
                    <Select value={String(value || '')} onValueChange={onChange}>
                        <SelectTrigger className="w-full h-8 rounded-xl border-gray-200">
                            <SelectValue placeholder="Select..." />
                        </SelectTrigger>
                        <SelectContent>
                            {field.options?.map(opt => (
                                <SelectItem key={opt.value} value={opt.value}>{opt.label}</SelectItem>
                            ))}
                        </SelectContent>
                    </Select>
                );
            case 'number':
                return (
                    <Input
                        type="number"
                        value={value ?? ''}
                        onChange={(e) => onChange(e.target.value === '' ? null : Number(e.target.value))}
                        className="w-full h-8 rounded-xl border-gray-200"
                    />
                );
            case 'date':
                return (
                    <Input
                        type="date"
                        value={value ? new Date(value).toISOString().split('T')[0] : ''}
                        onChange={(e) => onChange(e.target.value)}
                        className="w-full h-8 rounded-xl border-gray-200"
                    />
                );
            case 'file':
                return (
                    <div className="flex items-center gap-2">
                        <Input
                            type="file"
                            accept="image/*"
                            onChange={handleFileUpload}
                            className="text-xs rounded-xl"
                        />
                    </div>
                );
            default:
                return (
                    <Input
                        value={value || ''}
                        onChange={(e) => onChange(e.target.value)}
                        className="w-full h-8 rounded-xl border-gray-200"
                    />
                );
        }
    };

    return (
        <div className="space-y-6 animate-in fade-in duration-300">
            <div className="flex items-center justify-between">
                <div className="flex items-center gap-4">
                    <Button variant="ghost" onClick={onBack} className="rounded-xl font-bold hover:bg-gray-100">
                        <ArrowLeft className="h-4 w-4 mr-2" /> Back
                    </Button>
                    <h2 className="text-2xl font-black text-gray-900">
                        {mode === 'create' ? `Add New ${type === 'client' ? 'Client' : 'Driver'}` : `${type === 'client' ? 'Client' : 'Driver'} Details: ${entity.first_name || ''} ${entity.last_name || ''}`}
                    </h2>
                </div>

                {mode === 'create' && type === 'client' && (
                    <div className="flex gap-2">
                        <div className="relative">
                            <Input type="file" className="hidden" id="id-scan-input" accept="image/*" onChange={(e) => handleScan(e, 'identity_document')} disabled={isScanning} />
                            <Button type="button" variant="outline" className="h-9 text-xs border-blue-200 text-blue-700 hover:bg-blue-50 rounded-xl" asChild disabled={isScanning}>
                                <label htmlFor="id-scan-input" className="cursor-pointer">
                                    {isScanning ? <Loader2 className="h-3 w-3 animate-spin mr-2" /> : <Scan className="h-4 w-4 mr-2" />}
                                    Scan Identity
                                </label>
                            </Button>
                        </div>
                    </div>
                )}
            </div>

            <div className="bg-white rounded-[30px] border border-gray-100 shadow-xl overflow-hidden pb-4">
                <Table>
                    <TableHeader>
                        <TableRow className="bg-gray-50/50">
                            <TableHead className="w-[40%] pl-8 font-black text-black uppercase tracking-widest text-[10px]">Question (Field)</TableHead>
                            <TableHead className="w-[40%] font-black text-black uppercase tracking-widest text-[10px]">Answer (Value)</TableHead>
                            <TableHead className="w-[20%] text-right pr-8 font-black text-black uppercase tracking-widest text-[10px]">Action</TableHead>
                        </TableRow>
                    </TableHeader>
                    <TableBody>
                        {allFields.map((field) => {
                            // Conditional logic for client admin fields
                            if (formData.client_type === 'individual' && field.key === 'business_name') return null;
                            if (formData.client_type === 'corporate' && (field.key === 'first_name' || field.key === 'last_name' || field.key === 'date_of_birth')) return null;

                            const isEditing = editingField === field.key;
                            const value = mode === 'create' ? formData[field.key] : entity[field.key];

                            if (field.type === 'file') {
                                const filePreview = mode === 'create'
                                    ? (formData.driving_license_url instanceof File ? URL.createObjectURL(formData.driving_license_url) : null)
                                    : entity.driving_license_url;

                                return (
                                    <TableRow key={field.key} className="hover:bg-gray-50/30 transition-colors">
                                        <TableCell className="font-bold text-gray-500 pl-8 py-4">{field.label}</TableCell>
                                        <TableCell className="py-4 font-bold text-gray-900">
                                            {filePreview ? (
                                                <div className="space-y-2">
                                                    <a href={filePreview} target="_blank" rel="noreferrer" className="text-blue-600 hover:underline flex items-center gap-2">
                                                        <FileText className="h-4 w-4" /> View Document
                                                    </a>
                                                    <div className="mt-2 rounded-lg border overflow-hidden w-full max-w-xs shadow-sm">
                                                        {/* eslint-disable-next-line @next/next/no-img-element */}
                                                        <img src={filePreview} alt="Document Preview" className="w-full h-auto object-cover" />
                                                    </div>
                                                </div>
                                            ) : (
                                                <span className="text-gray-400 italic">No file uploaded</span>
                                            )}
                                        </TableCell>
                                        <TableCell className="text-right pr-8 py-4">
                                            <div className="flex justify-end">
                                                <label className="cursor-pointer">
                                                    <Input type="file" className="hidden" accept="image/*" onChange={handleFileUpload} />
                                                    <div className="h-8 w-8 rounded-lg hover:bg-blue-50 text-[#00539F] flex items-center justify-center transition-colors">
                                                        {loading ? <Loader2 className="h-4 w-4 animate-spin" /> : <Upload className="h-4 w-4" />}
                                                    </div>
                                                </label>
                                            </div>
                                        </TableCell>
                                    </TableRow>
                                );
                            }

                            return (
                                <TableRow key={field.key} className="hover:bg-gray-50/30 transition-colors">
                                    <TableCell className="font-bold text-gray-500 pl-8 py-4">
                                        {field.label} {field.required && <span className="text-red-500">*</span>}
                                    </TableCell>
                                    <TableCell className="py-2 font-bold text-gray-900">
                                        {mode === 'create' || isEditing ? (
                                            renderInput(field)
                                        ) : (
                                            <span className="text-gray-900">
                                                {field.type === 'date' && value ? new Date(String(value)).toLocaleDateString() : (value || '-')}
                                            </span>
                                        )}
                                    </TableCell>
                                    <TableCell className="text-right pr-8 py-4">
                                        {mode === 'edit' ? (
                                            isEditing ? (
                                                <div className="flex justify-end gap-2">
                                                    <Button size="sm" className="h-8 w-8 p-0 rounded-lg bg-green-600 hover:bg-green-700 text-white" onClick={() => saveField(field.key)} disabled={loading}>
                                                        {loading ? <Loader2 className="h-3 w-3 animate-spin" /> : <Check className="h-3 w-3" />}
                                                    </Button>
                                                    <Button size="sm" variant="ghost" className="h-8 w-8 p-0 rounded-lg hover:bg-red-50 text-red-500" onClick={cancelEditing} disabled={loading}>
                                                        <X className="h-3 w-3" />
                                                    </Button>
                                                </div>
                                            ) : (
                                                <Button size="sm" variant="ghost" className="h-8 w-8 p-0 rounded-lg hover:bg-blue-50 text-[#00539F]" onClick={() => startEditing(field.key, value)}>
                                                    <Pencil className="h-3 w-3" />
                                                </Button>
                                            )
                                        ) : null}
                                    </TableCell>
                                </TableRow>
                            );
                        })}
                    </TableBody>
                </Table>

                {mode === 'create' && (
                    <div className="p-8 flex justify-end gap-4">
                        <Button variant="ghost" onClick={onBack} className="rounded-xl font-bold h-12 px-8">Cancel</Button>
                        <Button
                            onClick={saveNewEntity}
                            disabled={loading}
                            className="bg-[#00539F] hover:bg-[#00438a] text-white rounded-xl px-12 h-12 text-lg font-bold shadow-lg shadow-blue-900/10"
                        >
                            {loading ? <Loader2 className="mr-2 h-5 w-5 animate-spin" /> : null}
                            Save New {type === 'client' ? 'Client' : 'Driver'}
                        </Button>
                    </div>
                )}
            </div>
        </div>
    );
}
