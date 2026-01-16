'use client';

import { useState } from 'react';
import { Card, CardContent, CardDescription, CardFooter, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { Checkbox } from '@/components/ui/checkbox';
import { Upload, CheckCircle2, ChevronRight, ChevronLeft, AlertCircle, FileText, Database } from 'lucide-react';
import { toast } from '@/components/ui/use-toast';
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from '@/components/ui/table';
import { Badge } from '@/components/ui/badge';
import { Progress } from '@/components/ui/progress';

type Step = 'upload' | 'mapping' | 'validation' | 'result';

const SCHEMAS = {
    clients: ['first_name', 'last_name', 'business_name', 'email', 'phone', 'date_of_birth', 'address', 'city', 'occupation'],
    employees: ['first_name', 'last_name', 'email', 'phone', 'job_title', 'department', 'base_salary'],
    policies: ['policy_number', 'premium_amount', 'start_date', 'end_date', 'status']
};

export function ImportWizard() {
    const [step, setStep] = useState<Step>('upload');
    const [dataType, setDataType] = useState<string>('clients');
    const [file, setFile] = useState<File | null>(null);
    const [parsedData, setParsedData] = useState<any>(null);
    const [mapping, setMapping] = useState<Record<string, string>>({});
    const [duplicates, setDuplicates] = useState<any[]>([]);
    const [isLoading, setIsLoading] = useState(false);
    const [importResult, setImportResult] = useState<any>(null);

    const handleFileUpload = async (e: React.ChangeEvent<HTMLInputElement>) => {
        const uploadedFile = e.target.files?.[0];
        if (!uploadedFile) return;
        setFile(uploadedFile);
    };

    const proceedToMapping = async () => {
        if (!file) {
            toast({ title: "Error", description: "Please select a file first", variant: "destructive" });
            return;
        }

        setIsLoading(true);
        const formData = new FormData();
        formData.append('file', file);
        formData.append('data_type', dataType);

        try {
            // In a real app, this calls the backend /upload endpoint
            // For now, we simulate the response
            console.log("Uploading file...");

            // Simulating API call
            setTimeout(() => {
                const mockParsed = {
                    all_fields: ['Name', 'Surname', 'Mail', 'Phone', 'DOB', 'Home Address'],
                    records: [
                        { 'Name': 'John', 'Surname': 'Doe', 'Mail': 'john@example.com', 'Phone': '123456789', 'DOB': '1990-01-01', 'Home Address': 'Main St 1' }
                    ]
                };
                setParsedData(mockParsed);

                // Initial auto-mapping
                const initialMapping: Record<string, string> = {};
                const targetFields = SCHEMAS[dataType as keyof typeof SCHEMAS];
                mockParsed.all_fields.forEach(f => {
                    const match = targetFields.find(tf =>
                        tf.toLowerCase().replace('_', '') === f.toLowerCase().replace(' ', '')
                    );
                    if (match) initialMapping[f] = match;
                });
                setMapping(initialMapping);

                setIsLoading(false);
                setStep('mapping');
            }, 1000);

        } catch (error) {
            setIsLoading(false);
            toast({ title: "Error", description: "Failed to upload file", variant: "destructive" });
        }
    };

    const proceedToValidation = async () => {
        setIsLoading(true);
        try {
            // Simulating /validate call
            setTimeout(() => {
                setDuplicates([
                    {
                        imported: { 'Name': 'John', 'Surname': 'Doe' },
                        existing: { name: 'John Doe', email: 'john@example.com' },
                        matching_fields: ['first_name', 'last_name']
                    }
                ]);
                setIsLoading(false);
                setStep('validation');
            }, 1000);
        } catch (error) {
            setIsLoading(false);
        }
    };

    const executeImport = async () => {
        setIsLoading(true);
        try {
            // Simulating /execute call
            setTimeout(() => {
                setImportResult({ count: 42 });
                setIsLoading(false);
                setStep('result');
            }, 1500);
        } catch (error) {
            setIsLoading(false);
        }
    };

    return (
        <div className="space-y-6">
            <div className="flex items-center justify-between mb-8">
                <div className="flex items-center gap-4">
                    <div className={step === 'upload' ? "text-primary font-bold" : "text-muted-foreground"}>1. Upload</div>
                    <ChevronRight className="h-4 w-4 text-muted-foreground" />
                    <div className={step === 'mapping' ? "text-primary font-bold" : "text-muted-foreground"}>2. Mapping</div>
                    <ChevronRight className="h-4 w-4 text-muted-foreground" />
                    <div className={step === 'validation' ? "text-primary font-bold" : "text-muted-foreground"}>3. Validation</div>
                    <ChevronRight className="h-4 w-4 text-muted-foreground" />
                    <div className={step === 'result' ? "text-primary font-bold" : "text-muted-foreground"}>4. Done</div>
                </div>
            </div>

            {step === 'upload' && (
                <Card>
                    <CardHeader>
                        <CardTitle>Upload Data File</CardTitle>
                        <CardDescription>Select the type of data and upload your file (CSV, JSON, XLS, PDF, XML, Markdown)</CardDescription>
                    </CardHeader>
                    <CardContent className="space-y-4">
                        <div className="space-y-2">
                            <Label>Data Type</Label>
                            <Select value={dataType} onValueChange={setDataType}>
                                <SelectTrigger>
                                    <SelectValue placeholder="Select data type" />
                                </SelectTrigger>
                                <SelectContent>
                                    <SelectItem value="clients">Clients</SelectItem>
                                    <SelectItem value="employees">Employees</SelectItem>
                                    <SelectItem value="policies">Policies</SelectItem>
                                </SelectContent>
                            </Select>
                        </div>
                        <div
                            className="border-2 border-dashed rounded-lg p-12 flex flex-col items-center justify-center gap-4 cursor-pointer hover:bg-muted/50 transition-colors"
                            onClick={() => document.getElementById('file-upload')?.click()}
                        >
                            <Upload className="h-10 w-10 text-muted-foreground" />
                            <div className="text-center">
                                <p className="font-medium">{file ? file.name : "Click to upload or drag and drop"}</p>
                                <p className="text-sm text-muted-foreground">Supports CSV, JSON, XLS, PDF, XML, MD</p>
                            </div>
                            <Input
                                id="file-upload"
                                type="file"
                                className="hidden"
                                onChange={handleFileUpload}
                                accept=".csv,.json,.xlsx,.xls,.pdf,.xml,.md"
                            />
                        </div>
                    </CardContent>
                    <CardFooter>
                        <Button onClick={proceedToMapping} disabled={!file || isLoading}>
                            {isLoading ? "Processing..." : "Next: Map Fields"}
                        </Button>
                    </CardFooter>
                </Card>
            )}

            {step === 'mapping' && (
                <Card>
                    <CardHeader>
                        <CardTitle>Map Imported Fields</CardTitle>
                        <CardDescription>Align your file columns with Tinsur.AI application fields</CardDescription>
                    </CardHeader>
                    <CardContent>
                        <Table>
                            <TableHeader>
                                <TableRow>
                                    <TableHead>Imported Column</TableHead>
                                    <TableHead>Tinsur.AI Field</TableHead>
                                </TableRow>
                            </TableHeader>
                            <TableBody>
                                {parsedData?.all_fields.map((field: string) => (
                                    <TableRow key={field}>
                                        <TableCell className="font-medium">{field}</TableCell>
                                        <TableCell>
                                            <Select
                                                value={mapping[field] || 'skip'}
                                                onValueChange={(val) => setMapping(prev => ({ ...prev, [field]: val }))}
                                            >
                                                <SelectTrigger className="w-[200px]">
                                                    <SelectValue />
                                                </SelectTrigger>
                                                <SelectContent>
                                                    <SelectItem value="skip">-- Skip --</SelectItem>
                                                    {SCHEMAS[dataType as keyof typeof SCHEMAS].map(f => (
                                                        <SelectItem key={f} value={f}>{f.replace('_', ' ')}</SelectItem>
                                                    ))}
                                                </SelectContent>
                                            </Select>
                                        </TableCell>
                                    </TableRow>
                                ))}
                            </TableBody>
                        </Table>
                    </CardContent>
                    <CardFooter className="flex justify-between">
                        <Button variant="outline" onClick={() => setStep('upload')}>Back</Button>
                        <Button onClick={proceedToValidation}>Next: Validate Data</Button>
                    </CardFooter>
                </Card>
            )}

            {step === 'validation' && (
                <Card>
                    <CardHeader>
                        <CardTitle>Data Validation & Duplicates</CardTitle>
                        <CardDescription>We found {duplicates.length} potential duplicates in your data</CardDescription>
                    </CardHeader>
                    <CardContent className="space-y-4">
                        {duplicates.length > 0 ? (
                            <div className="border rounded-lg overflow-hidden">
                                <Table>
                                    <TableHeader>
                                        <TableRow>
                                            <TableHead>Imported Record</TableHead>
                                            <TableHead>Existing Match</TableHead>
                                            <TableHead>Matched On</TableHead>
                                            <TableHead>Action</TableHead>
                                        </TableRow>
                                    </TableHeader>
                                    <TableBody>
                                        {duplicates.map((dup, i) => (
                                            <TableRow key={i}>
                                                <TableCell>
                                                    {Object.entries(dup.imported).map(([k, v]: any) => (
                                                        <div key={k} className="text-xs">
                                                            <span className="font-semibold">{k}:</span> {v}
                                                        </div>
                                                    ))}
                                                </TableCell>
                                                <TableCell>
                                                    <div className="text-xs font-semibold">{dup.existing.name}</div>
                                                    <div className="text-xs text-muted-foreground">{dup.existing.email}</div>
                                                </TableCell>
                                                <TableCell>
                                                    {dup.matching_fields.map((f: string) => (
                                                        <Badge key={f} variant="outline" className="mr-1 bg-amber-50 text-amber-700 border-amber-200">
                                                            {f.replace('_', ' ')}
                                                        </Badge>
                                                    ))}
                                                </TableCell>
                                                <TableCell>
                                                    <div className="flex gap-2">
                                                        <Button size="sm" variant="outline">Skip</Button>
                                                        <Button size="sm">Update</Button>
                                                    </div>
                                                </TableCell>
                                            </TableRow>
                                        ))}
                                    </TableBody>
                                </Table>
                            </div>
                        ) : (
                            <div className="flex flex-col items-center justify-center py-8 text-muted-foreground">
                                <CheckCircle2 className="h-12 w-12 text-green-500 mb-4" />
                                <p>No duplicates found! Your data is clean.</p>
                            </div>
                        )}
                    </CardContent>
                    <CardFooter className="flex justify-between">
                        <Button variant="outline" onClick={() => setStep('mapping')}>Back</Button>
                        <Button onClick={executeImport} disabled={isLoading}>
                            {isLoading ? "Importing..." : "Finalize Import"}
                        </Button>
                    </CardFooter>
                </Card>
            )}

            {step === 'result' && (
                <Card className="text-center py-12">
                    <CardContent className="space-y-4">
                        <div className="mx-auto w-16 h-16 bg-green-100 rounded-full flex items-center justify-center mb-6">
                            <CheckCircle2 className="h-10 w-10 text-green-600" />
                        </div>
                        <CardTitle className="text-2xl">Import Successful!</CardTitle>
                        <CardDescription className="text-lg">
                            We've successfully imported {importResult?.count} {dataType} into your database.
                        </CardDescription>
                        <div className="pt-8">
                            <Button onClick={() => setStep('upload')}>Done</Button>
                        </div>
                    </CardContent>
                </Card>
            )}
        </div>
    );
}
