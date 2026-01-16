'use client';

import Link from 'next/link';
import { useState, useEffect } from 'react';
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Plus, MessageSquare, Loader2, Sparkles } from 'lucide-react';
import { Input } from '@/components/ui/input';
import { Badge } from '@/components/ui/badge';
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from "@/components/ui/table";
import { Dialog, DialogContent, DialogHeader, DialogTitle, DialogDescription, DialogFooter, DialogTrigger } from "@/components/ui/dialog";
import { Textarea } from "@/components/ui/textarea";
import { Label } from "@/components/ui/label";
import {
    Select,
    SelectContent,
    SelectItem,
    SelectTrigger,
    SelectValue,
} from "@/components/ui/select"
import { portalApi, Ticket } from '@/lib/portal-api';
import { SupportChatWidget } from '@/components/support/support-chat-widget';

export default function ClientSupportPage() {
    const [tickets, setTickets] = useState<Ticket[]>([]);
    const [loading, setLoading] = useState(true);
    const [selectedTicket, setSelectedTicket] = useState<Ticket | null>(null);
    const [replyText, setReplyText] = useState("");
    const [sending, setSending] = useState(false);

    // New Ticket State
    const [isNewOpen, setIsNewOpen] = useState(false);
    const [newTicket, setNewTicket] = useState({
        subject: "",
        category: "general",
        description: "",
        priority: "medium"
    });

    useEffect(() => {
        fetchTickets();
    }, []);

    const fetchTickets = async () => {
        setLoading(true);
        try {
            const data = await portalApi.getTickets();
            setTickets(data);
        } catch (error) {
            console.error(error);
        } finally {
            setLoading(false);
        }
    };

    const handleOpenTicket = async (ticket: Ticket) => {
        try {
            const fullTicket = await portalApi.getTicket(ticket.id);
            setSelectedTicket(fullTicket);
        } catch (error) {
            console.error(error);
        }
    };

    const handleReply = async () => {
        if (!selectedTicket || !replyText.trim()) return;
        setSending(true);
        try {
            await portalApi.replyTicket(selectedTicket.id, {
                message: replyText
            });
            const updated = await portalApi.getTicket(selectedTicket.id);
            setSelectedTicket(updated);
            setReplyText("");
            fetchTickets();
        } catch (error) {
            console.error(error);
        } finally {
            setSending(false);
        }
    };

    const handleCreateTicket = async () => {
        if (!newTicket.subject || !newTicket.description) return;
        setSending(true);
        try {
            await portalApi.createTicket(newTicket);
            setIsNewOpen(false);
            setNewTicket({ subject: "", category: "general", description: "", priority: "medium" });
            fetchTickets();
        } catch (error) {
            console.error(error);
        } finally {
            setSending(false);
        }
    }

    const formatDate = (dateString: string) => {
        return new Date(dateString).toLocaleDateString('en-US', {
            year: 'numeric',
            month: 'short',
            day: 'numeric',
            hour: '2-digit',
            minute: '2-digit'
        });
    }

    return (
        <div className="max-w-[1700px] mx-auto flex-1 space-y-8 pt-6 pb-20">
            <div className="flex flex-col md:flex-row md:items-end justify-between gap-4">
                <div>
                    <h2 className="text-2xl font-extrabold tracking-tight text-slate-900">Support Center</h2>
                    <p className="text-slate-500 mt-1 text-lg">Instant AI assistance and ticket management.</p>
                </div>

                <div className="flex gap-2">
                    <Button variant="outline" className="border-slate-200 hover:bg-slate-50" asChild>
                        <Link href="/portal/support/cancellation-guide">Guide de Résiliation (FR)</Link>
                    </Button>

                    <Dialog open={isNewOpen} onOpenChange={setIsNewOpen}>
                        <DialogTrigger asChild>
                            <Button variant="outline" className="border-slate-200 hover:bg-slate-50 font-semibold shadow-sm">
                                <Plus className="mr-2 h-4 w-4" /> Traditional Ticket
                            </Button>
                        </DialogTrigger>
                        <DialogContent>
                            <DialogHeader>
                                <DialogTitle>Create New Support Ticket</DialogTitle>
                                <DialogDescription>Describe your issue and we'll get back to you asap.</DialogDescription>
                            </DialogHeader>
                            <div className="grid gap-4 py-4">
                                <div className="grid gap-2">
                                    <Label htmlFor="subject">Subject</Label>
                                    <Input
                                        id="subject"
                                        placeholder="Brief summary of the issue"
                                        value={newTicket.subject}
                                        onChange={(e) => setNewTicket({ ...newTicket, subject: e.target.value })}
                                    />
                                </div>
                                <div className="grid gap-2">
                                    <Label htmlFor="category">Category</Label>
                                    <Select
                                        value={newTicket.category}
                                        onValueChange={(val) => setNewTicket({ ...newTicket, category: val })}
                                    >
                                        <SelectTrigger>
                                            <SelectValue placeholder="Select category" />
                                        </SelectTrigger>
                                        <SelectContent>
                                            <SelectItem value="general">General Inquiry</SelectItem>
                                            <SelectItem value="billing">Billing & Payments</SelectItem>
                                            <SelectItem value="technical">Technical Issue</SelectItem>
                                            <SelectItem value="claim">Claims Support</SelectItem>
                                        </SelectContent>
                                    </Select>
                                </div>
                                <div className="grid gap-2">
                                    <Label htmlFor="description">Description</Label>
                                    <Textarea
                                        id="description"
                                        placeholder="Detailed explanation..."
                                        rows={4}
                                        value={newTicket.description}
                                        onChange={(e) => setNewTicket({ ...newTicket, description: e.target.value })}
                                    />
                                </div>
                            </div>
                            <DialogFooter>
                                <Button onClick={handleCreateTicket} disabled={sending} className="bg-blue-600 hover:bg-blue-700">
                                    {sending ? 'Creating...' : 'Submit Ticket'}
                                </Button>
                            </DialogFooter>
                        </DialogContent>
                    </Dialog>
                </div>
            </div>

            <div className="grid grid-cols-12 gap-6">
                {/* AI Chat Widget - Primary focus */}
                <div className="col-span-12 lg:col-span-5 order-2 lg:order-1">
                    <SupportChatWidget />
                </div>

                {/* Ticket List - Secondary/History */}
                <div className="col-span-12 lg:col-span-7 space-y-6 order-1 lg:order-2">
                    <Card className="border-slate-200 shadow-md">
                        <CardHeader className="flex flex-row items-center justify-between space-y-0">
                            <div>
                                <CardTitle className="text-xl">Your Open Cases</CardTitle>
                                <CardDescription>Track the status of your reported issues.</CardDescription>
                            </div>
                            <Badge variant="secondary" className="bg-slate-100 font-bold px-3 py-1">
                                {tickets.length} Total
                            </Badge>
                        </CardHeader>
                        <CardContent>
                            <Table>
                                <TableHeader>
                                    <TableRow className="hover:bg-transparent border-slate-100">
                                        <TableHead className="font-bold">ID</TableHead>
                                        <TableHead className="font-bold">Subject</TableHead>
                                        <TableHead className="font-bold">Status</TableHead>
                                        <TableHead className="text-right font-bold">Action</TableHead>
                                    </TableRow>
                                </TableHeader>
                                <TableBody>
                                    {loading ? (
                                        <TableRow>
                                            <TableCell colSpan={4} className="text-center h-32">
                                                <Loader2 className="h-8 w-8 animate-spin text-slate-300 mx-auto" />
                                            </TableCell>
                                        </TableRow>
                                    ) : tickets.length === 0 ? (
                                        <TableRow>
                                            <TableCell colSpan={4} className="text-center h-32 text-slate-400">
                                                <div className="flex flex-col items-center gap-2">
                                                    <MessageSquare className="h-8 w-8 text-slate-200" />
                                                    <p>No active tickets found.</p>
                                                </div>
                                            </TableCell>
                                        </TableRow>
                                    ) : (
                                        tickets.map((ticket) => (
                                            <TableRow key={ticket.id} className="border-slate-50">
                                                <TableCell className="font-mono text-[11px] text-slate-500">{ticket.ticket_number}</TableCell>
                                                <TableCell className="font-semibold text-slate-900">{ticket.subject}</TableCell>
                                                <TableCell>
                                                    <Badge variant={ticket.status === 'open' ? 'default' : 'secondary'}
                                                        className={ticket.status === 'open' ? 'bg-blue-600' : 'bg-slate-200 text-slate-600'}>
                                                        {ticket.status}
                                                    </Badge>
                                                </TableCell>
                                                <TableCell className="text-right">
                                                    <Button variant="ghost" size="sm" onClick={() => handleOpenTicket(ticket)} className="text-blue-600 hover:text-blue-700 hover:bg-blue-50">
                                                        Interact
                                                    </Button>
                                                </TableCell>
                                            </TableRow>
                                        ))
                                    )}
                                </TableBody>
                            </Table>
                        </CardContent>
                    </Card>

                    {/* Quick Tips or Stats Card */}
                    <Card className="border-blue-100 bg-blue-50/30 overflow-hidden">
                        <div className="flex p-5 gap-4">
                            <div className="h-10 w-10 shrink-0 rounded-full bg-blue-100 flex items-center justify-center text-blue-600">
                                <Sparkles className="h-5 w-5" />
                            </div>
                            <div>
                                <h4 className="font-bold text-blue-900">Did you know?</h4>
                                <p className="text-sm text-blue-800 leading-relaxed mt-1">
                                    Our AI Assistant can handle most requests instantly, including <strong>claims assessment from photos</strong>,
                                    policy cancellations, and coverage explanations.
                                </p>
                            </div>
                        </div>
                    </Card>
                </div>
            </div>

            <Dialog open={!!selectedTicket} onOpenChange={(open) => !open && setSelectedTicket(null)}>
                <DialogContent className="max-w-2xl max-h-[85vh] flex flex-col p-0 overflow-hidden border-none shadow-2xl">
                    <div className="bg-slate-900 text-white p-6">
                        <DialogHeader>
                            <div className="flex justify-between items-start">
                                <div>
                                    <DialogTitle className="text-2xl font-bold">{selectedTicket?.subject}</DialogTitle>
                                    <DialogDescription className="text-slate-400 mt-1">
                                        Ticket #{selectedTicket?.ticket_number} • {selectedTicket?.category}
                                    </DialogDescription>
                                </div>
                                <Badge className={selectedTicket?.status === 'open' ? 'bg-blue-500' : 'bg-slate-700'}>
                                    {selectedTicket?.status}
                                </Badge>
                            </div>
                        </DialogHeader>
                    </div>

                    <div className="flex-1 overflow-y-auto p-6 bg-slate-50 space-y-6">
                        <div className="bg-white p-5 rounded-xl shadow-sm border border-slate-100">
                            <div className="flex items-center gap-2 mb-2 text-xs font-bold text-slate-400 uppercase tracking-wider">
                                <MessageSquare className="h-3 w-3" /> Initial Statement
                            </div>
                            <p className="text-slate-700 leading-relaxed whitespace-pre-wrap">{selectedTicket?.description}</p>
                        </div>

                        {selectedTicket?.messages?.filter(m => !m.is_internal).map((msg) => (
                            <div key={msg.id} className={`flex flex-col ${msg.sender_type === 'client' ? 'items-end' : 'items-start'}`}>
                                <div className={`max-w-[85%] p-4 rounded-2xl text-sm shadow-sm ${msg.sender_type === 'client'
                                    ? 'bg-blue-600 text-white rounded-br-none'
                                    : 'bg-white border text-slate-700 rounded-bl-none'
                                    }`}>
                                    <p>{msg.message}</p>
                                    <div className={`text-[10px] mt-2 flex items-center justify-between ${msg.sender_type === 'client' ? 'text-blue-100' : 'text-slate-400'}`}>
                                        <span className="font-bold uppercase tracking-tighter">{msg.sender_type}</span>
                                        <span>{formatDate(msg.created_at)}</span>
                                    </div>
                                </div>
                            </div>
                        ))}
                    </div>

                    <div className="p-6 bg-white border-t flex gap-3 shadow-[0_-4px_6px_-1px_rgba(0,0,0,0.05)]">
                        <Textarea
                            placeholder="Add a comment..."
                            value={replyText}
                            onChange={(e) => setReplyText(e.target.value)}
                            className="flex-1 min-h-[50px] border-slate-200 focus-visible:ring-blue-500"
                        />
                        <Button onClick={handleReply} disabled={sending || !replyText.trim()} className="self-end bg-blue-600 hover:bg-blue-700 h-10 px-6">
                            Send
                        </Button>
                    </div>
                </DialogContent>
            </Dialog>
        </div>
    );
}
