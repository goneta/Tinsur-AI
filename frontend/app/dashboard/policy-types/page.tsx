"use client";

import { useState, useEffect } from "react";
import { Plus, Search, Shield } from "lucide-react";
import { QuoteAPI } from "@/lib/api/quotes";
import { PolicyType } from "@/types/quote";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import {
    Card,
    CardContent,
    CardDescription,
    CardHeader,
    CardTitle,
} from "@/components/ui/card";
import {
    Dialog,
    DialogContent,
    DialogDescription,
    DialogHeader,
    DialogTitle,
    DialogTrigger,
} from "@/components/ui/dialog";
import {
    Table,
    TableBody,
    TableCell,
    TableHead,
    TableHeader,
    TableRow,
} from "@/components/ui/table";
import { PolicyTypeForm } from "@/components/management/policy-type-form";

import { useLanguage } from '@/contexts/language-context';

export default function PolicyTypesPage() {
    const { t } = useLanguage();
    const [policyTypes, setPolicyTypes] = useState<PolicyType[]>([]);
    const [searchQuery, setSearchQuery] = useState("");
    const [isCreateOpen, setIsCreateOpen] = useState(false);

    useEffect(() => {
        loadPolicyTypes();
    }, []);

    const loadPolicyTypes = async () => {
        try {
            const data = await QuoteAPI.listPolicyTypes();
            setPolicyTypes(data);
        } catch (error) {
            console.error("Failed to load policy types", error);
        }
    };

    const handleCreateSuccess = (newType: PolicyType) => {
        setIsCreateOpen(false);
        loadPolicyTypes();
    };

    const filteredTypes = policyTypes.filter(type =>
        type.name.toLowerCase().includes(searchQuery.toLowerCase()) ||
        type.code.toLowerCase().includes(searchQuery.toLowerCase())
    );

    return (
        <div className="flex-1 space-y-4 p-4 md:p-8 pt-6">
            <div className="flex items-center justify-between space-y-2">
                <div>
                    <h2 className="text-3xl font-bold tracking-tight">{t('policy_types.title')}</h2>
                    <p className="text-muted-foreground">
                        {t('policy_types.desc')}
                    </p>
                </div>
                <div className="flex items-center space-x-2">
                    <Dialog open={isCreateOpen} onOpenChange={setIsCreateOpen}>
                        <DialogTrigger asChild>
                            <Button>
                                <Plus className="mr-2 h-4 w-4" /> {t('policy_types.new_type')}
                            </Button>
                        </DialogTrigger>
                        <DialogContent>
                            <DialogHeader>
                                <DialogTitle>{t('policy_types.new_type')}</DialogTitle>
                                <DialogDescription>
                                    {t('policy_types.dialog_desc', 'Add a new policy type to the system.')}
                                </DialogDescription>
                            </DialogHeader>
                            <PolicyTypeForm
                                onSuccess={handleCreateSuccess}
                                onCancel={() => setIsCreateOpen(false)}
                            />
                        </DialogContent>
                    </Dialog>
                </div>
            </div>

            <Card>
                <CardHeader>
                    <CardTitle>{t('policy_types.defined_types')}</CardTitle>
                    <CardDescription>
                        {t('policy_types.list_desc', 'List of all active policy types available for quotes.')}
                    </CardDescription>
                    <div className="flex items-center pt-2">
                        <Search className="mr-2 h-4 w-4 text-muted-foreground" />
                        <Input
                            placeholder={t('policy_types.search')}
                            className="max-w-sm"
                            value={searchQuery}
                            onChange={(e) => setSearchQuery(e.target.value)}
                        />
                    </div>
                </CardHeader>
                <CardContent>
                    <Table>
                        <TableHeader>
                            <TableRow>
                                <TableHead>{t('policy_types.type_name')}</TableHead>
                                <TableHead>{t('policy_types.code')}</TableHead>
                                <TableHead>{t('policy_types.description')}</TableHead>
                                <TableHead className="text-right">ID</TableHead>
                            </TableRow>
                        </TableHeader>
                        <TableBody>
                            {filteredTypes.length === 0 ? (
                                <TableRow>
                                    <TableCell colSpan={4} className="h-24 text-center">
                                        {t('common.no_results', 'No results found.')}
                                    </TableCell>
                                </TableRow>
                            ) : (
                                filteredTypes.map((type) => (
                                    <TableRow key={type.id}>
                                        <TableCell className="font-medium">
                                            <div className="flex items-center">
                                                <Shield className="mr-2 h-4 w-4 text-muted-foreground" />
                                                {type.name}
                                            </div>
                                        </TableCell>
                                        <TableCell>{type.code}</TableCell>
                                        <TableCell>{type.description || "-"}</TableCell>
                                        <TableCell className="text-right font-mono text-xs text-muted-foreground">
                                            {type.id.substring(0, 8)}...
                                        </TableCell>
                                    </TableRow>
                                ))
                            )}
                        </TableBody>
                    </Table>
                </CardContent>
            </Card>
        </div>
    );
}
