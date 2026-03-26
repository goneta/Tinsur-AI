'use client';

import React, { useState } from 'react';
import {
    Dialog,
    DialogContent,
    DialogHeader,
    DialogTitle,
    DialogDescription,
} from '@/components/ui/dialog';
import { Button } from '@/components/ui/button';
import { useToast } from '@/components/ui/use-toast';
import { SharingSettings, SharingConfig } from '@/components/collaboration/sharing-settings';
import { RecipientSelector } from '@/components/collaboration/recipient-selector';
import { Share2, Globe, Lock } from 'lucide-react';

interface PortalShareModalProps {
    open: boolean;
    onOpenChange: (open: boolean) => void;
    documentName: string;
}

export function PortalShareModal({ open, onOpenChange, documentName }: PortalShareModalProps) {
    const { toast } = useToast();
    const [config, setConfig] = useState<SharingConfig>({
        visibility: 'PRIVATE',
        scope: 'C2C',
        isShareable: false,
    });
    const [selectedRecipients, setSelectedRecipients] = useState<string[]>([]);
    const [isLoading, setIsLoading] = useState(false);

    const handleConfigChange = (newConfig: SharingConfig) => {
        if (newConfig.scope !== config.scope) {
            setSelectedRecipients([]);
        }
        setConfig(newConfig);
    };

    const handleSave = async () => {
        setIsLoading(true);
        // Simulate API call
        setTimeout(() => {
            setIsLoading(false);
            toast({
                title: 'Settings Saved',
                description: `Share settings for ${documentName} have been updated.`,
            });
            onOpenChange(false);
        }, 1200);
    };

    return (
        <Dialog open={open} onOpenChange={onOpenChange}>
            <DialogContent className="max-w-[90vw] md:max-w-6xl p-0 overflow-hidden h-[85vh] flex flex-col gap-0 border-none rounded-3xl bg-white shadow-2xl">
                {/* Header */}
                <div className="p-10 border-b border-gray-100 bg-white">
                    <DialogTitle className="text-xl font-black text-gray-900 tracking-tight">
                        Share Settings: {documentName}
                    </DialogTitle>
                    <DialogDescription className="text-gray-400 text-base mt-2 font-bold">
                        Configure visibility and collaborative permissions.
                    </DialogDescription>
                </div>

                <div className="flex-1 flex overflow-hidden flex-col md:row">
                    <div className="flex-1 flex overflow-hidden md:flex-row flex-col">
                        {/* Left Side: Settings */}
                        <div className="w-full md:w-[45%] bg-gray-50/50 border-r border-gray-100 p-10 overflow-y-auto">
                            <SharingSettings
                                initialConfig={config}
                                onChange={handleConfigChange}
                            />

                            <div className="mt-12 flex gap-4">
                                <Button
                                    variant="outline"
                                    onClick={() => onOpenChange(false)}
                                    className="px-10 py-7 rounded-2xl font-black text-base border-gray-200 hover:bg-white transition-all text-gray-400"
                                >
                                    Cancel
                                </Button>
                                <Button
                                    onClick={handleSave}
                                    disabled={isLoading}
                                    className="flex-1 px-10 py-7 rounded-2xl font-black text-base bg-black text-white hover:bg-zinc-800 transition-all shadow-lg"
                                >
                                    {isLoading ? 'Saving...' : 'Save Changes'}
                                </Button>
                            </div>
                        </div>

                        {/* Right Side: Recipients */}
                        <div className="w-full md:w-[55%] bg-white p-10 overflow-hidden flex flex-col">
                            {config.visibility === 'PRIVATE' ? (
                                <RecipientSelector
                                    scope={config.scope || 'C2C'}
                                    selectedIds={selectedRecipients}
                                    onSelectionChange={setSelectedRecipients}
                                />
                            ) : (
                                <div className="flex flex-col items-center justify-center h-full text-center space-y-6">
                                    <div className="p-8 bg-blue-50 rounded-full">
                                        <Globe className="h-16 w-16 text-blue-500" />
                                    </div>
                                    <div className="max-w-sm">
                                        <h4 className="text-lg font-black text-gray-900">Public visibility</h4>
                                        <p className="text-gray-500 text-base mt-2 font-medium">
                                            This document will be visible to all users. Specific recipients are not required in public mode.
                                        </p>
                                    </div>
                                </div>
                            )}
                        </div>
                    </div>
                </div>
            </DialogContent>
        </Dialog>
    );
}
