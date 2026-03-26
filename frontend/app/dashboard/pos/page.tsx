"use client";

import { useState, useEffect } from "react";
import { Plus, Package, Edit, Trash2, Users, BarChart3 } from "lucide-react";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from "@/components/ui/card";
import { Dialog, DialogContent, DialogHeader, DialogTitle, DialogTrigger, DialogFooter } from "@/components/ui/dialog";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from "@/components/ui/table";
import { Badge } from "@/components/ui/badge";
import { useToast } from "@/components/ui/use-toast";
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select";
import { posApi, POSLocation, POSInventory, POSStats } from "@/lib/pos-api";
import { userApi } from "@/lib/user-api";
import { User } from "@/types/user";

import { useLanguage } from '@/contexts/language-context';

export default function POSManagementPage() {
    const { t } = useLanguage();
    const [locations, setLocations] = useState<POSLocation[]>([]);
    const [stats, setStats] = useState<Record<string, POSStats>>({});
    const [loading, setLoading] = useState(true);

    // Dialog States
    const [newLocationOpen, setNewLocationOpen] = useState(false);
    const [inventoryOpen, setInventoryOpen] = useState(false);
    const [agentsOpen, setAgentsOpen] = useState(false);

    // Selection States
    const [selectedLocation, setSelectedLocation] = useState<POSLocation | null>(null);
    const [inventory, setInventory] = useState<POSInventory[]>([]);
    const [agents, setAgents] = useState<User[]>([]);
    const [availableAgents, setAvailableAgents] = useState<User[]>([]);

    // Loading States
    const [invLoading, setInvLoading] = useState(false);
    const [agentsLoading, setAgentsLoading] = useState(false);

    const { toast } = useToast();

    // Forms
    const [formData, setFormData] = useState({
        name: "",
        address: "",
        city: "",
        region: "",
        manager_id: "none",
        is_active: true
    });

    const [invFormData, setInvFormData] = useState({
        item_name: "",
        quantity: 0,
        low_stock_threshold: 10
    });

    const [selectedAgentId, setSelectedAgentId] = useState<string>("");

    useEffect(() => {
        loadData();
    }, []);

    const loadData = async () => {
        setLoading(true);
        try {
            const locs = await posApi.getLocations();
            setLocations(locs);

            // Load stats for each location
            const newStats: Record<string, POSStats> = {};
            await Promise.all(locs.map(async (loc) => {
                try {
                    const stat = await posApi.getStats(loc.id);
                    newStats[loc.id] = stat;
                } catch (e) {
                    console.error("Failed to load stats for", loc.name);
                }
            }));
            setStats(newStats);
        } catch (error) {
            toast({ title: "Error", description: "Failed to load locations", variant: "destructive" });
        } finally {
            setLoading(false);
        }
    };

    const handleOpenInventory = async (location: POSLocation) => {
        setSelectedLocation(location);
        setInventoryOpen(true);
        setInvLoading(true);
        try {
            const data = await posApi.getInventory(location.id);
            setInventory(data);
        } finally {
            setInvLoading(false);
        }
    };

    const handleOpenAgents = async (location: POSLocation) => {
        setSelectedLocation(location);
        setAgentsOpen(true);
        setAgentsLoading(true);
        try {
            const [currentAgents, allUsers] = await Promise.all([
                posApi.getAgents(location.id),
                userApi.list(undefined, 'agent')
            ]);
            setAgents(currentAgents);
            // Filter agents not already assigned to THIS location (though they could be assigned to others, we might want to allow re-assignment)
            setAvailableAgents(allUsers.filter(u => u.pos_location_id !== location.id));
        } finally {
            setAgentsLoading(false);
        }
    };

    const handleCreateLocation = async () => {
        try {
            await posApi.createLocation({
                ...formData,
                manager_id: formData.manager_id === "none" ? undefined : formData.manager_id
            });
            toast({ title: "Success", description: "Location created" });
            setNewLocationOpen(false);
            loadData();
            setFormData({ name: "", address: "", city: "", region: "", manager_id: "none", is_active: true });
        } catch (error) {
            toast({ title: "Error", description: "Failed to create location", variant: "destructive" });
        }
    };

    const handleAddInventory = async () => {
        if (!selectedLocation) return;
        try {
            await posApi.addInventoryItem({
                pos_location_id: selectedLocation.id,
                ...invFormData
            });
            toast({ title: "Success", description: "Item added" });
            const data = await posApi.getInventory(selectedLocation.id);
            setInventory(data);
            setInvFormData({ item_name: "", quantity: 0, low_stock_threshold: 10 });
        } catch (error) {
            toast({ title: "Error", description: "Failed to add item", variant: "destructive" });
        }
    };

    const handleAssignAgent = async () => {
        if (!selectedAgentId || !selectedLocation) return;
        try {
            await userApi.update(selectedAgentId, { pos_location_id: selectedLocation.id });
            toast({ title: "Success", description: "Agent assigned" });

            // Refresh list
            const currentAgents = await posApi.getAgents(selectedLocation.id);
            setAgents(currentAgents);

            // Refresh stats to show updated agent count
            const stat = await posApi.getStats(selectedLocation.id);
            setStats(prev => ({ ...prev, [selectedLocation.id]: stat }));

            setSelectedAgentId("");
        } catch (error) {
            toast({ title: "Error", description: "Failed to assign agent", variant: "destructive" });
        }
    };

    return (
        <div className="space-y-6">
            <div className="flex justify-between items-center">
                <div>
                    <h2 className="text-3xl font-bold tracking-tight">{t('pos.title')}</h2>
                    <p className="text-muted-foreground">{t('pos.desc')}</p>
                </div>
                <Dialog open={newLocationOpen} onOpenChange={setNewLocationOpen}>
                    <DialogTrigger asChild>
                        <Button>
                            <Plus className="mr-2 h-4 w-4" /> {t('pos.add_pos')}
                        </Button>
                    </DialogTrigger>
                    <DialogContent>
                        <DialogHeader>
                            <DialogTitle>{t('pos.add_pos')}</DialogTitle>
                        </DialogHeader>
                        <div className="grid gap-4 py-4">
                            <div className="grid grid-cols-4 items-center gap-4">
                                <Label htmlFor="name" className="text-right">Name</Label>
                                <Input id="name" value={formData.name} onChange={(e) => setFormData({ ...formData, name: e.target.value })} className="col-span-3" />
                            </div>
                            <div className="grid grid-cols-4 items-center gap-4">
                                <Label htmlFor="city" className="text-right">City</Label>
                                <Input id="city" value={formData.city} onChange={(e) => setFormData({ ...formData, city: e.target.value })} className="col-span-3" />
                            </div>
                        </div>
                        <Button onClick={handleCreateLocation} className="w-full">Create Office</Button>
                    </DialogContent>
                </Dialog>
            </div>

            <Card>
                <CardHeader>
                    <CardTitle>{t('pos.pos_locations')}</CardTitle>
                    <CardDescription>{t('pos.performance_metrics', 'Performance metrics per location.')}</CardDescription>
                </CardHeader>
                <CardContent>
                    <Table>
                        <TableHeader>
                            <TableRow>
                                <TableHead>{t('common.column.name', 'Name')}</TableHead>
                                <TableHead>{t('common.column.city', 'City')}</TableHead>
                                <TableHead>{t('pos.active_agents', 'Active Agents')}</TableHead>
                                <TableHead>{t('pos.sales_policies', 'Sales (Policies)')}</TableHead>
                                <TableHead>{t('pos.total_premium', 'Total Premium')}</TableHead>
                                <TableHead>{t('pos.actions', 'Actions')}</TableHead>
                            </TableRow>
                        </TableHeader>
                        <TableBody>
                            {loading ? (
                                <TableRow><TableCell colSpan={6} className="text-center">{t('common.loading', 'Loading...')}</TableCell></TableRow>
                            ) : locations.length === 0 ? (
                                <TableRow><TableCell colSpan={6} className="text-center">{t('pos.no_locations', 'No locations found.')}</TableCell></TableRow>
                            ) : (
                                locations.map((location) => {
                                    const stat = stats[location.id] || { active_agents: 0, total_policies_sold: 0, total_premium_collected: 0 };
                                    return (
                                        <TableRow key={location.id}>
                                            <TableCell className="font-medium">{location.name}</TableCell>
                                            <TableCell>{location.city || "-"}</TableCell>
                                            <TableCell>
                                                <Badge variant="outline" className="flex w-fit items-center gap-1">
                                                    <Users className="h-3 w-3" /> {stat.active_agents}
                                                </Badge>
                                            </TableCell>
                                            <TableCell>{stat.total_policies_sold}</TableCell>
                                            <TableCell>{new Intl.NumberFormat('fr-FR', { style: 'currency', currency: 'XOF' }).format(stat.total_premium_collected)}</TableCell>
                                            <TableCell>
                                                <div className="flex gap-2">
                                                    <Button variant="outline" size="sm" onClick={() => handleOpenInventory(location)}>
                                                        <Package className="h-4 w-4 mr-1" /> {t('pos.stock', 'Stock')}
                                                    </Button>
                                                    <Button variant="outline" size="sm" onClick={() => handleOpenAgents(location)}>
                                                        <Users className="h-4 w-4 mr-1" /> {t('pos.staff', 'Staff')}
                                                    </Button>
                                                </div>
                                            </TableCell>
                                        </TableRow>
                                    );
                                })
                            )}
                        </TableBody>
                    </Table>
                </CardContent>
            </Card>

            {/* Inventory Dialog */}
            <Dialog open={inventoryOpen} onOpenChange={setInventoryOpen}>
                <DialogContent className="max-w-3xl">
                    <DialogHeader>
                        <DialogTitle>{t('pos.inventory_title', 'Inventory: {0}').replace('{0}', selectedLocation?.name || '')}</DialogTitle>
                    </DialogHeader>
                    <div className="space-y-4">
                        <div className="flex items-end gap-2 border p-4 rounded-lg bg-slate-50">
                            <div className="grid gap-2 flex-1">
                                <Label>{t('pos.item_name', 'Item Name')}</Label>
                                <Input placeholder="Stickers, Cards..." value={invFormData.item_name} onChange={e => setInvFormData({ ...invFormData, item_name: e.target.value })} />
                            </div>
                            <div className="grid gap-2 w-24">
                                <Label>{t('pos.qty', 'Qty')}</Label>
                                <Input type="number" value={invFormData.quantity} onChange={e => setInvFormData({ ...invFormData, quantity: parseInt(e.target.value) })} />
                            </div>
                            <Button onClick={handleAddInventory}><Plus className="h-4 w-4" /></Button>
                        </div>

                        <Table>
                            <TableHeader>
                                <TableRow>
                                    <TableHead>{t('common.column.item', 'Item')}</TableHead>
                                    <TableHead>{t('pos.quantity', 'Quantity')}</TableHead>
                                    <TableHead>{t('common.column.status', 'Status')}</TableHead>
                                </TableRow>
                            </TableHeader>
                            <TableBody>
                                {inventory.map(item => (
                                    <TableRow key={item.id}>
                                        <TableCell>{item.item_name}</TableCell>
                                        <TableCell>{item.quantity}</TableCell>
                                        <TableCell>
                                            {item.quantity <= item.low_stock_threshold ?
                                                <Badge variant="destructive">{t('pos.low_stock', 'Low Stock')}</Badge> :
                                                <Badge variant="outline" className="bg-green-50 text-green-700 border-green-200">{t('pos.ok', 'OK')}</Badge>
                                            }
                                        </TableCell>
                                    </TableRow>
                                ))}
                            </TableBody>
                        </Table>
                    </div>
                </DialogContent>
            </Dialog>

            {/* Agents Dialog */}
            <Dialog open={agentsOpen} onOpenChange={setAgentsOpen}>
                <DialogContent className="max-w-2xl">
                    <DialogHeader>
                        <DialogTitle>{t('pos.staff_title', 'Staff at {0}').replace('{0}', selectedLocation?.name || '')}</DialogTitle>
                    </DialogHeader>
                    <div className="space-y-6">
                        <div className="flex items-end gap-2 border p-4 rounded-lg bg-slate-50">
                            <div className="grid gap-2 flex-1">
                                <Label>{t('pos.assign_agent', 'Assign New Agent')}</Label>
                                <Select value={selectedAgentId} onValueChange={setSelectedAgentId}>
                                    <SelectTrigger>
                                        <SelectValue placeholder={t('pos.app_agent_select', 'Select agent...')} />
                                    </SelectTrigger>
                                    <SelectContent>
                                        {availableAgents.map(agent => (
                                            <SelectItem key={agent.id} value={agent.id}>
                                                {agent.first_name} {agent.last_name} ({agent.email})
                                            </SelectItem>
                                        ))}
                                    </SelectContent>
                                </Select>
                            </div>
                            <Button onClick={handleAssignAgent}>{t('pos.assign', 'Assign')}</Button>
                        </div>

                        <div>
                            <h4 className="font-medium mb-4">{t('pos.current_staff', 'Current Staff')}</h4>
                            <Table>
                                <TableHeader>
                                    <TableRow>
                                        <TableHead>{t('common.column.name', 'Name')}</TableHead>
                                        <TableHead>{t('common.column.email', 'Email')}</TableHead>
                                        <TableHead>{t('common.column.role', 'Role')}</TableHead>
                                    </TableRow>
                                </TableHeader>
                                <TableBody>
                                    {agentsLoading ? (
                                        <TableRow><TableCell colSpan={3}>{t('common.loading', 'Loading...')}</TableCell></TableRow>
                                    ) : agents.length === 0 ? (
                                        <TableRow><TableCell colSpan={3} className="text-muted-foreground">{t('pos.no_agents', 'No agents assigned.')}</TableCell></TableRow>
                                    ) : (
                                        agents.map(agent => (
                                            <TableRow key={agent.id}>
                                                <TableCell className="font-medium">{agent.first_name} {agent.last_name}</TableCell>
                                                <TableCell>{agent.email}</TableCell>
                                                <TableCell><Badge variant="outline">{agent.role}</Badge></TableCell>
                                            </TableRow>
                                        ))
                                    )}
                                </TableBody>
                            </Table>
                        </div>
                    </div>
                </DialogContent>
            </Dialog>
        </div>
    );
}
