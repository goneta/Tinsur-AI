"use client";

import { useState, useEffect } from "react";
import { Plus, Trash2, Edit2, Save, X } from "lucide-react";
import { QuoteElement, QuoteElementCategory } from "@/types/quote-element";
import { quoteElementApi } from "@/lib/quote-element-api";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import {
    Table,
    TableBody,
    TableCell,
    TableHead,
    TableHeader,
    TableRow,
} from "@/components/ui/table";
import {
    Dialog,
    DialogContent,
    DialogDescription,
    DialogFooter,
    DialogHeader,
    DialogTitle,
    DialogTrigger,
} from "@/components/ui/dialog";
import { useToast } from "@/components/ui/use-toast";
import { Badge } from "@/components/ui/badge";
import { Switch } from "@/components/ui/switch";
import { useLanguage } from '@/contexts/language-context';

interface QuoteElementManagerProps {
    category: QuoteElementCategory;
    title: string;
    description: string;
    valueLabel?: string; // e.g., "Percentage (%)" or "Amount (FCFA)"
}

export function QuoteElementManager({ category, title, description, valueLabel = "Value" }: QuoteElementManagerProps) {
    const { t } = useLanguage();
    const { toast } = useToast();
    const [elements, setElements] = useState<QuoteElement[]>([]);
    const [loading, setLoading] = useState(true);
    const [isDialogOpen, setIsDialogOpen] = useState(false);
    const [editingElement, setEditingElement] = useState<QuoteElement | null>(null);

    // Form State
    const [formData, setFormData] = useState({
        name: "",
        value: "",
        description: "",
        is_active: true,
    });

    useEffect(() => {
        loadElements();
    }, [category]);

    const loadElements = async () => {
        setLoading(true);
        try {
            const data = await quoteElementApi.list({ category });
            setElements(data);
        } catch (error) {
            toast({
                title: "Error",
                description: "Failed to load elements.",
                variant: "destructive",
            });
        } finally {
            setLoading(false);
        }
    };

    const handleOpenDialog = (element?: QuoteElement) => {
        if (element) {
            setEditingElement(element);
            setFormData({
                name: element.name,
                value: element.value.toString(),
                description: element.description || "",
                is_active: element.is_active,
            });
        } else {
            setEditingElement(null);
            setFormData({
                name: "",
                value: "",
                description: "",
                is_active: true,
            });
        }
        setIsDialogOpen(true);
    };

    const handleSave = async () => {
        try {
            const payload = {
                category,
                name: formData.name,
                value: parseFloat(formData.value),
                description: formData.description,
                is_active: formData.is_active,
            };

            if (editingElement) {
                await quoteElementApi.update(editingElement.id, payload);
                toast({ title: "Updated", description: "Element updated successfully." });
            } else {
                await quoteElementApi.create(payload);
                toast({ title: "Created", description: "Element created successfully." });
            }

            setIsDialogOpen(false);
            loadElements();
        } catch (error) {
            toast({
                title: "Error",
                description: "Failed to save element.",
                variant: "destructive",
            });
        }
    };

    const handleDelete = async (id: string) => {
        if (!confirm("Are you sure you want to delete this element?")) return;
        try {
            await quoteElementApi.delete(id);
            toast({ title: "Deleted", description: "Element deleted successfully." });
            loadElements();
        } catch (error) {
            toast({
                title: "Error",
                description: "Failed to delete element.",
                variant: "destructive",
            });
        }
    };

    const handleToggleActive = async (element: QuoteElement) => {
        try {
            await quoteElementApi.update(element.id, { is_active: !element.is_active });
            // Optimistic update
            setElements(elements.map(e => e.id === element.id ? { ...e, is_active: !e.is_active } : e));
            toast({ title: "Updated", description: `Element ${!element.is_active ? 'activated' : 'deactivated'}.` });
        } catch (error) {
            loadElements(); // Revert on error
            toast({
                title: "Error",
                description: "Failed to update status.",
                variant: "destructive",
            });
        }
    }

    return (
        <div className="space-y-4">
            <div className="flex justify-between items-center">
                <div>
                    <h3 className="text-lg font-medium">{title}</h3>
                    <p className="text-sm text-muted-foreground">{description}</p>
                </div>
                <Button onClick={() => handleOpenDialog()} size="sm">
                    <Plus className="h-4 w-4 mr-2" />
                    {t('common.add_new', 'Add New')}
                </Button>
            </div>

            <div className="rounded-md border">
                <Table>
                    <TableHeader>
                        <TableRow>
                            <TableHead>{t('common.column.name', 'Name')}</TableHead>
                            <TableHead>{valueLabel}</TableHead>
                            <TableHead>{t('common.description', 'Description')}</TableHead>
                            <TableHead>{t('common.column.status', 'Status')}</TableHead>
                            <TableHead className="text-right">{t('common.column.actions', 'Actions')}</TableHead>
                        </TableRow>
                    </TableHeader>
                    <TableBody>
                        {elements.length === 0 ? (
                            <TableRow>
                                <TableCell colSpan={5} className="text-center h-24 text-muted-foreground">
                                    No elements found.
                                </TableCell>
                            </TableRow>
                        ) : (
                            elements.map((element) => (
                                <TableRow key={element.id}>
                                    <TableCell className="font-medium">
                                        {category === 'base_rate' ? t(`rate.${element.name.toLowerCase().replace(/ /g, '_')}`, element.name) : element.name}
                                    </TableCell>
                                    <TableCell>{element.value}</TableCell>
                                    <TableCell>
                                        {category === 'base_rate' ? t(`rate.${element.name.toLowerCase().replace(/ /g, '_')}_desc`, element.description) : element.description}
                                    </TableCell>
                                    <TableCell>
                                        <Switch
                                            checked={element.is_active}
                                            onCheckedChange={() => handleToggleActive(element)}
                                        />
                                    </TableCell>
                                    <TableCell className="text-right space-x-2">
                                        <Button variant="ghost" size="sm" onClick={() => handleOpenDialog(element)}>
                                            <Edit2 className="h-4 w-4" />
                                        </Button>
                                        <Button variant="ghost" size="sm" onClick={() => handleDelete(element.id)}>
                                            <Trash2 className="h-4 w-4 text-destructive" />
                                        </Button>
                                    </TableCell>
                                </TableRow>
                            ))
                        )}
                    </TableBody>
                </Table>
            </div>

            <Dialog open={isDialogOpen} onOpenChange={setIsDialogOpen}>
                <DialogContent>
                    <DialogHeader>
                        <DialogTitle>{editingElement ? "Edit Element" : "Add New Element"}</DialogTitle>
                        <DialogDescription>
                            Configure the details for this {title.toLowerCase()}.
                        </DialogDescription>
                    </DialogHeader>
                    <div className="space-y-4 py-4">
                        <div className="space-y-2">
                            <Label>Name</Label>
                            <Input
                                value={formData.name}
                                onChange={(e) => setFormData({ ...formData, name: e.target.value })}
                                placeholder="e.g. Standard Rate"
                            />
                        </div>
                        <div className="space-y-2">
                            <Label>{valueLabel}</Label>
                            <Input
                                type="number"
                                step="any"
                                value={formData.value}
                                onChange={(e) => setFormData({ ...formData, value: e.target.value })}
                                placeholder="0.00"
                            />
                        </div>
                        <div className="space-y-2">
                            <Label>Description</Label>
                            <Input
                                value={formData.description}
                                onChange={(e) => setFormData({ ...formData, description: e.target.value })}
                                placeholder="Optional description"
                            />
                        </div>
                        <div className="flex items-center space-x-2">
                            <Switch
                                id="active-mode"
                                checked={formData.is_active}
                                onCheckedChange={(checked) => setFormData({ ...formData, is_active: checked })}
                            />
                            <Label htmlFor="active-mode">Active</Label>
                        </div>
                    </div>
                    <DialogFooter>
                        <Button variant="outline" onClick={() => setIsDialogOpen(false)}>Cancel</Button>
                        <Button onClick={handleSave}>{editingElement ? "Save Changes" : "Create"}</Button>
                    </DialogFooter>
                </DialogContent>
            </Dialog>
        </div>
    );
}
