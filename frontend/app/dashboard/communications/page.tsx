"use client";

import { useState, useEffect } from "react";
import { format } from "date-fns";
import { Mail, MessageSquare, Bell, Filter, RefreshCcw } from "lucide-react";

import { Button } from "@/components/ui/button";
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from "@/components/ui/card";
import { Input } from "@/components/ui/input";
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from "@/components/ui/table";
import { Badge } from "@/components/ui/badge";
import {
    Select,
    SelectContent,
    SelectItem,
    SelectTrigger,
    SelectValue,
} from "@/components/ui/select";
import { api } from "@/lib/api";
import { useToast } from "@/components/ui/use-toast";

interface NotificationLog {
    id: string;
    type: string;
    channel: string;
    subject: string;
    content: string;
    status: string;
    created_at: string;
    recipient?: string; // We might need to fetch this if not in current API response
}

export default function CommunicationsPage() {
    const [logs, setLogs] = useState<NotificationLog[]>([]);
    const [loading, setLoading] = useState(true);
    const [filterChannel, setFilterChannel] = useState("all");
    const { toast } = useToast();

    const fetchLogs = async () => {
        setLoading(true);
        try {
            // Using scope=all to get company-wide logs
            const response = await api.get<NotificationLog[]>("/notifications/?scope=all&limit=100");
            setLogs(response.data);
        } catch (error) {
            toast({
                title: "Error",
                description: "Failed to fetch communication logs.",
                variant: "destructive",
            });
        } finally {
            setLoading(false);
        }
    };

    useEffect(() => {
        fetchLogs();
    }, []);

    const getIcon = (channel: string) => {
        switch (channel) {
            case "email": return <Mail className="h-4 w-4" />;
            case "sms": return <MessageSquare className="h-4 w-4" />;
            default: return <Bell className="h-4 w-4" />;
        }
    };

    const getStatusVariant = (status: string) => {
        switch (status) {
            case "sent": return "success"; // Assuming custom variant or use default
            case "delivered": return "success";
            case "failed": return "destructive";
            case "pending": return "secondary";
            default: return "outline";
        }
    };

    const filteredLogs = logs.filter(log => filterChannel === "all" || log.channel === filterChannel);

    return (
        <div className="space-y-6">
            <div className="flex justify-between items-center">
                <div>
                    <h2 className="text-3xl font-bold tracking-tight">Communications Log</h2>
                    <p className="text-muted-foreground">Audit trail of all system sent emails and messages.</p>
                </div>
                <Button variant="outline" onClick={fetchLogs}>
                    <RefreshCcw className="mr-2 h-4 w-4" /> Refresh
                </Button>
            </div>

            <Card>
                <CardHeader>
                    <div className="flex justify-between items-center">
                        <CardTitle>Sent History</CardTitle>
                        <div className="flex items-center gap-2">
                            <Filter className="h-4 w-4 text-muted-foreground" />
                            <Select value={filterChannel} onValueChange={setFilterChannel}>
                                <SelectTrigger className="w-[180px]">
                                    <SelectValue placeholder="Filter by Channel" />
                                </SelectTrigger>
                                <SelectContent>
                                    <SelectItem value="all">All Channels</SelectItem>
                                    <SelectItem value="email">Email</SelectItem>
                                    <SelectItem value="sms">SMS</SelectItem>
                                    <SelectItem value="whatsapp">WhatsApp</SelectItem>
                                </SelectContent>
                            </Select>
                        </div>
                    </div>
                </CardHeader>
                <CardContent>
                    <Table>
                        <TableHeader>
                            <TableRow>
                                <TableHead>Time</TableHead>
                                <TableHead>Channel</TableHead>
                                <TableHead>Topic</TableHead>
                                <TableHead>Status</TableHead>
                            </TableRow>
                        </TableHeader>
                        <TableBody>
                            {loading ? (
                                <TableRow><TableCell colSpan={4} className="text-center">Loading...</TableCell></TableRow>
                            ) : filteredLogs.length === 0 ? (
                                <TableRow><TableCell colSpan={4} className="text-center text-muted-foreground">No logs found.</TableCell></TableRow>
                            ) : (
                                filteredLogs.map((log) => (
                                    <TableRow key={log.id}>
                                        <TableCell className="text-xs text-muted-foreground">
                                            {format(new Date(log.created_at), "MMM d, HH:mm")}
                                        </TableCell>
                                        <TableCell>
                                            <div className="flex items-center gap-2">
                                                {getIcon(log.channel)}
                                                <span className="capitalize">{log.channel}</span>
                                            </div>
                                        </TableCell>
                                        <TableCell>
                                            <div className="flex flex-col">
                                                <span className="font-medium text-sm">{log.subject}</span>
                                                <span className="text-xs text-muted-foreground line-clamp-1">{log.content}</span>
                                            </div>
                                        </TableCell>
                                        <TableCell>
                                            <Badge variant={log.status === 'failed' ? 'destructive' : 'outline'}>
                                                {log.status}
                                            </Badge>
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
