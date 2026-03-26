"use client";

import React, { useState } from 'react';
import { Button } from '@/components/ui/button';
import {
    Dialog,
    DialogContent,
    DialogDescription,
    DialogFooter,
    DialogHeader,
    DialogTitle,
    DialogTrigger,
} from "@/components/ui/dialog";
import { SharingSettings, SharingConfig, SharingScope } from './sharing-settings';
import { RecipientSelector } from './recipient-selector';
import { X, Save } from 'lucide-react';
import { useToast } from "@/components/ui/use-toast";
import { api } from '@/lib/api';

// Reusing types from SharingSettings
// Assuming the parent component will handle the actual "Save" API call or we do it here.
// For now, let's assume we pass the final config back to parent.

interface ShareModalProps {
    open: boolean;
    onOpenChange: (open: boolean) => void;
    documentName?: string;
    documentId?: string; // Optional: If we want to save directly
    initialConfig?: Partial<SharingConfig>;
    onSave?: (config: SharingConfig, recipientIds: string[]) => void;
}

export function ShareModal({
    open,
    onOpenChange,
    documentName = "Document",
    documentId,
    initialConfig,
    onSave
}: ShareModalProps) {
    const { toast } = useToast();
    const [config, setConfig] = useState<SharingConfig>({
        visibility: 'PRIVATE', // Default
        scope: 'B2B',
        isShareable: false,
        reshareRule: 'C',
        ...initialConfig
    });
    const [selectedRecipients, setSelectedRecipients] = useState<string[]>([]);
    const [saving, setSaving] = useState(false);

    const handleConfigChange = (newConfig: SharingConfig) => {
        // When scope changes, we might want to clear recipients or warn?
        // For now, we clear recipients if scope changed significantly to avoid invalid IDs.
        if (newConfig.scope !== config.scope) {
            setSelectedRecipients([]);
        }
        setConfig(newConfig);
    };

    const handleSave = async () => {
        setSaving(true);
        try {
            if (onSave) {
                // Determine effective config
                // If Visibility is Public, recipients might be irrelevant or ignored?
                // Requirements say "The recipient list must update in real time based on the selected sharing option".
                // If Public, maybe no recipients are needed.
                await onSave(config, selectedRecipients);
            } else if (documentId) {
                // Fallback: Perform API call directly if onSave not provided
                const payload = {
                    visibility: config.visibility,
                    scope: config.scope,
                    is_shareable: config.isShareable,
                    reshare_rule: config.reshareRule,
                    recipient_ids: selectedRecipients
                };
                await api.post(`/documents/${documentId}/share`, payload);

                toast({
                    title: "Settings Saved",
                    description: `Share settings for ${documentName} have been updated.`,
                });
            }
            onOpenChange(false);
        } catch (error) {
            console.error("Failed to save settings", error);
            toast({
                title: "Error",
                description: "Failed to save share settings.",
                variant: "destructive",
            });
        } finally {
            setSaving(false);
        }
    };

    return (
        <Dialog open={open} onOpenChange={onOpenChange}>
            {/* Reduced max-width by 1/3 approx (from 1400px to ~950px/5xl) */}
            <DialogContent className="max-w-[90vw] md:max-w-5xl lg:max-w-5xl p-0 overflow-hidden h-[90vh] flex flex-col gap-0 border-none">
                {/* Header: Dark by default in design, but let's make it adapt or keep dark for contrast if desired. 
                    User asked: "When Dark Mode is selected... apply dark-mode design." 
                    This implies light mode should look "light".
                */}
                <div className="bg-card text-card-foreground p-6 pb-2 border-b">
                    <div className="flex items-center justify-between">
                        <div>
                            <DialogTitle className="text-xl font-bold">Share Settings: {documentName}</DialogTitle>
                            <DialogDescription className="text-muted-foreground mt-1">
                                Configure visibility and collaborative permissions.
                            </DialogDescription>
                        </div>
                    </div>
                </div>

                <div className="flex-1 flex overflow-hidden flex-col md:flex-row">
                    {/* Left Column: Settings */}
                    {/* Use standard card background which adapts to light/dark */}
                    <div className="w-full md:w-1/2 bg-muted/30 border-r dark:border-border text-foreground p-6 overflow-y-auto">
                        <SharingSettings
                            initialConfig={config}
                            onChange={handleConfigChange}
                        />

                        <div className="mt-8 flex justify-end gap-3">
                            <Button variant="outline" onClick={() => onOpenChange(false)}>
                                Cancel
                            </Button>
                            <Button onClick={handleSave} disabled={saving}>
                                {saving ? "Saving..." : "Save Changes"}
                            </Button>
                        </div>
                    </div>

                    {/* Right Column: Recipients */}
                    {/* White in light mode, dark in dark mode */}
                    <div className="w-full md:w-1/2 bg-background p-6 overflow-hidden flex flex-col">
                        {config.visibility === 'PRIVATE' ? (
                            <RecipientSelector
                                scope={config.scope || 'B2B'}
                                selectedIds={selectedRecipients}
                                onSelectionChange={setSelectedRecipients}
                            />
                        ) : (
                            <div className="flex items-center justify-center h-full text-muted-foreground">
                                <p>Public visibility does not require specific recipients.</p>
                            </div>
                        )}
                    </div>
                </div>
            </DialogContent>
        </Dialog>
    );
}
