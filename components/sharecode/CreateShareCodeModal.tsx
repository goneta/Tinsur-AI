import React, { useState, useEffect } from 'react';
import { Button } from "@/components/ui/button";
import {
    Dialog,
    DialogContent,
    DialogDescription,
    DialogFooter,
    DialogHeader,
    DialogTitle,
} from "@/components/ui/dialog";
import {
    Select,
    SelectContent,
    SelectItem,
    SelectTrigger,
    SelectValue,
} from "@/components/ui/select";
import { Checkbox } from "@/components/ui/checkbox";
import { Label } from "@/components/ui/label";
import { createShareCode, ShareCode } from '@/lib/sharecode-api';
import { useToast } from "@/components/ui/use-toast";

interface CreateShareCodeModalProps {
    open: boolean;
    onOpenChange: (open: boolean) => void;
    onSuccess: (shareCode: ShareCode) => void;
}

// Mock recipients for now - in real app would fetch based on type
const MOCK_RECIPIENTS = [
    { id: '1', name: 'Ken Thunderfam (vous)', type: 'user', description: 'Envoyez-vous un message' },
    { id: '2', name: "DESCENDANT DE MOH N'DA", type: 'user', description: 'Bigben, CISSE, Goneta...' },
    { id: '3', name: 'Jean Philippe Sie', type: 'user', description: 'Salut ! J\'utilise WhatsApp.' },
    { id: '4', name: 'Goneta Kenneth Guillaume Cisse', type: 'user', description: '' },
];

export const CreateShareCodeModal: React.FC<CreateShareCodeModalProps> = ({
    open,
    onOpenChange,
    onSuccess
}) => {
    const [shareType, setShareType] = useState<string>('B2B');
    const [selectedRecipients, setSelectedRecipients] = useState<string[]>([]);
    const [loading, setLoading] = useState(false);
    const { toast } = useToast();

    const handleCreate = async () => {
        if (selectedRecipients.length === 0) {
            toast({
                title: "Error",
                description: "Please select at least one recipient",
                variant: "destructive",
            });
            return;
        }

        setLoading(true);
        try {
            const result = await createShareCode({
                share_type: shareType,
                recipient_ids: selectedRecipients
            });
            onSuccess(result);
            onOpenChange(false);
            // Reset form
            setSelectedRecipients([]);
            setShareType('B2B');
        } catch (error) {
            toast({
                title: "Error",
                description: "Failed to generate share code",
                variant: "destructive",
            });
        } finally {
            setLoading(false);
        }
    };

    const toggleRecipient = (id: string) => {
        if (selectedRecipients.includes(id)) {
            setSelectedRecipients(selectedRecipients.filter(r => r !== id));
        } else {
            setSelectedRecipients([...selectedRecipients, id]);
        }
    };

    return (
        <Dialog open={open} onOpenChange={onOpenChange}>
            <DialogContent className="sm:max-w-[425px]">
                <DialogHeader>
                    <DialogTitle>Generate Sharecode</DialogTitle>
                    <DialogDescription>
                        Create a secure code to authorize document sharing with specific recipients.
                    </DialogDescription>
                </DialogHeader>
                <div className="grid gap-4 py-4">
                    <div className="grid gap-2">
                        <Label htmlFor="share-type">Share option</Label>
                        <Select value={shareType} onValueChange={setShareType}>
                            <SelectTrigger id="share-type">
                                <SelectValue placeholder="Select option" />
                            </SelectTrigger>
                            <SelectContent>
                                <SelectItem value="B2B">B2B (Business to Business)</SelectItem>
                                <SelectItem value="B2C">B2C (Business to Client)</SelectItem>
                                <SelectItem value="B2E">B2E (Business to Employee)</SelectItem>
                                <SelectItem value="E2C">E2C (Employee to Client)</SelectItem>
                                <SelectItem value="E2E">E2E (Employee to Employee)</SelectItem>
                                <SelectItem value="C2C">C2C (Client to Client)</SelectItem>
                            </SelectContent>
                        </Select>
                    </div>

                    <div className="grid gap-2">
                        <Label>Recipients</Label>
                        <div className="border rounded-md max-h-[200px] overflow-y-auto p-2 space-y-2">
                            {MOCK_RECIPIENTS.map((recipient) => (
                                <div key={recipient.id} className="flex items-start space-x-3 p-2 hover:bg-gray-50 rounded">
                                    <Checkbox
                                        id={`recipient-${recipient.id}`}
                                        checked={selectedRecipients.includes(recipient.id)}
                                        onCheckedChange={() => toggleRecipient(recipient.id)}
                                        className="mt-1"
                                    />
                                    <div className="grid gap-0.5">
                                        <Label
                                            htmlFor={`recipient-${recipient.id}`}
                                            className="text-sm font-medium leading-none cursor-pointer"
                                        >
                                            {recipient.name}
                                        </Label>
                                        <p className="text-xs text-muted-foreground">{recipient.description}</p>
                                    </div>
                                </div>
                            ))}
                        </div>
                    </div>
                </div>
                <DialogFooter>
                    <Button onClick={handleCreate} disabled={loading} className="w-full">
                        {loading ? "Generating..." : "Generate Sharecode"}
                    </Button>
                </DialogFooter>
            </DialogContent>
        </Dialog>
    );
};
