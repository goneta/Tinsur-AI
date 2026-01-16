"use client";

import { useState, useEffect } from "react";
import { translationApi, Translation } from "@/lib/translation-api";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from "@/components/ui/card";
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from "@/components/ui/table";
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select";
import { Dialog, DialogContent, DialogHeader, DialogTitle, DialogTrigger, DialogFooter } from "@/components/ui/dialog";
import { Label } from "@/components/ui/label";
import { useToast } from "@/components/ui/use-toast";
import { Loader2, Plus, Search, Save } from "lucide-react";

export default function TranslationsPage() {
    const { toast } = useToast();
    const [translations, setTranslations] = useState<Translation[]>([]);
    const [loading, setLoading] = useState(true);
    const [filterLang, setFilterLang] = useState<string>("all");
    const [search, setSearch] = useState("");

    // Create/Edit State
    const [isDialogOpen, setIsDialogOpen] = useState(false);
    const [editingId, setEditingId] = useState<number | null>(null);
    const [formData, setFormData] = useState({
        key: "",
        language_code: "fr",
        value: "",
        group: "common"
    });

    useEffect(() => {
        loadTranslations();
    }, []);

    async function loadTranslations() {
        setLoading(true);
        try {
            // Fetch all (no lang filter on API for now, filter locally)
            const data = await translationApi.getAll();
            setTranslations(data);
        } catch (e) {
            toast({ title: "Error", description: "Failed to load translations", variant: "destructive" });
        } finally {
            setLoading(false);
        }
    }

    const filtered = translations.filter(t => {
        const matchesLang = filterLang === "all" || t.language_code === filterLang;
        const matchesSearch = t.key.toLowerCase().includes(search.toLowerCase()) ||
            t.value.toLowerCase().includes(search.toLowerCase());
        return matchesLang && matchesSearch;
    });

    const handleSave = async () => {
        try {
            if (editingId) {
                await translationApi.update(editingId, { value: formData.value });
                toast({ title: "Success", description: "Translation updated" });
            } else {
                await translationApi.create(formData);
                toast({ title: "Success", description: "Translation created" });
            }
            setIsDialogOpen(false);
            setEditingId(null);
            setFormData({ key: "", language_code: "fr", value: "", group: "common" });
            loadTranslations();
        } catch (e: any) {
            toast({ title: "Error", description: e.response?.data?.detail || "Failed to save", variant: "destructive" });
        }
    };

    const openEdit = (t: Translation) => {
        setEditingId(t.id);
        setFormData({
            key: t.key,
            language_code: t.language_code,
            value: t.value,
            group: t.group || "common"
        });
        setIsDialogOpen(true);
    };

    return (
        <div className="flex-1 space-y-4 p-8 pt-6">
            <div className="flex items-center justify-between space-y-2">
                <h2 className="text-3xl font-bold tracking-tight">Translations</h2>
                <div className="flex items-center space-x-2">
                    <Dialog open={isDialogOpen} onOpenChange={setIsDialogOpen}>
                        <DialogTrigger asChild>
                            <Button onClick={() => {
                                setEditingId(null);
                                setFormData({ key: "", language_code: "fr", value: "", group: "common" });
                            }}>
                                <Plus className="mr-2 h-4 w-4" /> Add Translation
                            </Button>
                        </DialogTrigger>
                        <DialogContent>
                            <DialogHeader>
                                <DialogTitle>{editingId ? "Edit Translation" : "New Translation"}</DialogTitle>
                            </DialogHeader>
                            <div className="grid gap-4 py-4">
                                <div className="grid grid-cols-4 items-center gap-4">
                                    <Label className="text-right">Key</Label>
                                    <Input
                                        className="col-span-3"
                                        value={formData.key}
                                        onChange={e => setFormData({ ...formData, key: e.target.value })}
                                        disabled={!!editingId} // Key immutable on edit
                                    />
                                </div>
                                <div className="grid grid-cols-4 items-center gap-4">
                                    <Label className="text-right">Language</Label>
                                    <Select
                                        value={formData.language_code}
                                        onValueChange={v => setFormData({ ...formData, language_code: v })}
                                        disabled={!!editingId}
                                    >
                                        <SelectTrigger className="col-span-3"><SelectValue /></SelectTrigger>
                                        <SelectContent>
                                            <SelectItem value="en">English</SelectItem>
                                            <SelectItem value="fr">Français</SelectItem>
                                        </SelectContent>
                                    </Select>
                                </div>
                                <div className="grid grid-cols-4 items-center gap-4">
                                    <Label className="text-right">Value</Label>
                                    <Input
                                        className="col-span-3"
                                        value={formData.value}
                                        onChange={e => setFormData({ ...formData, value: e.target.value })}
                                    />
                                </div>
                                <div className="grid grid-cols-4 items-center gap-4">
                                    <Label className="text-right">Group</Label>
                                    <Input
                                        className="col-span-3"
                                        value={formData.group}
                                        onChange={e => setFormData({ ...formData, group: e.target.value })}
                                    />
                                </div>
                            </div>
                            <DialogFooter>
                                <Button onClick={handleSave}>Save changes</Button>
                            </DialogFooter>
                        </DialogContent>
                    </Dialog>
                </div>
            </div>

            <Card>
                <CardHeader>
                    <CardTitle>Manage Translations</CardTitle>
                    <CardDescription>
                        Edit content for multilingual support.
                    </CardDescription>
                    <div className="flex gap-4 pt-4">
                        <div className="relative flex-1">
                            <Search className="absolute left-2 top-2.5 h-4 w-4 text-muted-foreground" />
                            <Input placeholder="Search keys or values..." className="pl-8" value={search} onChange={e => setSearch(e.target.value)} />
                        </div>
                        <Select value={filterLang} onValueChange={setFilterLang}>
                            <SelectTrigger className="w-[180px]">
                                <SelectValue placeholder="Language" />
                            </SelectTrigger>
                            <SelectContent>
                                <SelectItem value="all">All Languages</SelectItem>
                                <SelectItem value="en">English</SelectItem>
                                <SelectItem value="fr">Français</SelectItem>
                            </SelectContent>
                        </Select>
                    </div>
                </CardHeader>
                <CardContent>
                    {loading ? (
                        <div className="flex justify-center p-8"><Loader2 className="h-8 w-8 animate-spin" /></div>
                    ) : (
                        <Table>
                            <TableHeader>
                                <TableRow>
                                    <TableHead>Key</TableHead>
                                    <TableHead>Lang</TableHead>
                                    <TableHead>Value</TableHead>
                                    <TableHead>Group</TableHead>
                                    <TableHead className="text-right">Actions</TableHead>
                                </TableRow>
                            </TableHeader>
                            <TableBody>
                                {filtered.map((t) => (
                                    <TableRow key={t.id}>
                                        <TableCell className="font-mono text-xs">{t.key}</TableCell>
                                        <TableCell>
                                            <span className="uppercase text-xs font-bold bg-slate-100 px-2 py-1 rounded">{t.language_code}</span>
                                        </TableCell>
                                        <TableCell className="max-w-[300px] truncate" title={t.value}>{t.value}</TableCell>
                                        <TableCell>{t.group}</TableCell>
                                        <TableCell className="text-right">
                                            <Button variant="ghost" size="sm" onClick={() => openEdit(t)}>Edit</Button>
                                        </TableCell>
                                    </TableRow>
                                ))}
                            </TableBody>
                        </Table>
                    )}
                </CardContent>
            </Card>
        </div>
    );
}
