'use client';

import * as React from "react"
import { useEffect, useState, Fragment } from "react"
import { Check, Loader2, Shield, RefreshCw, Plus } from "lucide-react"
import {
    Table,
    TableBody,
    TableCell,
    TableHead,
    TableHeader,
    TableRow,
} from "@/components/ui/table"
import { Button } from "@/components/ui/button"
import { useToast } from "@/components/ui/use-toast"
import {
    Dialog,
    DialogContent,
    DialogDescription,
    DialogFooter,
    DialogHeader,
    DialogTitle,
    DialogTrigger,
} from "@/components/ui/dialog"
import { Input } from "@/components/ui/input"
import { Label } from "@/components/ui/label"
import { Textarea } from "@/components/ui/textarea"
import { Checkbox } from "@/components/ui/checkbox"
import { permissionApi, Role, Permission } from "@/lib/api/permissions"

interface PermissionMatrixProps {
    showTitle?: boolean;
    className?: string;
}

export function PermissionMatrix({ showTitle = true, className }: PermissionMatrixProps) {
    const { toast } = useToast()
    const [roles, setRoles] = useState<Role[]>([])
    const [permissions, setPermissions] = useState<Permission[]>([])
    const [loading, setLoading] = useState(true)
    const [updating, setUpdating] = useState<string | null>(null) // role_id-perm_id being updated

    // New Permission State
    const [isCreateDialogOpen, setIsCreateDialogOpen] = useState(false)
    const [newPermission, setNewPermission] = useState({
        scope: '',
        action: '',
        description: ''
    })
    const [isCreating, setIsCreating] = useState(false)

    const fetchData = async () => {
        setLoading(true)
        try {
            const [rolesData, permsData] = await Promise.all([
                permissionApi.getRoles(),
                permissionApi.getPermissions()
            ])

            // Logically sort roles: Admin, Company Admin, Agent, Receptionist, Client
            const roleOrder = ['super_admin', 'company_admin', 'agent', 'receptionist', 'client', 'manager']
            const sortedRoles = [...rolesData].sort((a, b) => {
                const nameA = (a.name || '').toLowerCase().trim()
                const nameB = (b.name || '').toLowerCase().trim()
                const idxA = roleOrder.indexOf(nameA)
                const idxB = roleOrder.indexOf(nameB)
                return (idxA === -1 ? 99 : idxA) - (idxB === -1 ? 99 : idxB)
            })

            // Only show roles requested by user + manager if it exists
            const filteredRoles = sortedRoles.filter(r => roleOrder.includes(r.name.toLowerCase().trim()))

            setRoles(filteredRoles)
            setPermissions(permsData)
        } catch (error) {
            console.error("Fetch permissions error:", error)
            toast({
                title: "Error",
                description: "Failed to load permissions data",
                variant: "destructive"
            })
        } finally {
            setLoading(false)
        }
    }

    useEffect(() => {
        fetchData()
    }, [])

    const roleDisplayName = (name: string) => {
        const normalized = name.toLowerCase().trim()
        if (normalized === 'super_admin') return 'Admin'
        if (normalized === 'company_admin') return 'Company Admin'
        if (normalized === 'agent') return 'Agent'
        if (normalized === 'receptionist') return 'Receptionist'
        if (normalized === 'client') return 'Client'
        if (normalized === 'manager') return 'Manager'
        return name
    }

    const togglePermission = async (role: Role, permId: string) => {
        try {
            setUpdating(`${role.id}-${permId}`)

            const hasPermission = role.permissions.some(p => p.id === permId)
            const newPermIds = hasPermission
                ? role.permissions.filter(p => p.id !== permId).map(p => p.id)
                : [...role.permissions.map(p => p.id), permId]

            // Update role permissions
            await permissionApi.assignPermissions(role.id, newPermIds)

            // Update local state - re-fetch to be safe and get full objects
            await fetchData()

            toast({
                title: "Permission updated",
                description: `${roleDisplayName(role.name)} permissions updated successfully.`,
            })

        } catch (error) {
            toast({
                title: "Error",
                description: "Failed to update permission",
                variant: "destructive"
            })
        } finally {
            setUpdating(null)
        }
    }

    const handleCreatePermission = async (e: React.FormEvent) => {
        e.preventDefault()
        if (!newPermission.scope || !newPermission.action) return

        setIsCreating(true)
        try {
            await permissionApi.createPermission(newPermission)
            toast({
                title: "Success",
                description: "New permission created successfully.",
            })
            setIsCreateDialogOpen(false)
            setNewPermission({ scope: '', action: '', description: '' })
            fetchData()
        } catch (error) {
            toast({
                title: "Error",
                description: "Failed to create permission.",
                variant: "destructive"
            })
        } finally {
            setIsCreating(false)
        }
    }

    // Group permissions by scope
    const groupedPermissions = permissions.reduce((acc, perm) => {
        const scope = perm.scope || 'general'
        if (!acc[scope]) acc[scope] = []
        acc[scope].push(perm)
        return acc
    }, {} as Record<string, Permission[]>)

    if (loading && roles.length === 0) {
        return (
            <div className="flex flex-col items-center justify-center py-20 space-y-4">
                <Loader2 className="h-10 w-10 animate-spin text-primary" />
                <p className="text-muted-foreground animate-pulse">Loading permission matrix...</p>
            </div>
        )
    }

    return (
        <div className={`space-y-6 ${className}`}>
            {showTitle && (
                <div className="flex items-center justify-between">
                    <div>
                        <h2 className="text-2xl font-bold tracking-tight">Permission Matrix</h2>
                        <p className="text-muted-foreground">
                            Manage role-based access control for all users.
                        </p>
                    </div>
                    <div className="flex items-center gap-2">
                        <Dialog open={isCreateDialogOpen} onOpenChange={setIsCreateDialogOpen}>
                            <DialogTrigger asChild>
                                <Button size="sm">
                                    <Plus className="mr-2 h-4 w-4" />
                                    New Permission
                                </Button>
                            </DialogTrigger>
                            <DialogContent className="sm:max-w-[425px]">
                                <form onSubmit={handleCreatePermission}>
                                    <DialogHeader>
                                        <DialogTitle>Create New Permission</DialogTitle>
                                        <DialogDescription>
                                            Add a new granular action that can be assigned to different roles.
                                        </DialogDescription>
                                    </DialogHeader>
                                    <div className="grid gap-4 py-4">
                                        <div className="grid grid-cols-4 items-center gap-4">
                                            <Label htmlFor="scope" className="text-right">
                                                Scope
                                            </Label>
                                            <Input
                                                id="scope"
                                                placeholder="e.g. policy"
                                                className="col-span-3"
                                                value={newPermission.scope}
                                                onChange={(e) => setNewPermission({ ...newPermission, scope: e.target.value })}
                                                required
                                            />
                                        </div>
                                        <div className="grid grid-cols-4 items-center gap-4">
                                            <Label htmlFor="action" className="text-right">
                                                Action
                                            </Label>
                                            <Input
                                                id="action"
                                                placeholder="e.g. delete"
                                                className="col-span-3"
                                                value={newPermission.action}
                                                onChange={(e) => setNewPermission({ ...newPermission, action: e.target.value })}
                                                required
                                            />
                                        </div>
                                        <div className="grid grid-cols-4 items-center gap-4">
                                            <Label htmlFor="description" className="text-right">
                                                Description
                                            </Label>
                                            <Textarea
                                                id="description"
                                                placeholder="What does this allow?"
                                                className="col-span-3"
                                                value={newPermission.description}
                                                onChange={(e) => setNewPermission({ ...newPermission, description: e.target.value })}
                                            />
                                        </div>
                                    </div>
                                    <DialogFooter>
                                        <Button type="submit" disabled={isCreating}>
                                            {isCreating ? <Loader2 className="h-4 w-4 animate-spin mr-2" /> : null}
                                            Create Permission
                                        </Button>
                                    </DialogFooter>
                                </form>
                            </DialogContent>
                        </Dialog>

                        <Button variant="outline" size="sm" onClick={fetchData} disabled={loading}>
                            <RefreshCw className={`mr-2 h-4 w-4 ${loading ? 'animate-spin' : ''}`} />
                            Refresh
                        </Button>
                    </div>
                </div>
            )}

            {!showTitle && (
                <div className="flex justify-end mb-4">
                    <Dialog open={isCreateDialogOpen} onOpenChange={setIsCreateDialogOpen}>
                        <DialogTrigger asChild>
                            <Button size="sm" variant="outline" className="border-dashed">
                                <Plus className="mr-2 h-4 w-4" />
                                Add Custom Permission
                            </Button>
                        </DialogTrigger>
                        <DialogContent className="sm:max-w-[425px]">
                            <form onSubmit={handleCreatePermission}>
                                <DialogHeader>
                                    <DialogTitle>Create New Permission</DialogTitle>
                                    <DialogDescription>
                                        Add a new granular action that can be assigned to different roles.
                                    </DialogDescription>
                                </DialogHeader>
                                <div className="grid gap-4 py-4">
                                    <div className="grid grid-cols-4 items-center gap-4">
                                        <Label htmlFor="scope" className="text-right">
                                            Scope
                                        </Label>
                                        <Input
                                            id="scope"
                                            placeholder="e.g. policy"
                                            className="col-span-3"
                                            value={newPermission.scope}
                                            onChange={(e) => setNewPermission({ ...newPermission, scope: e.target.value })}
                                            required
                                        />
                                    </div>
                                    <div className="grid grid-cols-4 items-center gap-4">
                                        <Label htmlFor="action" className="text-right">
                                            Action
                                        </Label>
                                        <Input
                                            id="action"
                                            placeholder="e.g. delete"
                                            className="col-span-3"
                                            value={newPermission.action}
                                            onChange={(e) => setNewPermission({ ...newPermission, action: e.target.value })}
                                            required
                                        />
                                    </div>
                                    <div className="grid grid-cols-4 items-center gap-4">
                                        <Label htmlFor="description" className="text-right">
                                            Description
                                        </Label>
                                        <Textarea
                                            id="description"
                                            placeholder="What does this allow?"
                                            className="col-span-3"
                                            value={newPermission.description}
                                            onChange={(e) => setNewPermission({ ...newPermission, description: e.target.value })}
                                        />
                                    </div>
                                </div>
                                <DialogFooter>
                                    <Button type="submit" disabled={isCreating}>
                                        {isCreating ? <Loader2 className="h-4 w-4 animate-spin mr-2" /> : null}
                                        Create Permission
                                    </Button>
                                </DialogFooter>
                            </form>
                        </DialogContent>
                    </Dialog>
                </div>
            )}

            <div className="rounded-xl border bg-card/50 backdrop-blur-sm shadow-sm overflow-hidden">
                <div className="overflow-x-auto">
                    <Table>
                        <TableHeader>
                            <TableRow className="bg-muted/50 hover:bg-muted/50 whitespace-nowrap">
                                <TableHead className="w-[320px] font-bold">Permission / Scope</TableHead>
                                {roles.map(role => (
                                    <TableHead key={role.id} className="text-center min-w-[140px]">
                                        <div className="flex flex-col items-center py-2 px-4 border-l">
                                            <span className="font-black text-primary uppercase text-[11px] tracking-[0.1em]">
                                                {roleDisplayName(role.name)}
                                            </span>
                                            {role.description && (
                                                <span className="text-[10px] font-normal text-muted-foreground uppercase mt-1 opacity-70">
                                                    {role.description.replace('Default ', '').replace(' role', '')}
                                                </span>
                                            )}
                                        </div>
                                    </TableHead>
                                ))}
                            </TableRow>
                        </TableHeader>
                        <TableBody>
                            {Object.entries(groupedPermissions).length === 0 && !loading && (
                                <TableRow>
                                    <TableCell colSpan={roles.length + 1} className="py-20 text-center text-muted-foreground italic">
                                        No permissions found. Click "Add Custom Permission" to get started.
                                    </TableCell>
                                </TableRow>
                            )}
                            {Object.entries(groupedPermissions).map(([scope, perms]) => (
                                <Fragment key={scope}>
                                    <TableRow className="bg-muted/30 border-y">
                                        <TableCell colSpan={roles.length + 1} className="py-2 px-4">
                                            <div className="flex items-center gap-2">
                                                <Shield className="h-3.5 w-3.5 text-primary" />
                                                <span className="text-xs font-black uppercase tracking-widest text-primary/80">
                                                    {scope}
                                                </span>
                                            </div>
                                        </TableCell>
                                    </TableRow>
                                    {perms.map(perm => (
                                        <TableRow key={perm.id} className="hover:bg-muted/10 transition-colors">
                                            <TableCell className="pl-8 py-4">
                                                <div className="flex flex-col">
                                                    <span className="text-sm font-semibold capitalize">
                                                        {perm.action || (perm.key ? perm.key.split(':')[1] : 'unknown')}
                                                    </span>
                                                    {perm.description && (
                                                        <span className="text-xs text-muted-foreground leading-tight">
                                                            {perm.description}
                                                        </span>
                                                    )}
                                                </div>
                                            </TableCell>
                                            {roles.map(role => {
                                                const hasPerm = role.permissions.some(p => p.id === perm.id)
                                                const isUpdating = updating === `${role.id}-${perm.id}`

                                                return (
                                                    <TableCell key={`${role.id}-${perm.id}`} className="text-center border-l">
                                                        <div className="flex justify-center items-center">
                                                            {isUpdating ? (
                                                                <Loader2 className="h-4 w-4 animate-spin text-primary" />
                                                            ) : (
                                                                <Checkbox
                                                                    id={`${role.id}-${perm.id}`}
                                                                    checked={hasPerm}
                                                                    disabled={loading || updating !== null}
                                                                    onCheckedChange={() => togglePermission(role, perm.id)}
                                                                />
                                                            )}
                                                        </div>
                                                    </TableCell>
                                                )
                                            })}
                                        </TableRow>
                                    ))}
                                </Fragment>
                            ))}
                        </TableBody>
                    </Table>
                </div>
            </div>

            <p className="text-[11px] text-muted-foreground italic px-2">
                * Changes are applied instantly. Some permissions may require user logout/login to take full effect.
            </p>
        </div>
    )
}
