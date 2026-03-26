'use client';

import { useState, useEffect, Suspense } from 'react';
import { useSearchParams } from 'next/navigation';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs';
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from "@/components/ui/table";
import { Badge } from "@/components/ui/badge";
import { formatCurrency } from "@/lib/utils";
import { referralApi, Referral, ReferralStats } from "@/lib/referral-api";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Share2, FileText, Download, Trash2, Eye, Shield, UserPlus, Users2, Coins } from 'lucide-react';
import { DocumentUpload } from '@/components/collaboration/document-upload';
import { ShareModal } from '@/components/collaboration/share-modal';
import { SharingSettings, SharingConfig } from '@/components/collaboration/sharing-settings';
import { NetworkSettlements } from '@/components/collaboration/network-settlements';
import {
    Dialog,
    DialogContent,
    DialogDescription,
    DialogHeader,
    DialogTitle,
    DialogTrigger,
    DialogFooter,
} from "@/components/ui/dialog"
import { api } from '@/lib/api';
import { useToast } from "@/components/ui/use-toast"; // Assuming toast hook exists
import { useLanguage } from '@/contexts/language-context';

import { collaborationService, DocumentData } from '@/services/collaborationService';

function CollaborationContent() {
    const { t, language } = useLanguage();
    const searchParams = useSearchParams();
    const tabParam = searchParams.get('tab');
    const [activeTab, setActiveTab] = useState(tabParam || "my-docs");
    const [isUploadOpen, setIsUploadOpen] = useState(false);
    const [editingShareDoc, setEditingShareDoc] = useState<DocumentData | null>(null);
    const [tempShareConfig, setTempShareConfig] = useState<SharingConfig | null>(null);

    // Referral State
    const [referralStats, setReferralStats] = useState<ReferralStats | null>(null);
    const [referralsList, setReferralsList] = useState<Referral[]>([]);

    useEffect(() => {
        if (tabParam) {
            setActiveTab(tabParam);
        }
    }, [tabParam]);
    const [isLoading, setIsLoading] = useState(true);
    // const { toast } = useToast(); 

    const [myDocs, setMyDocs] = useState<DocumentData[]>([]);
    const [publicDocs, setPublicDocs] = useState<DocumentData[]>([]);
    const [sharedWithMe, setSharedWithMe] = useState<DocumentData[]>([]);

    const fetchDocuments = async () => {
        try {
            setIsLoading(true);
            const data = await collaborationService.getDocuments();
            setMyDocs(data.my_docs);
            setPublicDocs(data.public_docs);
            setSharedWithMe(data.shared_with_me);
        } catch (error) {
            console.error("Failed to fetch documents", error);
        } finally {
            setIsLoading(false);
        }
    };

    useEffect(() => {
        fetchDocuments();
        fetchReferrals();
    }, []);

    const fetchReferrals = async () => {
        try {
            const stats = await referralApi.getStats();
            setReferralStats(stats);
            const list = await referralApi.getReferrals();
            setReferralsList(list);
        } catch (error) {
            console.error("Failed to fetch referrals", error);
        }
    };

    const handleUpload = async (file: File, label: string): Promise<void> => {
        try {
            const res = await collaborationService.uploadDocument(file, label);

            // Proactively update state before refetching
            if (res.document) {
                setMyDocs(prev => [res.document, ...prev]);
            }

            // Wait for upload to finish before closing
            setIsUploadOpen(false);

            // Still refresh to ensure consistency
            setTimeout(() => fetchDocuments(), 500);
        } catch (error) {
            console.error("Upload failed", error);
            alert("Upload failed: " + (error as any).message);
            throw error;
        }
    };

    const handleShareConfigChange = (config: SharingConfig) => {
        setTempShareConfig(config);
    };

    const handleSaveChanges = async () => {
        if (!editingShareDoc || !tempShareConfig) return;

        try {
            const payload = {
                visibility: tempShareConfig.visibility,
                scope: tempShareConfig.scope,
                is_shareable: tempShareConfig.isShareable,
                reshare_rule: tempShareConfig.reshareRule
            };

            await api.post(`/documents/${editingShareDoc.id}/share`, payload);

            setEditingShareDoc(null);
            setTempShareConfig(null);
            fetchDocuments();
        } catch (error) {
            console.error("Share update failed", error);
            alert("Failed to update share settings");
        }
    };

    const getTranslatedLabel = (label: string) => {
        if (label === 'Car Papers') return t('collaboration.doc_types.car_papers');
        if (label === 'Photo') return t('collaboration.doc_types.photo');
        return label;
    }

    const getTranslatedVisibility = (visibility: string) => {
        if (visibility === 'PUBLIC') return t('collaboration_hub.public', 'PUBLIC');
        if (visibility === 'PRIVATE') return t('collaboration_hub.private', 'PRIVATE');
        return visibility;
    }

    return (
        <div className="flex-1 space-y-4 p-4 md:p-8 pt-6">
            <div className="flex items-center justify-between">
                <div>
                    <h2 className="text-3xl font-bold tracking-tight">{t('collaboration_hub.title')}</h2>
                    <p className="text-muted-foreground">{t('collaboration_hub.description')}</p>
                </div>
                <Dialog open={isUploadOpen} onOpenChange={setIsUploadOpen}>
                    <DialogTrigger asChild>
                        <Button>
                            <Share2 className="mr-2 h-4 w-4" /> {t('collaboration_hub.upload_share')}
                        </Button>
                    </DialogTrigger>
                    <DialogContent className="sm:max-w-[500px]">
                        <DialogHeader>
                            <DialogTitle>Upload New Document</DialogTitle>
                            <DialogDescription>
                                Select a file and assign a label to start.
                            </DialogDescription>
                        </DialogHeader>
                        <DocumentUpload onUpload={handleUpload} />
                    </DialogContent>
                </Dialog>
            </div>

            <Tabs value={activeTab} onValueChange={setActiveTab} className="space-y-4">
                <TabsList className="grid w-full grid-cols-2 lg:grid-cols-5 gap-2 h-auto bg-transparent p-0">
                    <TabsTrigger value="my-docs" className="data-[state=active]:bg-sidebar-accent data-[state=active]:text-sidebar-accent-foreground border py-2 flex items-center gap-2">
                        <FileText className="h-4 w-4" /> {t('collaboration_hub.my_documents', 'My Documents')}
                    </TabsTrigger>
                    <TabsTrigger value="shared-with-me" className="data-[state=active]:bg-sidebar-accent data-[state=active]:text-sidebar-accent-foreground border py-2 flex items-center gap-2">
                        <Shield className="h-4 w-4" /> {t('collaboration_hub.shared_with_me', 'Shared with Me')}
                    </TabsTrigger>
                    <TabsTrigger value="public" className="data-[state=active]:bg-sidebar-accent data-[state=active]:text-sidebar-accent-foreground border py-2 flex items-center gap-2">
                        <Eye className="h-4 w-4" /> {t('collaboration_hub.public_dataset', 'Public Dataset')}
                    </TabsTrigger>
                    <TabsTrigger value="referrals" className="data-[state=active]:bg-sidebar-accent data-[state=active]:text-sidebar-accent-foreground border py-2 flex items-center gap-2">
                        <UserPlus className="h-4 w-4" /> {t('collaboration_hub.referrals', 'Referrals')}
                    </TabsTrigger>
                    <TabsTrigger value="settlements" className="data-[state=active]:bg-sidebar-accent data-[state=active]:text-sidebar-accent-foreground border py-2 flex items-center gap-2">
                        <Coins className="h-4 w-4" /> {t('collaboration_hub.network_settlements', 'Network Settlements')}
                    </TabsTrigger>
                </TabsList>

                {/* MY DOCUMENTS TAB */}
                <TabsContent value="my-docs" className="space-y-4">
                    <Card>
                        <CardHeader>
                            <CardTitle>{t('collaboration_hub.my_documents', 'My Documents')}</CardTitle>
                            <CardDescription>{t('collaboration_hub.my_docs_desc', 'Manage files you own...')}</CardDescription>
                        </CardHeader>
                        <CardContent>
                            <div className="space-y-4">
                                {myDocs.length === 0 ? (
                                    <div className="text-center py-10 text-muted-foreground">{t('collaboration_hub.no_documents')}</div>
                                ) : (
                                    myDocs.map((doc) => (
                                        <div key={doc.id} className="flex items-center justify-between p-4 border rounded-lg bg-card hover:bg-muted/30 transition">
                                            <div className="flex items-center gap-4">
                                                <div className="h-10 w-10 rounded bg-blue-100 flex items-center justify-center text-blue-600">
                                                    <FileText className="h-5 w-5" />
                                                </div>
                                                <div>
                                                    <p className="font-medium">{doc.name}</p>
                                                    <div className="flex items-center gap-2 text-sm text-muted-foreground">
                                                        <Badge variant="outline">{getTranslatedLabel(doc.label)}</Badge>
                                                        <span>{doc.size}</span>
                                                        <span>•</span>
                                                        <span>{doc.date}</span>
                                                    </div>
                                                </div>
                                            </div>

                                            <div className="flex items-center gap-2">
                                                <div className="flex flex-col items-end mr-4">
                                                    <Badge variant={doc.visibility === 'PUBLIC' ? 'default' : 'secondary'} className="mb-1">
                                                        {getTranslatedVisibility(doc.visibility)}
                                                    </Badge>
                                                    {doc.visibility === 'PRIVATE' && doc.scope && (
                                                        <span className="text-xs text-muted-foreground font-mono">{doc.scope}</span>
                                                    )}
                                                </div>

                                                <Button variant="outline" size="sm" onClick={() => setEditingShareDoc(doc)}>
                                                    <Share2 className="h-4 w-4 mr-2" /> {t('collaboration_hub.share', 'Share')}
                                                </Button>

                                                <Button variant="ghost" size="icon" className="text-red-500 hover:text-red-700">
                                                    <Trash2 className="h-4 w-4" />
                                                </Button>
                                            </div>
                                        </div>
                                    ))
                                )}
                            </div>
                        </CardContent>
                    </Card>
                </TabsContent>

                {/* SHARED WITH ME TAB */}
                <TabsContent value="shared-with-me" className="space-y-4">
                    <Card>
                        <CardHeader>
                            <CardTitle>{t('collaboration_hub.shared_with_me')}</CardTitle>
                            <CardDescription>{t('collaboration_hub.shared_with_me_desc')}</CardDescription>
                        </CardHeader>
                        <CardContent>
                            <div className="space-y-4">
                                {sharedWithMe.map((doc) => (
                                    <div key={doc.id} className="flex items-center justify-between p-4 border rounded-lg">
                                        <div className="flex items-center gap-4">
                                            <div className="h-10 w-10 rounded bg-green-100 flex items-center justify-center text-green-600">
                                                <Shield className="h-5 w-5" />
                                            </div>
                                            <div>
                                                <p className="font-medium">{doc.name}</p>
                                                <p className="text-sm text-muted-foreground">
                                                    Shared by <span className="font-semibold">{doc.owner}</span> • {doc.scope}
                                                </p>
                                            </div>
                                        </div>
                                        <Button variant="outline" size="sm">
                                            <Download className="h-4 w-4 mr-2" /> Download
                                        </Button>
                                    </div>
                                ))}
                            </div>
                        </CardContent>
                    </Card>
                </TabsContent>

                {/* PUBLIC DATASET TAB */}
                <TabsContent value="public" className="space-y-4">
                    <Card>
                        <CardHeader>
                            <CardTitle>{t('collaboration_hub.public_dataset')}</CardTitle>
                            <CardDescription>{t('collaboration_hub.public_dataset_desc')}</CardDescription>
                        </CardHeader>
                        <CardContent>
                            <div className="space-y-4">
                                {publicDocs.map((doc) => (
                                    <div key={doc.id} className="flex items-center justify-between p-4 border rounded-lg">
                                        <div className="flex items-center gap-4">
                                            <div className="h-10 w-10 rounded bg-purple-100 flex items-center justify-center text-purple-600">
                                                <Eye className="h-5 w-5" />
                                            </div>
                                            <div>
                                                <p className="font-medium">{doc.name}</p>
                                                <p className="text-sm text-muted-foreground">
                                                    Published by {doc.owner}
                                                </p>
                                            </div>
                                        </div>
                                        <Button variant="outline" size="sm">
                                            <Download className="h-4 w-4 mr-2" /> Download
                                        </Button>
                                    </div>
                                ))}
                            </div>
                        </CardContent>
                    </Card>
                </TabsContent>

                {/* REFERRALS TAB */}
                <TabsContent value="referrals" className="space-y-4">
                    <Card>
                        <CardHeader>
                            <CardTitle>Referral Program</CardTitle>
                            <CardDescription>
                                Track client referrals and rewards.
                            </CardDescription>
                        </CardHeader>
                        <CardContent>
                            <div className="flex items-center gap-4 mb-6">
                                <div className="p-4 bg-muted rounded-lg">
                                    <p className="text-sm font-medium">Total Rewards Paid</p>
                                    <p className="text-2xl font-bold">{formatCurrency(referralStats?.total_rewards || 0)}</p>
                                </div>
                                <div className="p-4 bg-muted rounded-lg">
                                    <p className="text-sm font-medium">Pending Conversions</p>
                                    <p className="text-2xl font-bold">{referralStats?.pending_conversions || 0}</p>
                                </div>
                                <div className="p-4 bg-muted rounded-lg">
                                    <p className="text-sm font-medium">Total Converted</p>
                                    <p className="text-2xl font-bold">{referralStats?.converted_count || 0}</p>
                                </div>
                            </div>

                            <div className="rounded-md border">
                                <Table>
                                    <TableHeader>
                                        <TableRow>
                                            <TableHead>Code</TableHead>
                                            <TableHead>Status</TableHead>
                                            <TableHead>Reward</TableHead>
                                            <TableHead>Created</TableHead>
                                        </TableRow>
                                    </TableHeader>
                                    <TableBody>
                                        {referralsList.length === 0 ? (
                                            <TableRow>
                                                <TableCell colSpan={4} className="h-24 text-center">
                                                    No referrals found.
                                                </TableCell>
                                            </TableRow>
                                        ) : (
                                            referralsList.map((ref) => (
                                                <TableRow key={ref.id}>
                                                    <TableCell className="font-mono">{ref.referral_code}</TableCell>
                                                    <TableCell>
                                                        <Badge variant={
                                                            ref.status === 'converted' ? 'default' :
                                                                ref.status === 'pending' ? 'secondary' : 'outline'
                                                        }>
                                                            {ref.status}
                                                        </Badge>
                                                    </TableCell>
                                                    <TableCell>{ref.reward_amount ? formatCurrency(ref.reward_amount) : '-'}</TableCell>
                                                    <TableCell>{new Date(ref.created_at).toLocaleDateString()}</TableCell>
                                                </TableRow>
                                            ))
                                        )}
                                    </TableBody>
                                </Table>
                            </div>
                        </CardContent>
                    </Card>
                </TabsContent>

                {/* NETWORK SETTLEMENTS TAB */}
                <TabsContent value="settlements" className="space-y-4">
                    <NetworkSettlements />
                </TabsContent>
            </Tabs>

            <ShareModal
                open={!!editingShareDoc}
                onOpenChange={(open) => !open && setEditingShareDoc(null)}
                documentName={editingShareDoc?.name}
                documentId={editingShareDoc?.id}
                initialConfig={editingShareDoc ? {
                    visibility: editingShareDoc.visibility,
                    scope: editingShareDoc.scope as any,
                    isShareable: editingShareDoc.isShareable,
                    reshareRule: editingShareDoc.reshareRule
                } : undefined}
                onSave={async (config, recipientIds) => {
                    if (!editingShareDoc) return;

                    try {
                        const payload = {
                            visibility: config.visibility,
                            scope: config.scope,
                            is_shareable: config.isShareable,
                            reshare_rule: config.reshareRule,
                            recipient_ids: recipientIds
                        };

                        await api.post(`/documents/${editingShareDoc.id}/share`, payload);

                        setEditingShareDoc(null);
                        setTempShareConfig(null);
                        fetchDocuments();

                        // toast({ title: "Success", description: "Share settings updated" }); // handled in modal or here? 
                        // Modal handles generic success if no onSave provided. If onSave provided, modal awaits it.
                        // But since we provided onSave, we should probably handle toast here or let modal fallback?
                        // The Modal implementation waits for this promise. 
                    } catch (error) {
                        console.error("Share update failed", error);
                        alert("Failed to update share settings");
                        throw error; // Re-throw to let modal know it failed
                    }
                }}
            />
        </div>
    );
}

export default function CollaborationPage() {
    return (
        <Suspense fallback={<div>Loading collaboration...</div>}>
            <CollaborationContent />
        </Suspense>
    );
}
