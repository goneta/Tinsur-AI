'use client';

import { useState } from 'react';
import { Button } from '@/components/ui/button';
import {
    Dialog,
    DialogContent,
    DialogDescription,
    DialogFooter,
    DialogHeader,
    DialogTitle,
    DialogTrigger,
} from '@/components/ui/dialog';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import {
    Select,
    SelectContent,
    SelectItem,
    SelectTrigger,
    SelectValue,
} from '@/components/ui/select';
import { collaborationService } from '@/services/collaborationService';
import { Share2 } from 'lucide-react';
import { useToast } from '@/components/ui/use-toast';

interface CreateShareModalProps {
    onShareCreated: () => void;
}

export function CreateShareModal({ onShareCreated }: CreateShareModalProps) {
    const [open, setOpen] = useState(false);
    const [isLoading, setIsLoading] = useState(false);
    const { toast } = useToast();
    const [formData, setFormData] = useState({
        resource_type: 'document',
        resource_id: '',
        shared_with_company_id: '',
        permissions: 'read',
    });

    const handleSubmit = async (e: React.FormEvent) => {
        e.preventDefault();
        setIsLoading(true);
        try {
            // For MVP, resource_id is manual. In real app, it would be a selector.
            await collaborationService.createShare(formData);
            toast({
                title: 'Resource Shared',
                description: 'Access has been granted successfully.',
            });
            setFormData({ ...formData, resource_id: '', shared_with_company_id: '' });
            onShareCreated();
            setOpen(false);
        } catch (error) {
            toast({
                title: 'Error',
                description: 'Failed to share resource.',
                variant: 'destructive',
            });
        } finally {
            setIsLoading(false);
        }
    };

    return (
        <Dialog open={open} onOpenChange={setOpen}>
            <DialogTrigger asChild>
                <Button className="mb-4">
                    <Share2 className="mr-2 h-4 w-4" /> Share New Resource
                </Button>
            </DialogTrigger>
            <DialogContent className="sm:max-w-[425px]">
                <DialogHeader>
                    <DialogTitle>Share Resource</DialogTitle>
                    <DialogDescription>
                        Grant access to a resource for another company.
                    </DialogDescription>
                </DialogHeader>
                <form onSubmit={handleSubmit}>
                    <div className="grid gap-4 py-4">
                        <div className="grid gap-2">
                            <Label htmlFor="type">Resource Type</Label>
                            <Select
                                value={formData.resource_type}
                                onValueChange={(val) => setFormData({ ...formData, resource_type: val })}
                            >
                                <SelectTrigger>
                                    <SelectValue />
                                </SelectTrigger>
                                <SelectContent>
                                    <SelectItem value="document">Document</SelectItem>
                                    <SelectItem value="policy_template">Policy Template</SelectItem>
                                    <SelectItem value="claim_data">Claim Data</SelectItem>
                                </SelectContent>
                            </Select>
                        </div>
                        <div className="grid gap-2">
                            <Label htmlFor="resource_id">Resource UUID</Label>
                            <Input
                                id="resource_id"
                                value={formData.resource_id}
                                onChange={(e) => setFormData({ ...formData, resource_id: e.target.value })}
                                placeholder="e.g. 123e4567-e89b..."
                                required
                            />
                        </div>
                        <div className="grid gap-2">
                            <Label htmlFor="company_id">Target Company UUID</Label>
                            <Input
                                id="company_id"
                                value={formData.shared_with_company_id}
                                onChange={(e) => setFormData({ ...formData, shared_with_company_id: e.target.value })}
                                placeholder="UUID of partner company"
                                required
                            />
                        </div>
                        <div className="grid gap-2">
                            <Label htmlFor="permissions">Permissions</Label>
                            <Select
                                value={formData.permissions}
                                onValueChange={(val) => setFormData({ ...formData, permissions: val })}
                            >
                                <SelectTrigger>
                                    <SelectValue />
                                </SelectTrigger>
                                <SelectContent>
                                    <SelectItem value="read">Read Only</SelectItem>
                                    <SelectItem value="write">Write</SelectItem>
                                </SelectContent>
                            </Select>
                        </div>
                    </div>
                    <DialogFooter>
                        <Button type="submit" disabled={isLoading}>
                            {isLoading ? 'Sharing...' : 'Share Resource'}
                        </Button>
                    </DialogFooter>
                </form>
            </DialogContent>
        </Dialog>
    );
}
