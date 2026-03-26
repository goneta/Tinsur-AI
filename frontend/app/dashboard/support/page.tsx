'use client';

import Link from 'next/link';
import { useState, useEffect } from 'react';
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Plus, MessageSquare, Search, Filter } from 'lucide-react';
import { Input } from '@/components/ui/input';
import { Badge } from '@/components/ui/badge';
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from "@/components/ui/table";
import { Dialog, DialogContent, DialogHeader, DialogTitle, DialogDescription, DialogFooter } from "@/components/ui/dialog";
import { Textarea } from "@/components/ui/textarea";
import { ticketsApi, Ticket, TicketMessage } from '@/lib/tickets-api';
import { format } from 'date-fns';

import { useLanguage } from '@/contexts/language-context';

export default function SupportPage() {
    const { t } = useLanguage();
    const [tickets, setTickets] = useState<Ticket[]>([]);
    const [loading, setLoading] = useState(true);
    const [selectedTicket, setSelectedTicket] = useState<Ticket | null>(null);
    const [replyText, setReplyText] = useState("");
    const [isInternal, setIsInternal] = useState(false);
    const [sending, setSending] = useState(false);

    useEffect(() => {
        fetchTickets();
    }, []);

    const fetchTickets = async () => {
        setLoading(true);
        try {
            const data = await ticketsApi.getTickets();
            setTickets(data);
        } catch (error) {
            console.error(error);
        } finally {
            setLoading(false);
        }
    };

    const handleOpenTicket = async (ticket: Ticket) => {
        // Fetch full details including messages
        try {
            const fullTicket = await ticketsApi.getTicket(ticket.id);
            setSelectedTicket(fullTicket);
        } catch (error) {
            console.error(error);
        }
    };

    const handleReply = async () => {
        if (!selectedTicket || !replyText.trim()) return;
        setSending(true);
        try {
            await ticketsApi.replyTicket(selectedTicket.id, {
                message: replyText,
                is_internal: isInternal
            });
            // Refresh conversation
            const updated = await ticketsApi.getTicket(selectedTicket.id);
            setSelectedTicket(updated);
            setReplyText("");
            // Update list as well to reflect status change if any
            fetchTickets();
        } catch (error) {
            console.error(error);
        } finally {
            setSending(false);
        }
    };

    const getStatusColor = (status: string) => {
        switch (status) {
            case 'open': return 'default';
            case 'in_progress': return 'secondary';
            case 'resolved': return 'success'; // Assuming success variant exists or default to green-ish
            case 'closed': return 'outline';
            default: return 'outline';
        }
    };

    return (
        <div className="flex-1 space-y-4 p-4 md:p-8 pt-6">
            <div className="flex items-center justify-between">
                <div>
                    <h2 className="text-3xl font-bold tracking-tight">{t('support.title')}</h2>
                    <p className="text-muted-foreground">{t('support.desc')}</p>
                </div>
                <div className="flex items-center space-x-2">
                    <Button variant="outline" asChild>
                        <Link href="/dashboard/support/cancellation-guide">Guide de Résiliation (FR)</Link>
                    </Button>
                    {/* <Button>
                        <Plus className="mr-2 h-4 w-4" /> New Ticket
                    </Button> */}
                </div>
            </div>

            <Card>
                <CardHeader>
                    <div className="flex items-center justify-between">
                        <CardTitle>{t('support.recent_tickets')}</CardTitle>
                        <div className="flex gap-2">
                            <Input placeholder={t('support.search_placeholder', 'Search tickets...')} className="w-[200px]" />
                        </div>
                    </div>
                </CardHeader>
                <CardContent>
                    <Table>
                        <TableHeader>
                            <TableRow>
                                <TableHead>{t('support.ticket_id')}</TableHead>
                                <TableHead>{t('support.subject')}</TableHead>
                                <TableHead>{t('support.category')}</TableHead>
                                <TableHead>{t('support.status')}</TableHead>
                                <TableHead>{t('support.created')}</TableHead>
                                <TableHead>{t('support.action')}</TableHead>
                            </TableRow>
                        </TableHeader>
                        <TableBody>
                            {loading ? (
                                <TableRow>
                                    <TableCell colSpan={6} className="text-center h-24">{t('common.loading')}</TableCell>
                                </TableRow>
                            ) : tickets.length === 0 ? (
                                <TableRow>
                                    <TableCell colSpan={6} className="text-center h-24">{t('support.no_tickets')}</TableCell>
                                </TableRow>
                            ) : (
                                tickets.map((ticket) => (
                                    <TableRow key={ticket.id}>
                                        <TableCell className="font-mono text-xs">{ticket.ticket_number}</TableCell>
                                        <TableCell className="font-medium">{ticket.subject}</TableCell>
                                        <TableCell className="capitalize">{ticket.category}</TableCell>
                                        <TableCell>
                                            <Badge variant={ticket.status === 'open' ? 'destructive' : 'outline'}>
                                                {ticket.status}
                                            </Badge>
                                        </TableCell>
                                        <TableCell>{format(new Date(ticket.created_at), 'MMM d, yyyy')}</TableCell>
                                        <TableCell>
                                            <Button variant="ghost" size="sm" onClick={() => handleOpenTicket(ticket)}>
                                                {t('support.view')}
                                            </Button>
                                        </TableCell>
                                    </TableRow>
                                ))
                            )}
                        </TableBody>
                    </Table>
                </CardContent>
            </Card>

            <Dialog open={!!selectedTicket} onOpenChange={(open) => !open && setSelectedTicket(null)}>
                <DialogContent className="max-w-2xl max-h-[85vh] flex flex-col">
                    <DialogHeader>
                        <DialogTitle className="flex justify-between items-center mr-8">
                            <span>{selectedTicket?.subject}</span>
                            <Badge variant="outline">{selectedTicket?.status}</Badge>
                        </DialogTitle>
                        <DialogDescription>
                            Ticket #{selectedTicket?.ticket_number} • {selectedTicket?.category}
                        </DialogDescription>
                    </DialogHeader>

                    <div className="flex-1 overflow-y-auto p-4 border rounded-md bg-slate-50 space-y-4">
                        <div className="bg-white p-3 rounded shadow-sm border">
                            <p className="text-sm font-semibold text-slate-700">{t('support.description')}</p>
                            <p className="text-sm mt-1">{selectedTicket?.description}</p>
                        </div>

                        {selectedTicket?.messages?.map((msg) => (
                            <div key={msg.id} className={`flex flex-col ${msg.sender_type === 'user' ? 'items-end' : 'items-start'}`}>
                                <div className={`max-w-[80%] p-3 rounded-lg text-sm ${msg.is_internal ? 'bg-yellow-50 border border-yellow-200' :
                                    msg.sender_type === 'user' ? 'bg-blue-600 text-white' : 'bg-white border'
                                    }`}>
                                    {msg.is_internal && <p className="text-[10px] font-bold text-yellow-700 mb-1">{t('support.internal_note')}</p>}
                                    <p>{msg.message}</p>
                                    <p className={`text-[10px] mt-1 ${msg.sender_type === 'user' ? 'text-blue-100' : 'text-slate-400'}`}>
                                        {format(new Date(msg.created_at), 'MMM d, HH:mm')}
                                    </p>
                                </div>
                            </div>
                        ))}
                    </div>

                    <div className="pt-4 space-y-3">
                        <Textarea
                            placeholder={t('support.type_reply')}
                            value={replyText}
                            onChange={(e) => setReplyText(e.target.value)}
                        />
                        <div className="flex justify-between items-center">
                            <label className="flex items-center space-x-2 text-sm">
                                <input
                                    type="checkbox"
                                    checked={isInternal}
                                    onChange={(e) => setIsInternal(e.target.checked)}
                                    className="rounded border-gray-300"
                                />
                                <span>{t('support.internal_note')}</span>
                            </label>
                            <Button onClick={handleReply} disabled={sending}>
                                {sending ? t('support.sending') : t('support.send_reply')}
                            </Button>
                        </div>
                    </div>
                </DialogContent>
            </Dialog>
        </div>
    );
}
