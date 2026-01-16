'use client';

import {
    Dialog,
    DialogContent,
    DialogDescription,
    DialogFooter,
    DialogHeader,
    DialogTitle,
} from '@/components/ui/dialog';
import { Button } from '@/components/ui/button';
import { ShieldAlert } from 'lucide-react';

interface PermissionDeniedModalProps {
    isOpen: boolean;
    onClose: () => void;
}

export function PermissionDeniedModal({ isOpen, onClose }: PermissionDeniedModalProps) {
    return (
        <Dialog open={isOpen} onOpenChange={onClose}>
            <DialogContent className="sm:max-w-md">
                <DialogHeader>
                    <div className="flex items-center gap-3 text-destructive mb-2">
                        <ShieldAlert className="h-6 w-6" />
                        <DialogTitle className="text-xl">Access Denied</DialogTitle>
                    </div>
                    <DialogDescription className="text-base text-slate-700 font-medium">
                        You don't have the permission to operate this action. (Admin only)
                    </DialogDescription>
                </DialogHeader>
                <DialogFooter className="mt-4">
                    <Button
                        variant="secondary"
                        onClick={onClose}
                        className="w-full sm:w-auto"
                    >
                        Understood
                    </Button>
                </DialogFooter>
            </DialogContent>
        </Dialog>
    );
}
