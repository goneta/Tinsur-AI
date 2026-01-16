'use client';

import React, { useState, useEffect } from 'react';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import {
    Table,
    TableBody,
    TableCell,
    TableHead,
    TableHeader,
    TableRow,
} from "@/components/ui/table";
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select";
import { Loader2, Pencil, Check, X, ArrowLeft, Upload, FileText, Camera, Scan } from "lucide-react";
import { useToast } from "@/components/ui/use-toast";
import { VEHICLE_FIELDS, FieldDefinition } from '@/config/field-definitions';
import { clientApi } from '@/lib/client-api';
import { formatApiError } from '@/lib/api';

interface VehicleDetailsTableProps {
    clientId: string;
    mode: 'create' | 'edit';
    vehicle?: any;
    onUpdate: () => void;
    onBack: () => void;
}

export function VehicleDetailsTable({ clientId, mode, vehicle, onUpdate, onBack }: VehicleDetailsTableProps) {
    const { toast } = useToast();
    const [loading, setLoading] = useState(false);
    const [isScanning, setIsScanning] = useState(false);
    const [editingField, setEditingField] = useState<string | null>(null);
    const [tempValue, setTempValue] = useState<any>(null);
    const [formData, setFormData] = useState<any>(vehicle || {});
    const [uploading, setUploading] = useState(false);

    useEffect(() => {
        if (vehicle) {
            setFormData(vehicle);
        }
    }, [vehicle]);

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

    // SCAN FUNCTION
    const handleScan = async (e: React.ChangeEvent<HTMLInputElement>) => {
        const file = e.target.files?.[0];
        if (!file) return;

        setIsScanning(true);
        try {
            // Using 'car_papers' or generic 'vehicle_registration' doc type if supported by backend
            const result = await clientApi.uploadAndParseKycDocument(file, 'car_papers');

            // Map result fields to our schema
            if (result.registration_number || result.registration) handleInputChange('vehicle_registration', result.registration_number || result.registration);
            if (result.make || result.vehicle_make) handleInputChange('vehicle_make', result.make || result.vehicle_make);
            if (result.model || result.vehicle_model) handleInputChange('vehicle_model', result.model || result.vehicle_model);
            if (result.year || result.date_of_first_registration) {
                // Try to extract year if it's a date string
                let year = result.year;
                if (!year && result.date_of_first_registration) {
                    year = new Date(result.date_of_first_registration).getFullYear();
                }
                if (year) handleInputChange('vehicle_year', Number(year));
            }
            if (result.color || result.colour) handleInputChange('vehicle_color', result.color || result.colour);
            if (result.fuel_type) handleInputChange('fuel_type', result.fuel_type.toLowerCase());

            toast({ title: "Scan Complete", description: "Vehicle details extracted successfully." });
        } catch (err: any) {
            toast({ title: "Scan Failed", description: formatApiError(err.response?.data?.detail) || "AI parsing failed", variant: "destructive" });
        } finally {
            setIsScanning(false);
        }
    };

    // EDIT MODE: Save single field
    const saveField = async (field: string) => {
        if (!vehicle?.id) return;
        setLoading(true);
        try {
            // Check if field is actually distinct from existing
            const payload = { [field]: tempValue };
            await clientApi.updateVehicle(clientId, vehicle.id, payload);
            toast({ title: "Success", description: "Vehicle updated successfully." });
            onUpdate();
            setEditingField(null);
        } catch (error: any) {
            const msg = formatApiError(error.response?.data?.detail) || "Failed to update vehicle";
            toast({ title: "Error", description: msg, variant: "destructive" });
        } finally {
            setLoading(false);
        }
    };

    // CREATE MODE: Save entire vehicle
    const saveNewVehicle = async () => {
        if (!formData.vehicle_registration || !formData.vehicle_make || !formData.vehicle_model) {
            toast({ title: "Error", description: "Registration, Make, and Model are required.", variant: "destructive" });
            return;
        }

        setLoading(true);
        try {
            // Remove file object from JSON payload
            const payload = { ...formData };
            if (payload.vehicle_image_url instanceof File) delete payload.vehicle_image_url;

            const newVehicle = await clientApi.createVehicle(clientId, payload);

            // Upload image if present
            if (formData.vehicle_image_url instanceof File) {
                await clientApi.uploadVehicleImage(clientId, newVehicle.id, formData.vehicle_image_url);
            }

            toast({ title: "Success", description: "Vehicle added successfully." });
            onUpdate();
        } catch (error: any) {
            const msg = formatApiError(error.response?.data?.detail) || "Failed to add vehicle";
            toast({ title: "Error", description: msg, variant: "destructive" });
        } finally {
            setLoading(false);
        }
    };

    const renderFileInput = (field: FieldDefinition, currentValue: string | null) => {
        const handleFileChange = async (e: React.ChangeEvent<HTMLInputElement>) => {
            const file = e.target.files?.[0];
            if (!file) return;

            if (mode === 'create') {
                handleInputChange(field.key, file);
                return;
            }

            // Edit mode direct upload
            if (!vehicle?.id) return;

            setUploading(true);
            try {
                const result = await clientApi.uploadVehicleImage(clientId, vehicle.id, file);
                toast({ title: "Success", description: "Vehicle photo uploaded successfully." });
                onUpdate();
                // Update local state to show new image immediately
                setFormData((prev: any) => ({ ...prev, vehicle_image_url: result.vehicle_image_url }));
            } catch (error: any) {
                toast({ title: "Upload Failed", description: formatApiError(error) || "Could not upload image", variant: "destructive" });
            } finally {
                setUploading(false);
            }
        };

        const displayUrl = mode === 'create'
            ? ((currentValue as any) instanceof File ? URL.createObjectURL(currentValue as any) : null)
            : currentValue;

        return (
            <div className="flex items-center gap-4">
                {displayUrl ? (
                    <div className="relative group">
                        <div className="h-16 w-16 rounded-xl overflow-hidden border border-gray-100 bg-gray-50 flex-shrink-0">
                            {/* eslint-disable-next-line @next/next/no-img-element */}
                            <img src={displayUrl} alt="VehiclePhoto" className="w-full h-full object-cover" />
                        </div>
                        <label className="absolute inset-0 flex items-center justify-center bg-black/40 rounded-xl opacity-0 group-hover:opacity-100 transition-opacity cursor-pointer">
                            <Camera className="text-white h-4 w-4" />
                            <input type="file" className="hidden" accept="image/*" onChange={handleFileChange} disabled={uploading} />
                        </label>
                    </div>
                ) : (
                    <Button variant="outline" className="h-10 px-4 rounded-xl border-dashed border-2 border-gray-200 hover:border-[#00539F] hover:bg-blue-50/50 text-gray-500 font-bold flex items-center gap-2 group transition-all" asChild>
                        <label className="cursor-pointer">
                            {uploading ? <Loader2 className="h-4 w-4 animate-spin" /> : <Camera className="h-4 w-4 group-hover:text-[#00539F]" />}
                            <span className="group-hover:text-[#00539F]">{uploading ? 'Uploading...' : 'Upload Photo'}</span>
                            <input type="file" className="hidden" accept="image/*" onChange={handleFileChange} disabled={uploading} />
                        </label>
                    </Button>
                )}
            </div>
        );
    };

    const renderInput = (field: FieldDefinition) => {
        const value = mode === 'create' ? formData[field.key] : (editingField === field.key ? tempValue : formData[field.key]);
        const onChange = (val: any) => {
            if (mode === 'create') handleInputChange(field.key, val);
            else setTempValue(val);
        };

        if (field.type === 'file') {
            const fileVal = mode === 'create' ? formData[field.key] : formData[field.key];
            return renderFileInput(field, fileVal);
        }

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
                        {mode === 'create' ? 'Add New Vehicle' : `Vehicle Details: ${formData.vehicle_make || ''} ${formData.vehicle_model || ''}`}
                    </h2>
                </div>
                {mode === 'create' && (
                    <div className="flex gap-2">
                        <div className="relative">
                            <Input type="file" className="hidden" id="car-scan-input" accept="image/*" onChange={handleScan} disabled={isScanning} />
                            <Button type="button" variant="outline" className="h-9 text-xs border-blue-200 text-blue-700 hover:bg-blue-50 rounded-xl" asChild disabled={isScanning}>
                                <label htmlFor="car-scan-input" className="cursor-pointer">
                                    {isScanning ? <Loader2 className="h-3 w-3 animate-spin mr-2" /> : <Scan className="h-4 w-4 mr-2" />}
                                    Scan Car Papers
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
                            <TableHead className="w-[40%] font-black text-black uppercase tracking-widest text-[10px] pl-8">Question (Field)</TableHead>
                            <TableHead className="w-[40%] font-black text-black uppercase tracking-widest text-[10px]">Answer (Value)</TableHead>
                            <TableHead className="w-[20%] text-right font-black text-black uppercase tracking-widest text-[10px] pr-8">Action</TableHead>
                        </TableRow>
                    </TableHeader>
                    <TableBody>
                        {VEHICLE_FIELDS.map((field) => {
                            const isEditing = editingField === field.key;
                            const value = mode === 'create' ? formData[field.key] : formData[field.key];

                            if (field.type === 'file') {
                                return (
                                    <TableRow key={field.key} className="hover:bg-gray-50/30 transition-colors">
                                        <TableCell className="font-bold text-gray-500 pl-8 py-4">{field.label}</TableCell>
                                        <TableCell className="py-2 font-bold text-gray-900">
                                            {renderFileInput(field, value)}
                                        </TableCell>
                                        <TableCell className="text-right pr-8 py-4"></TableCell>
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
                                            <span className="text-gray-900">{value || '-'}</span>
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
                            onClick={saveNewVehicle}
                            disabled={loading}
                            className="bg-[#00539F] hover:bg-[#00438a] text-white rounded-xl px-12 h-12 text-lg font-bold shadow-lg shadow-blue-900/10"
                        >
                            {loading ? <Loader2 className="mr-2 h-5 w-5 animate-spin" /> : null}
                            Save New Vehicle
                        </Button>
                    </div>
                )}
            </div>
        </div>
    );
}
