'use client';

import { Ticket } from '@/services/ticketService';
import {
    Table,
    TableBody,
    TableCell,
    TableHead,
    TableHeader,
    TableRow,
} from '@/components/ui/table';
import { Badge } from '@/components/ui/badge';
import { format } from 'date-fns';

interface TicketListProps {
    tickets: Ticket[];
}

export function TicketList({ tickets }: TicketListProps) {
    const getStatusColor = (status: string) => {
        switch (status) {
            case 'open': return 'default'; // default is likely black/primary
            case 'in_progress': return 'secondary'; // usually blue/grey
            case 'resolved': return 'outline'; // green ideally but outline is safe
            case 'closed': return 'outline';
            default: return 'outline';
        }
    };

    const getPriorityColor = (priority: string) => {
        switch (priority) {
            case 'urgent': return 'destructive';
            case 'high': return 'destructive';
            case 'medium': return 'default';
            case 'low': return 'secondary';
            default: return 'outline';
        }
    };

    if (tickets.length === 0) {
        return (
            <div className="text-center py-10 text-muted-foreground">
                No tickets found.
            </div>
        );
    }

    return (
        <Table>
            <TableHeader>
                <TableRow>
                    <TableHead>Ticket #</TableHead>
                    <TableHead>Subject</TableHead>
                    <TableHead>Status</TableHead>
                    <TableHead>Priority</TableHead>
                    <TableHead>Created</TableHead>
                </TableRow>
            </TableHeader>
            <TableBody>
                {tickets.map((ticket) => (
                    <TableRow key={ticket.id}>
                        <TableCell className="font-medium">{ticket.ticket_number}</TableCell>
                        <TableCell>{ticket.subject}</TableCell>
                        <TableCell>
                            <Badge variant={getStatusColor(ticket.status) as any}>
                                {ticket.status.replace('_', ' ')}
                            </Badge>
                        </TableCell>
                        <TableCell>
                            <Badge variant={getPriorityColor(ticket.priority) as any} className="capitalize">
                                {ticket.priority}
                            </Badge>
                        </TableCell>
                        <TableCell>
                            {format(new Date(ticket.created_at), 'MMM d, yyyy')}
                        </TableCell>
                    </TableRow>
                ))}
            </TableBody>
        </Table>
    );
}
