'use client';

import { useState, useEffect } from 'react';
import {
    Table,
    TableBody,
    TableCell,
    TableHead,
    TableHeader,
    TableRow
} from '@/components/ui/table';
import { Checkbox } from '@/components/ui/checkbox';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import { Loader2, Save } from 'lucide-react';
import { permissionApi } from '@/lib/permission-api';
import { Permission, Role } from '@/types/permission';
import { useToast } from "@/components/ui/use-toast";
import { useLanguage } from '@/contexts/language-context';

export function PermissionMatrix() {
    const { t } = useLanguage();
    const [roles, setRoles] = useState<Role[]>([]);
    const [permissions, setPermissions] = useState<Permission[]>([]);
    const [loading, setLoading] = useState(true);
    const [saving, setSaving] = useState(false);
    // const { toast } = useToast();

    // Group permissions by scope
    const groupedPermissions = permissions.reduce((acc, perm) => {
        if (!acc[perm.scope]) {
            acc[perm.scope] = [];
        }
        acc[perm.scope].push(perm);
        return acc;
    }, {} as Record<string, Permission[]>);

    const sortedScopes = Object.keys(groupedPermissions).sort();

    useEffect(() => {
        loadData();

        // Safety timeout
        const timer = setTimeout(() => {
            if (loading) {
                setLoading(false);
                console.error("Loading timed out");
                // toast({ variant: "destructive", title: "Timeout", description: "Request timed out" });
            }
        }, 5000);
        return () => clearTimeout(timer);
    }, []);

    const loadData = async () => {
        try {
            setLoading(true);
            const [rolesData, permsData] = await Promise.all([
                permissionApi.getRoles(),
                permissionApi.getPermissions()
            ]);

            // Ensure specific order if needed, otherwise backend order
            // User requested: Admin, Manager, Agent, Client, Employee
            const priority = ['super_admin', 'company_admin', 'manager', 'agent', 'client', 'employee'];
            const sortedRoles = rolesData.sort((a, b) => {
                const idxA = priority.indexOf(a.name);
                const idxB = priority.indexOf(b.name);
                // If both found, sort by index
                if (idxA !== -1 && idxB !== -1) return idxA - idxB;
                // If only A found, A comes first
                if (idxA !== -1) return -1;
                // If only B found, B comes first
                if (idxB !== -1) return 1;
                // Neither found, alphabetical
                return a.name.localeCompare(b.name);
            });

            setRoles(sortedRoles);
            setPermissions(permsData);
        } catch (error) {
            console.error("Failed to load permissions matrix", error);
            // toast({ variant: "destructive", title: "Error", description: "Failed to load data" });
        } finally {
            setLoading(false);
        }
    };

    const togglePermission = (roleId: string, permissionId: string, hasPermission: boolean) => {
        // Optimistic update locally
        setRoles(currentRoles => currentRoles.map(role => {
            if (role.id !== roleId) return role;

            const newPermissions = hasPermission
                ? role.permissions.filter(p => p.id !== permissionId) // Remove
                : [...role.permissions, permissions.find(p => p.id === permissionId)!]; // Add

            return { ...role, permissions: newPermissions };
        }));
    };

    const handleSave = async () => {
        try {
            setSaving(true);
            // Save all roles - in a real app might optimize to only changed ones
            // Logic: we iterate roles and update their permission lists
            await Promise.all(roles.map(role =>
                permissionApi.updateRole(role.id, {
                    permissions: role.permissions.map(p => p.id)
                })
            ));

            // toast({ title: "Success", description: "Permissions updated successfully" });
        } catch (error) {
            console.error("Failed to save permissions", error);
            // toast({ variant: "destructive", title: "Error", description: "Failed to save changes" });
            loadData(); // Revert on error
        } finally {
            setSaving(false);
        }
    };

    const hasPermission = (role: Role, permId: string) => {
        return role.permissions.some(p => p.id === permId);
    };

    if (loading) {
        return <div className="flex h-64 items-center justify-center"><Loader2 className="h-8 w-8 animate-spin" /></div>;
    }

    if (roles.length === 0 && !loading) {
        return (
            <div className="p-8 text-center text-red-500 bg-red-50 rounded-lg">
                <p>Failed to load data or unauthorized.</p>
                <Button variant="outline" className="mt-4" onClick={loadData}>Retry</Button>
            </div>
        );
    }

    return (
        <div className="space-y-4">
            <div className="flex justify-between items-center bg-muted/30 p-4 rounded-lg border">
                <div>
                    <h3 className="text-lg font-medium">{t('admin.permissions.matrix', 'Role Permission Matrix')}</h3>
                    <p className="text-sm text-muted-foreground">{t('admin.permissions.manage_desc', 'Manage access control across the platform.')}</p>
                </div>
                <Button onClick={handleSave} disabled={saving}>
                    {saving && <Loader2 className="mr-2 h-4 w-4 animate-spin" />}
                    <Save className="mr-2 h-4 w-4" />
                    {t('common.save_changes', 'Save Changes')}
                </Button>
            </div>

            <div className="border rounded-md overflow-x-auto">
                <Table>
                    <TableHeader>
                        <TableRow>
                            <TableHead className="w-[300px] bg-muted/50 font-bold">{t('admin.permissions.col_perm_role', 'Permission / Role')}</TableHead>
                            {roles.map(role => (
                                <TableHead key={role.id} className="text-center bg-muted/50 font-bold min-w-[100px] capitalization">
                                    <div className="flex flex-col items-center gap-1 py-2">
                                        <Badge variant="outline" className="capitalize text-sm px-3 py-1">
                                            {t(`role.${role.name}`, role.name.replace('_', ' '))}
                                        </Badge>
                                    </div>
                                </TableHead>
                            ))}
                        </TableRow>
                    </TableHeader>
                    <TableBody>
                        {sortedScopes.map(scope => (
                            <>
                                <TableRow key={`header-${scope}`} className="bg-muted/10">
                                    <TableCell colSpan={roles.length + 1} className="font-semibold text-primary capitalize py-3 pl-4">
                                        {t(`admin.permissions.group_${scope}_mgmt`, `${scope} Management`)}
                                    </TableCell>
                                </TableRow>
                                {groupedPermissions[scope].map(perm => (
                                    <TableRow key={perm.id} className="hover:bg-muted/5">
                                        <TableCell className="font-medium">
                                            <div className="flex flex-col">
                                                <span>{t(`perm.${perm.action}`, perm.action)}</span>
                                                <span className="text-xs text-muted-foreground font-normal">
                                                    {t(`perm.${perm.action}_desc`, perm.description || perm.action)}
                                                </span>
                                            </div>
                                        </TableCell>
                                        {roles.map(role => {
                                            const isChecked = hasPermission(role, perm.id);
                                            // Super admin always has everything (visual lock optional)
                                            // const isLocked = role.name === 'super_admin'; 
                                            // Assume backend handles enforcement, UI allows edit

                                            return (
                                                <TableCell key={`${role.id}-${perm.id}`} className="text-center p-0">
                                                    <div className="flex justify-center h-full w-full py-2">
                                                        <Checkbox
                                                            checked={isChecked}
                                                            onCheckedChange={() => togglePermission(role.id, perm.id, isChecked)}
                                                            className="data-[state=checked]:bg-primary h-5 w-5"
                                                        />
                                                    </div>
                                                </TableCell>
                                            );
                                        })}
                                    </TableRow>
                                ))}
                            </>
                        ))}
                    </TableBody>
                </Table>
            </div>
        </div>
    );
}
