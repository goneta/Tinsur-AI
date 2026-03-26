
"use client"

import { useEffect, useState } from "react"
import { useRouter } from "next/navigation"
import { ArrowLeft, Check, Shield, Loader2 } from "lucide-react"

import { Button } from "@/components/ui/button"
import {
    Card,
    CardContent,
    CardDescription,
    CardHeader,
    CardTitle,
} from "@/components/ui/card"
import {
    Table,
    TableBody,
    TableCell,
    TableHead,
    TableHeader,
    TableRow,
} from "@/components/ui/table"
import { useToast } from "@/components/ui/use-toast"
import { permissionApi, Role, Permission } from "@/lib/permission-api"

export default function PermissionsPage() {
    const router = useRouter()
    const { toast } = useToast()

    const [roles, setRoles] = useState<Role[]>([])
    const [permissions, setPermissions] = useState<Permission[]>([])
    const [loading, setLoading] = useState(true)
    const [updating, setUpdating] = useState<string | null>(null) // role_id being updated

    useEffect(() => {
        loadData()
    }, [])

    const loadData = async () => {
        try {
            setLoading(true)
            const [rolesData, permsData] = await Promise.all([
                permissionApi.getRoles(),
                permissionApi.getPermissions()
            ])
            setRoles(rolesData)
            setPermissions(permsData)
        } catch (error) {
            toast({
                title: "Error",
                description: "Failed to load permissions data",
                variant: "destructive"
            })
        } finally {
            setLoading(false)
        }
    }

    const togglePermission = async (role: Role, permId: string) => {
        try {
            setUpdating(role.id)

            // Calculate new permissions
            const currentPermIds = role.permissions.map(p => p.id)
            const hasPermission = currentPermIds.includes(permId)

            let newPermIds: string[]
            if (hasPermission) {
                newPermIds = currentPermIds.filter(id => id !== permId)
            } else {
                newPermIds = [...currentPermIds, permId]
            }

            // Optimistic update (local state)
            // But for simplicity/safety, we await API then reload or update state from response
            const updatedRole = await permissionApi.updateRole(role.id, { permissions: newPermIds })

            setRoles(prev => prev.map(r => r.id === role.id ? updatedRole : r))

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

    // Group permissions by scope
    const groupedPermissions = permissions.reduce((acc, perm) => {
        if (!acc[perm.scope]) acc[perm.scope] = []
        acc[perm.scope].push(perm)
        return acc
    }, {} as Record<string, Permission[]>)

    if (loading) {
        return (
            <div className="flex items-center justify-center h-screen">
                <Loader2 className="h-8 w-8 animate-spin" />
            </div>
        )
    }

    return (
        <div className="container mx-auto py-10 space-y-8">
            <div className="flex items-center space-x-4">
                <Button variant="ghost" onClick={() => router.back()}>
                    <ArrowLeft className="mr-2 h-4 w-4" />
                    Back
                </Button>
                <div>
                    <h2 className="text-3xl font-bold tracking-tight">Permission Management</h2>
                    <p className="text-muted-foreground">
                        Manage granular permissions for each user role.
                    </p>
                </div>
            </div>

            <Card>
                <CardHeader>
                    <CardTitle>Permission Matrix</CardTitle>
                    <CardDescription>
                        Toggle permissions to enable or disable features for specific roles.
                    </CardDescription>
                </CardHeader>
                <CardContent>
                    <div className="rounded-md border">
                        <Table>
                            <TableHeader>
                                <TableRow>
                                    <TableHead className="w-[300px]">Permission (Scope : Action)</TableHead>
                                    {roles.map(role => (
                                        <TableHead key={role.id} className="text-center bg-muted/50">
                                            {role.name.toUpperCase()}
                                        </TableHead>
                                    ))}
                                </TableRow>
                            </TableHeader>
                            <TableBody>
                                {Object.entries(groupedPermissions).map(([scope, perms]) => (
                                    <>
                                        <TableRow key={scope} className="bg-muted/20 hover:bg-muted/20">
                                            <TableCell colSpan={roles.length + 1} className="font-semibold text-xs uppercase tracking-wider pl-4">
                                                By Scope: {scope}
                                            </TableCell>
                                        </TableRow>
                                        {perms.map(perm => (
                                            <TableRow key={perm.id}>
                                                <TableCell className="font-medium pl-8">
                                                    <div className="flex items-center space-x-2">
                                                        <span>{perm.action}</span>
                                                        <span className="text-xs text-muted-foreground">
                                                            ({perm.description})
                                                        </span>
                                                    </div>
                                                </TableCell>
                                                {roles.map(role => {
                                                    const hasPerm = role.permissions.some(p => p.id === perm.id)
                                                    const isUpdating = updating === role.id

                                                    // Super Admin is usually immutable or handles all, but here we allow editing
                                                    // unless we want to lock it. Let's allow editing for transparency.

                                                    return (
                                                        <TableCell key={`${role.id}-${perm.id}`} className="text-center">
                                                            <div
                                                                className={`
                                                                    mx-auto h-6 w-6 rounded border cursor-pointer flex items-center justify-center transition-colors
                                                                    ${hasPerm ? 'bg-primary border-primary text-primary-foreground' : 'border-input hover:bg-accent'}
                                                                    ${isUpdating ? 'opacity-50 cursor-not-allowed' : ''}
                                                                `}
                                                                onClick={() => !isUpdating && togglePermission(role, perm.id)}
                                                            >
                                                                {hasPerm && <Check className="h-4 w-4" />}
                                                            </div>
                                                        </TableCell>
                                                    )
                                                })}
                                            </TableRow>
                                        ))}
                                    </>
                                ))}
                            </TableBody>
                        </Table>
                    </div>
                </CardContent>
            </Card>
        </div>
    )
}
