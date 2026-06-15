'use client';

import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { MessageSquare, FileText, Share2, Mail } from 'lucide-react';

interface CommunicationCardProps {
    employeeId: string;
}

export function CommunicationCard({ employeeId }: CommunicationCardProps) {
    // Mock communication stats as requested
    const stats = {
        receivedMessages: 145,
        receivedDocuments: 28,
        sharedDocuments: 15,
    };

    return (
        <Card className="h-full">
            <CardHeader className="pb-2">
                <CardTitle className="text-lg font-medium flex items-center gap-2">
                    <Mail className="h-4 w-4 text-primary" />
                    Communication
                </CardTitle>
            </CardHeader>
            <CardContent>
                <div className="space-y-4">
                    <div className="flex items-center gap-4">
                        <div className="p-2 rounded-md bg-blue-100 text-blue-600">
                            <MessageSquare className="h-5 w-5" />
                        </div>
                        <div className="flex-1">
                            <div className="text-xs text-muted-foreground uppercase tracking-wider font-semibold">Messages Received</div>
                            <div className="text-xl font-bold">{stats.receivedMessages}</div>
                        </div>
                    </div>

                    <div className="flex items-center gap-4">
                        <div className="p-2 rounded-md bg-purple-100 text-purple-600">
                            <FileText className="h-5 w-5" />
                        </div>
                        <div className="flex-1">
                            <div className="text-xs text-muted-foreground uppercase tracking-wider font-semibold">Documents Received</div>
                            <div className="text-xl font-bold">{stats.receivedDocuments}</div>
                        </div>
                    </div>

                    <div className="flex items-center gap-4">
                        <div className="p-2 rounded-md bg-orange-100 text-orange-600">
                            <Share2 className="h-5 w-5" />
                        </div>
                        <div className="flex-1">
                            <div className="text-xs text-muted-foreground uppercase tracking-wider font-semibold">Documents Shared</div>
                            <div className="text-xl font-bold">{stats.sharedDocuments}</div>
                        </div>
                    </div>
                </div>
            </CardContent>
        </Card>
    );
}
