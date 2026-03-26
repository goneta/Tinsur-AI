"use client"

import { Shield } from "lucide-react"
import { Button } from "@/components/ui/button"
import {
    Dialog,
    DialogContent,
    DialogDescription,
    DialogHeader,
    DialogTitle,
} from "@/components/ui/dialog"
import { PermissionMatrix } from "./shared/permission-matrix"
import { useLanguage } from '@/contexts/language-context'

interface UserPermissionsModalProps {
    open: boolean
    onOpenChange: (open: boolean) => void
}

export function UserPermissionsModal({ open, onOpenChange }: UserPermissionsModalProps) {
    const { t } = useLanguage()
    return (
        <Dialog open={open} onOpenChange={onOpenChange}>
            <DialogContent className="max-w-[85vw] w-[85vw] max-h-[90vh] overflow-y-auto">
                <DialogHeader className="mb-4">
                    <DialogTitle className="flex items-center gap-2 text-2xl">
                        <Shield className="h-6 w-6 text-primary" />
                        {t('settings.rbac_title', 'Role-Based Access Control')}
                    </DialogTitle>
                    <DialogDescription>
                        {t('settings.rbac_desc', 'Configure granular permissions for each user role. Changes are reflected in the system upon the next user interaction.')}
                    </DialogDescription>
                </DialogHeader>

                <PermissionMatrix showTitle={false} />

                <div className="flex justify-end pt-6 mt-4 border-t">
                    <Button onClick={() => onOpenChange(false)} variant="secondary" className="px-8">
                        {t('common.done', 'Done')}
                    </Button>
                </div>
            </DialogContent>
        </Dialog>
    )
}
