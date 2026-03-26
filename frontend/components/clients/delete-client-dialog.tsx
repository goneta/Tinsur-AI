/**
 * Delete client confirmation dialog.
 */
'use client';

import { useState } from 'react';
import { clientApi } from '@/lib/client-api';
import { Client } from '@/types/client';
import {
    Dialog,
    DialogContent,
    DialogDescription,
    DialogFooter,
    DialogHeader,
    DialogTitle,
} from '@/components/ui/dialog';
import { Button } from '@/components/ui/button';

interface DeleteClientDialogProps {
    open: boolean;
    onOpenChange: (open: boolean) => void;
    client?: Client | null;
    onSuccess: () => void;
}

export function DeleteClientDialog({
    open,
    onOpenChange,
    client,
    onSuccess,
}: DeleteClientDialogProps) {
    const [loading, setLoading] = useState(false);
    const [error, setError] = useState('');

    if (!client && open) {
        // This case shouldn't happen if managed correctly by parent, 
        // but helps with type safety and prevents crashes.
        return null;
    }

    const handleDelete = async () => {
        if (!client) return;
        setError('');
        setLoading(true);

        try {
            await clientApi.deleteClient(client.id);
            onSuccess();
        } catch (err: any) {
            setError(err.response?.data?.detail || err.message || 'Failed to delete client');
        } finally {
            setLoading(false);
        }
    };

    const clientName = client ? (
        client.client_type === 'individual'
            ? `${client.first_name} ${client.last_name}`
            : client.business_name
    ) : '';

    return (
        <Dialog open={open} onOpenChange={onOpenChange}>
            <DialogContent>
                <DialogHeader>
                    <DialogTitle>Delete Client</DialogTitle>
                    <DialogDescription>
                        Are you sure you want to delete {clientName}? This action cannot be undone.
                    </DialogDescription>
                </DialogHeader>

                {error && (
                    <div className="rounded-md bg-red-50 p-3 text-sm text-red-800">
                        {error}
                    </div>
                )}

                <DialogFooter>
                    <Button
                        variant="outline"
                        onClick={() => onOpenChange(false)}
                        disabled={loading}
                    >
                        Cancel
                    </Button>
                    <Button
                        variant="destructive"
                        onClick={handleDelete}
                        disabled={loading}
                    >
                        {loading ? 'Deleting...' : 'Delete Client'}
                    </Button>
                </DialogFooter>
            </DialogContent>
        </Dialog>
    );
}
