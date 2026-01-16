'use client';

import React, { useState } from 'react';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Badge } from '@/components/ui/badge';
import { Label } from '@/components/ui/label';
import { Upload, X, FileText, Loader2 } from 'lucide-react';
import {
    Select,
    SelectContent,
    SelectItem,
    SelectTrigger,
    SelectValue,
} from '@/components/ui/select';

export const DOCUMENT_LABELS = [
    'Quote', 'Policy', 'Receipt', 'Payslip',
    'Document', 'Ads', 'Driving Licence', 'Car Papers', 'Photo'
];

interface DocumentUploadProps {
    onUpload: (file: File, label: string) => Promise<void>;
}

export function DocumentUpload({ onUpload }: DocumentUploadProps) {
    const [file, setFile] = useState<File | null>(null);
    const [label, setLabel] = useState<string>('Document');
    const [isUploading, setIsUploading] = useState(false);
    const isMounted = React.useRef(false);

    React.useEffect(() => {
        isMounted.current = true;
        return () => {
            isMounted.current = false;
        };
    }, []);

    const handleFileChange = (e: React.ChangeEvent<HTMLInputElement>) => {
        if (e.target.files && e.target.files[0]) {
            setFile(e.target.files[0]);
        }
    };

    const handleUpload = async () => {
        if (file && label) {
            try {
                // If unmounted, don't start
                if (!isMounted.current) return;

                setIsUploading(true);
                await onUpload(file, label);

                // Only clear state if component is still mounted
                if (isMounted.current) {
                    setFile(null);
                    setLabel('Document');
                }
            } catch (error) {
                console.error("Upload failed in component", error);
                // Keep file selected so user can retry
            } finally {
                if (isMounted.current) {
                    setIsUploading(false);
                }
            }
        }
    };

    return (
        <div className="space-y-4 p-4 border rounded-lg bg-card">
            <div className="space-y-2">
                <Label>Select Document</Label>
                {!file ? (
                    <div className="flex items-center justify-center w-full">
                        <div
                            onClick={() => document.getElementById('file-upload-input')?.click()}
                            className={`flex flex-col items-center justify-center w-full h-32 border-2 border-dashed rounded-lg cursor-pointer hover:bg-muted/50 transition ${isUploading ? 'opacity-50 cursor-not-allowed' : ''}`}
                        >
                            <div className="flex flex-col items-center justify-center pt-5 pb-6">
                                <Upload className="w-8 h-8 mb-2 text-muted-foreground" />
                                <p className="text-sm text-muted-foreground">Click to upload (PDF, DOCS, MM)</p>
                            </div>
                            <input
                                id="file-upload-input"
                                type="file"
                                className="hidden"
                                onChange={handleFileChange}
                                accept=".pdf,.doc,.docx,.xls,.xlsx,.csv,.png,.jpg,.jpeg,.xml,.md,.mp4"
                                disabled={isUploading}
                            />
                        </div>
                    </div>
                ) : (
                    <div className="flex items-center justify-between p-3 border rounded-md bg-muted/50">
                        <div className="flex items-center gap-2">
                            <FileText className="h-5 w-5 text-blue-500" />
                            <span className="text-sm font-medium truncate max-w-[200px]">{file.name}</span>
                        </div>
                        <Button variant="ghost" size="icon" onClick={() => setFile(null)} disabled={isUploading}>
                            <X className="h-4 w-4" />
                        </Button>
                    </div>
                )}
            </div>

            <div className="space-y-2">
                <Label>Label</Label>
                <Select value={label} onValueChange={setLabel} disabled={isUploading}>
                    <SelectTrigger>
                        <SelectValue placeholder="Select Label" />
                    </SelectTrigger>
                    <SelectContent>
                        {DOCUMENT_LABELS.map((l) => (
                            <SelectItem key={l} value={l}>{l}</SelectItem>
                        ))}
                    </SelectContent>
                </Select>
            </div>

            <Button className="w-full" disabled={!file || isUploading} onClick={handleUpload}>
                {isUploading ? (
                    <>
                        <Loader2 className="mr-2 h-4 w-4 animate-spin" />
                        Uploading...
                    </>
                ) : (
                    'Upload Document'
                )}
            </Button>
        </div>
    );
}
