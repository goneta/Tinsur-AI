'use client';

import { PermissionMatrix } from '@/components/shared/permission-matrix';

export default function PermissionMatrixPage() {
    return (
        <div className="space-y-6">
            <div>
                <h1 className="text-3xl font-bold tracking-tight">Permission Matrix</h1>
                <p className="text-muted-foreground">
                    Manage role-based access control for all agents and users.
                </p>
            </div>

            <PermissionMatrix showTitle={false} />
        </div>
    );
}
