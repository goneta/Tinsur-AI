"use client";

import { useEffect, useState } from "react";
import { useLanguage } from "@/contexts/language-context";
import { translationApi, Translation, TranslationUpdate, TranslationCreate } from "@/lib/translation-api";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
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
import { Label } from "@/components/ui/label";
import { Plus, Search, Loader2 } from "lucide-react";
import { useToast } from "@/components/ui/use-toast";

export default function TranslationsPage() {
    const { t } = useLanguage();
    const { toast } = useToast();
    const [translations, setTranslations] = useState<Translation[]>([]);
    const [loading, setLoading] = useState(true);
    const [searchTerm, setSearchTerm] = useState("");
    const [isDialogOpen, setIsDialogOpen] = useState(false);
    const [currentTranslation, setCurrentTranslation] = useState<Translation | null>(null);
    const [isCreateMode, setIsCreateMode] = useState(false);

    // Form State
    const [formData, setFormData] = useState<TranslationCreate>({
        key: "",
        language_code: "fr",
        value: "",
        group: "common"
    });

    const fetchTranslations = async () => {
        setLoading(true);
        try {
            // Fetch all translations (admin view likely needs all)
            // Since backend filtering by lang is optional, we can fetch all or handle filtering here
            // The current API endpoint /translations/list returns a list
            const data = await translationApi.getAll();
            setTranslations(data);
        } catch (error) {
            toast({
                title: "Error",
                description: "Failed to load translations",
                variant: "destructive",
            });
        } finally {
            setLoading(false);
        }
    };

    useEffect(() => {
        fetchTranslations();
    }, []);

    const handleSave = async () => {
        try {
            if (isCreateMode) {
                await translationApi.create(formData);
                toast({ title: "Success", description: "Translation created successfully" });
            } else if (currentTranslation) {
                await translationApi.update(currentTranslation.id, {
                    value: formData.value,
                    is_active: true // Ensure it stays active
                });
                toast({ title: "Success", description: "Translation updated successfully" });
            }
            setIsDialogOpen(false);
            fetchTranslations();
        } catch (error) {
            toast({
                title: "Error",
                description: "Failed to save translation",
                variant: "destructive",
            });
        }
    };

    const openCreateDialog = () => {
        setIsCreateMode(true);
        setFormData({ key: "", language_code: "fr", value: "", group: "common" });
        setCurrentTranslation(null);
        setIsDialogOpen(true);
    };

    const openEditDialog = (translation: Translation) => {
        setIsCreateMode(false);
        setFormData({
            key: translation.key,
            language_code: translation.language_code,
            value: translation.value,
            group: translation.group
        });
        setCurrentTranslation(translation);
        setIsDialogOpen(true);
    };

    const filteredTranslations = translations.filter((item) =>
        item.key.toLowerCase().includes(searchTerm.toLowerCase()) ||
        item.value.toLowerCase().includes(searchTerm.toLowerCase())
    );

    return (
        <div className="p-6 space-y-6">
            <div className="flex justify-between items-center">
                <div>
                    <h1 className="text-3xl font-bold tracking-tight">{t("Translations")}</h1>
                    <p className="text-muted-foreground">
                        {t("Manage application translations")}
                    </p>
                </div>
                <Button onClick={openCreateDialog}>
                    <Plus className="mr-2 h-4 w-4" /> {t("Add Translation")}
                </Button>
            </div>

            <div className="flex items-center space-x-2">
                <div className="relative flex-1 max-w-sm">
                    <Search className="absolute left-2 top-2.5 h-4 w-4 text-muted-foreground" />
                    <Input
                        placeholder={t("Search translations...")}
                        className="pl-8"
                        value={searchTerm}
                        onChange={(e) => setSearchTerm(e.target.value)}
                    />
                </div>
            </div>

            <div className="border rounded-md">
                <Table>
                    <TableHeader>
                        <TableRow>
                            <TableHead>{t("Key")}</TableHead>
                            <TableHead>{t("Language")}</TableHead>
                            <TableHead>{t("Value")}</TableHead>
                            <TableHead className="w-[100px]">{t("Actions")}</TableHead>
                        </TableRow>
                    </TableHeader>
                    <TableBody>
                        {loading ? (
                            <TableRow>
                                <TableCell colSpan={4} className="h-24 text-center">
                                    <Loader2 className="h-6 w-6 animate-spin mx-auto" />
                                </TableCell>
                            </TableRow>
                        ) : filteredTranslations.length === 0 ? (
                            <TableRow>
                                <TableCell colSpan={4} className="h-24 text-center">
                                    {t("No translations found")}
                                </TableCell>
                            </TableRow>
                        ) : (
                            filteredTranslations.map((item) => (
                                <TableRow key={item.id}>
                                    <TableCell className="font-medium">{item.key}</TableCell>
                                    <TableCell>
                                        <span className={`inline-flex items-center rounded-full px-2.5 py-0.5 text-xs font-medium ${item.language_code === 'en' ? 'bg-blue-100 text-blue-800' : 'bg-purple-100 text-purple-800'}`}>
                                            {item.language_code.toUpperCase()}
                                        </span>
                                    </TableCell>
                                    <TableCell className="max-w-md truncate" title={item.value}>
                                        {item.value}
                                    </TableCell>
                                    <TableCell>
                                        <Button
                                            variant="ghost"
                                            size="sm"
                                            onClick={() => openEditDialog(item)}
                                        >
                                            {t("Edit")}
                                        </Button>
                                    </TableCell>
                                </TableRow>
                            ))
                        )}
                    </TableBody>
                </Table>
            </div>

            <Dialog open={isDialogOpen} onOpenChange={setIsDialogOpen}>
                <DialogContent className="sm:max-w-[425px]">
                    <DialogHeader>
                        <DialogTitle>
                            {isCreateMode ? t("Add Translation") : t("Edit Translation")}
                        </DialogTitle>
                        <DialogDescription>
                            {t("Make changes to the translation here. Click save when you're done.")}
                        </DialogDescription>
                    </DialogHeader>
                    <div className="grid gap-4 py-4">
                        <div className="grid grid-cols-4 items-center gap-4">
                            <Label htmlFor="key" className="text-right">
                                {t("Key")}
                            </Label>
                            <Input
                                id="key"
                                value={formData.key}
                                onChange={(e) => setFormData({ ...formData, key: e.target.value })}
                                className="col-span-3"
                                disabled={!isCreateMode} // Key is immutable on edit
                            />
                        </div>
                        <div className="grid grid-cols-4 items-center gap-4">
                            <Label htmlFor="lang" className="text-right">
                                {t("Language")}
                            </Label>
                            <select
                                id="lang"
                                className="flex h-10 w-full rounded-md border border-input bg-background px-3 py-2 text-sm ring-offset-background file:border-0 file:bg-transparent file:text-sm file:font-medium placeholder:text-muted-foreground focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring focus-visible:ring-offset-2 disabled:cursor-not-allowed disabled:opacity-50 col-span-3"
                                value={formData.language_code}
                                onChange={(e) => setFormData({ ...formData, language_code: e.target.value })}
                                disabled={!isCreateMode} // Language is immutable on edit usually, or we create a new entry
                            >
                                <option value="fr">French (FR)</option>
                                <option value="en">English (EN)</option>
                            </select>
                        </div>
                        <div className="grid grid-cols-4 items-center gap-4">
                            <Label htmlFor="value" className="text-right">
                                {t("Value")}
                            </Label>
                            <Input
                                id="value"
                                value={formData.value}
                                onChange={(e) => setFormData({ ...formData, value: e.target.value })}
                                className="col-span-3"
                            />
                        </div>
                    </div>
                    <DialogFooter>
                        <Button onClick={handleSave}>{t("Save changes")}</Button>
                    </DialogFooter>
                </DialogContent>
            </Dialog>
        </div>
    );
}
