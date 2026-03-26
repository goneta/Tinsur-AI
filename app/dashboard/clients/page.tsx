/**
 * Client list page with data table.
 */
'use client';

import { useState, useEffect, useMemo, useCallback } from 'react';
import { useRouter } from 'next/navigation';
import { clientApi } from '@/lib/client-api';
// Client type is imported from columns as well, but let's check conflict.
// Original file imported Client from '@/types/client'.
// My bad edit added import { columns as getColumns, Client } from './columns';
// I should stick to one. columns usually exports Client type if it's defined there, or I import from types.
// I'll import Shared Client type if possible.
import { Client } from '@/types/client';
import { Button } from '@/components/ui/button';
import { Plus, Search, Eye, Filter, Loader2, Camera, Pencil, MapPin } from 'lucide-react';
import { UnifiedEntityForm } from '@/components/shared/unified-entity-form';
import { DeleteClientDialog } from '@/components/clients/delete-client-dialog';
import { Input } from '@/components/ui/input';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { api, getProfileImageUrl } from '@/lib/api';
import { useToast } from '@/components/ui/use-toast';
import { ClientProfilePicture } from '@/components/clients/client-profile-picture';
import { DataView } from '@/components/ui/data-view';
import { columns as getColumns } from './columns';
import { UserAvatar } from '@/components/shared/user-avatar';
import { ProfileUploader } from '@/components/shared/profile-uploader';
import { useLanguage } from '@/contexts/language-context';

export default function ClientsPage() {
    const router = useRouter();
    const { t } = useLanguage();
    const [clients, setClients] = useState<Client[]>([]);
    const [loading, setLoading] = useState(true);
    const [isAddingClient, setIsAddingClient] = useState(false);
    const [editingClient, setEditingClient] = useState<Client | null>(null);
    const [deletingClient, setDeletingClient] = useState<Client | null>(null);
    const [viewMode, setViewMode] = useState<'card' | 'list'>('card');
    const [searchTerm, setSearchTerm] = useState('');
    const [mounted, setMounted] = useState(false);
    const { toast } = useToast();

    useEffect(() => {
        setMounted(true);
        loadClients();
    }, []);

    const loadClients = async () => {
        setLoading(true);
        try {
            const data = await clientApi.getClients({ page_size: 1000 });
            setClients(data);
        } catch (error) {
            console.error('Failed to load clients:', error);
        } finally {
            setLoading(false);
        }
    };

    const handleClientCreated = () => {
        setIsAddingClient(false);
        setTimeout(() => loadClients(), 100);
    };

    const handleClientUpdated = () => {
        setEditingClient(null);
        setTimeout(() => loadClients(), 100);
    };

    const handleClientDeleted = () => {
        setDeletingClient(null);
        setTimeout(() => loadClients(), 100);
    };

    const filteredClients = clients.filter(client => {
        if (!searchTerm) return true;
        const term = searchTerm.toLowerCase();
        const fullName = `${client.first_name || ''} ${client.last_name || ''}`.toLowerCase();
        const businessName = (client.business_name || '').toLowerCase();
        return (
            fullName.includes(term) ||
            businessName.includes(term) ||
            client.email?.toLowerCase().includes(term) ||
            client.phone_number?.includes(term) ||
            client.city?.toLowerCase().includes(term)
        );
    });


    const memoColumns = useMemo(() =>
        getColumns(setEditingClient, setDeletingClient, loadClients, t),
        [setEditingClient, setDeletingClient, t]);

    const renderClientCard = useCallback((client: Client) => (
        <Card className="relative overflow-hidden hover:shadow-md transition-shadow">
            <div className="absolute top-2 right-2 flex items-center gap-1 z-10">
                <Button
                    variant="ghost"
                    size="icon"
                    className="h-8 w-8 text-muted-foreground hover:text-foreground"
                    onClick={() => router.push(`/dashboard/clients/${client.id}`)}
                    title={t('clients.action_view')}
                >
                    <Eye className="h-4 w-4" />
                </Button>
                <Button
                    variant="ghost"
                    size="icon"
                    className="h-8 w-8 text-muted-foreground hover:text-foreground"
                    onClick={() => setEditingClient(client)}
                    title={t('clients.edit_client', 'Edit Client')}
                >
                    <Pencil className="h-4 w-4" />
                </Button>
            </div>
            <CardHeader className="flex flex-col items-center gap-4 bg-muted/20 p-6 pb-2">
                <ProfileUploader
                    entityId={client.id}
                    entityType="client"
                    currentImageUrl={client.profile_picture}
                    name={`${client.first_name} ${client.last_name}`}
                    className="h-20 w-20 border-4 border-white shadow-sm"
                    size="lg"
                    onUploadSuccess={loadClients}
                />
                <div className="text-center grid gap-1 w-full mt-4">
                    <CardTitle className="text-xl truncate">{client.first_name} {client.last_name}</CardTitle>
                    <div className="text-sm text-muted-foreground break-all px-4">{client.email}</div>
                </div>
            </CardHeader>
            <CardContent className="p-6 grid gap-3 pt-4">
                <div className="flex items-center justify-between text-sm py-1 border-b">
                    <span className="text-muted-foreground">{t('clients.phone')}</span>
                    <span>{client.phone_number}</span>
                </div>
                <div className="flex items-center justify-between text-sm py-1 border-b">
                    <span className="text-muted-foreground">{t('clients.status')}</span>
                    <span className={`px-2 py-0.5 rounded-full text-xs font-medium ${client.status === 'active' ? 'bg-green-100 text-green-700' : 'bg-gray-100 text-gray-700'
                        }`}>
                        {client.status === 'active' ? t('clients.status_active') : client.status}
                    </span>
                </div>
                <div className="flex items-center justify-between text-sm py-1 border-b">
                    <span className="text-muted-foreground">{t('clients.type')}</span>
                    <span className="capitalize">{client.client_type === 'individual' ? t('clients.type_individual') : client.client_type}</span>
                </div>
            </CardContent>
        </Card>
    ), [router, loadClients, setEditingClient, t]);

    if (!mounted) return null;

    return (
        <div className="flex-1 space-y-4 p-8 pt-6">
            <div className="flex items-center justify-between">
                <div>
                    <h2 className="text-3xl font-bold tracking-tight">{t('clients.title')}</h2>
                    <p className="text-muted-foreground">{t('clients.desc')}</p>
                </div>
                <div className="flex items-center gap-2">
                    {!isAddingClient && !editingClient && (
                        <Button onClick={() => setIsAddingClient(true)}>
                            <Plus className="mr-2 h-4 w-4" />
                            {t('clients.new_client')}
                        </Button>
                    )}
                </div>
            </div>

            {isAddingClient || editingClient ? (
                <UnifiedEntityForm
                    type="client"
                    mode={isAddingClient ? 'create' : 'edit'}
                    entity={editingClient || {}}
                    onUpdate={isAddingClient ? handleClientCreated : handleClientUpdated}
                    onBack={() => {
                        setIsAddingClient(false);
                        setEditingClient(null);
                    }}
                />
            ) : (
                <DataView
                    columns={memoColumns}
                    data={clients}
                    renderCard={renderClientCard}
                    defaultView="card"
                    getRowId={(row) => row.id}
                />
            )}

            <DeleteClientDialog
                open={!!deletingClient}
                onOpenChange={(open) => !open && setDeletingClient(null)}
                client={deletingClient || undefined}
                onSuccess={handleClientDeleted}
            />
        </div>
    );
}
