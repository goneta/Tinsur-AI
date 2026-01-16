'use client';

import { useState } from 'react';
import { Card, CardContent, CardDescription, CardFooter, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select';
import { Label } from '@/components/ui/label';
import { Checkbox } from '@/components/ui/checkbox';
import { Download, FileDown, FileJson, FileText, FileCode, Database } from 'lucide-react';
import { toast } from '@/components/ui/use-toast';

const SCHEMAS = {
    clients: ['first_name', 'last_name', 'email', 'phone', 'date_of_birth', 'address', 'city', 'kyc_status', 'status'],
    employees: ['first_name', 'last_name', 'email', 'phone', 'role', 'job_title', 'department'],
    policies: ['policy_number', 'premium_amount', 'premium_frequency', 'start_date', 'end_date', 'status']
};

export function ExportWizard() {
    const [dataType, setDataType] = useState<string>('clients');
    const [format, setFormat] = useState<string>('csv');
    const [selectedFields, setSelectedFields] = useState<string[]>(SCHEMAS['clients']);
    const [isExporting, setIsExporting] = useState(false);

    const toggleField = (field: string) => {
        setSelectedFields(prev =>
            prev.includes(field) ? prev.filter(f => f !== field) : [...prev, field]
        );
    };

    const handleDataTypeChange = (val: string) => {
        setDataType(val);
        setSelectedFields(SCHEMAS[val as keyof typeof SCHEMAS]);
    };

    const handleExport = async () => {
        setIsExporting(true);
        try {
            // In a real app, this would be a direct download link or a blob fetch
            const fieldsParam = selectedFields.join(',');
            const url = `${process.env.NEXT_PUBLIC_API_URL}/api/v1/import-export/export?data_type=${dataType}&format=${format}&fields=${fieldsParam}`;

            // Simulating download logic
            console.log("Exporting to:", url);

            setTimeout(() => {
                setIsExporting(false);
                toast({
                    title: "Export Started",
                    description: `Your ${dataType} export in ${format.toUpperCase()} format is being generated.`,
                });
                // In actual implementation: window.location.href = url;
            }, 1000);
        } catch (error) {
            setIsExporting(false);
            toast({
                title: "Error",
                description: "Failed to generate export file",
                variant: "destructive"
            });
        }
    };

    const getFormatIcon = (f: string) => {
        switch (f) {
            case 'json': return <FileJson className="h-4 w-4" />;
            case 'csv': return <FileText className="h-4 w-4" />;
            case 'xlsx': return <FileSpreadsheet className="h-4 w-4" />;
            case 'xml': return <FileCode className="h-4 w-4" />;
            default: return <Download className="h-4 w-4" />;
        }
    };

    return (
        <Card>
            <CardHeader>
                <CardTitle>Configure Export</CardTitle>
                <CardDescription>Select the data and format you wish to export</CardDescription>
            </CardHeader>
            <CardContent className="space-y-6">
                <div className="grid grid-cols-2 gap-6">
                    <div className="space-y-2">
                        <Label>Data Source</Label>
                        <Select value={dataType} onValueChange={handleDataTypeChange}>
                            <SelectTrigger>
                                <SelectValue />
                            </SelectTrigger>
                            <SelectContent>
                                <SelectItem value="clients">Clients</SelectItem>
                                <SelectItem value="employees">Employees</SelectItem>
                                <SelectItem value="policies">Policies</SelectItem>
                            </SelectContent>
                        </Select>
                    </div>
                    <div className="space-y-2">
                        <Label>Export Format</Label>
                        <Select value={format} onValueChange={setFormat}>
                            <SelectTrigger>
                                <SelectValue />
                            </SelectTrigger>
                            <SelectContent>
                                <SelectItem value="csv">CSV (Comma Separated)</SelectItem>
                                <SelectItem value="json">JSON (Data Interchange)</SelectItem>
                                <SelectItem value="xlsx">Excel (XLSX)</SelectItem>
                                <SelectItem value="xml">XML</SelectItem>
                                <SelectItem value="pdf">PDF Report</SelectItem>
                                <SelectItem value="md">Markdown Table</SelectItem>
                            </SelectContent>
                        </Select>
                    </div>
                </div>

                <div className="space-y-4">
                    <Label>Select Fields to Include</Label>
                    <div className="grid grid-cols-3 gap-2 border rounded-lg p-4 bg-muted/30">
                        {SCHEMAS[dataType as keyof typeof SCHEMAS].map(field => (
                            <div key={field} className="flex items-center space-x-2">
                                <Checkbox
                                    id={`field-${field}`}
                                    checked={selectedFields.includes(field)}
                                    onCheckedChange={() => toggleField(field)}
                                />
                                <Label htmlFor={`field-${field}`} className="text-sm font-normal cursor-pointer capitalize">
                                    {field.replace('_', ' ')}
                                </Label>
                            </div>
                        ))}
                    </div>
                    <div className="flex gap-2">
                        <Button variant="outline" size="sm" onClick={() => setSelectedFields(SCHEMAS[dataType as keyof typeof SCHEMAS])}>Select All</Button>
                        <Button variant="outline" size="sm" onClick={() => setSelectedFields([])}>Deselect All</Button>
                    </div>
                </div>
            </CardContent>
            <CardFooter className="bg-muted/30 pt-6">
                <Button className="w-full" onClick={handleExport} disabled={isExporting || selectedFields.length === 0}>
                    {isExporting ? "Generating..." : "Download Export File"}
                    {!isExporting && <Download className="ml-2 h-4 w-4" />}
                </Button>
            </CardFooter>
        </Card>
    );
}

function FileSpreadsheet(props: any) {
    return (
        <svg
            {...props}
            xmlns="http://www.w3.org/2000/svg"
            width="24"
            height="24"
            viewBox="0 0 24 24"
            fill="none"
            stroke="currentColor"
            strokeWidth="2"
            strokeLinecap="round"
            strokeLinejoin="round"
        >
            <path d="M15 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V7Z" />
            <path d="M14 2v4a2 2 0 0 0 2 2h4" />
            <path d="M8 13h2" />
            <path d="M14 13h2" />
            <path d="M8 17h2" />
            <path d="M14 17h2" />
        </svg>
    )
}
