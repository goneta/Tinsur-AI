import React from 'react';
import { ShareCode, revokeShareCode } from '@/lib/sharecode-api';
import { Button } from "@/components/ui/button";
import {
    Table,
    TableBody,
    TableCell,
    TableHead,
    TableHeader,
    TableRow,
} from "@/components/ui/table";
import { Trash2, Eye, Send } from 'lucide-react';
import { useToast } from "@/components/ui/use-toast";
import Image from 'next/image';

interface ShareCodeListProps {
    codes: ShareCode[];
    onRefresh: () => void;
    onCodeSelect: (code: ShareCode) => void;
}

export const ShareCodeList: React.FC<ShareCodeListProps> = ({ codes, onRefresh, onCodeSelect }) => {
    const { toast } = useToast();

    const handleRevoke = async (id: string) => {
        try {
            await revokeShareCode(id);
            toast({
                title: "Code Revoked",
                description: "The share code has been successfully revoked.",
            });
            onRefresh();
        } catch (error) {
            toast({
                title: "Error",
                description: "Failed to revoke share code",
                variant: "destructive",
            });
        }
    };

    return (
        <div className="rounded-md border">
            <Table>
                <TableHeader>
                    <TableRow>
                        <TableHead>QR Code</TableHead>
                        <TableHead>Code</TableHead>
                        <TableHead>Type</TableHead>
                        <TableHead>Recipients</TableHead>
                        <TableHead>Status</TableHead>
                        <TableHead className="text-right">Actions</TableHead>
                    </TableRow>
                </TableHeader>
                <TableBody>
                    {codes.length === 0 ? (
                        <TableRow>
                            <TableCell colSpan={6} className="h-24 text-center">
                                No active share codes found.
                            </TableCell>
                        </TableRow>
                    ) : (
                        codes.map((code) => (
                            <TableRow key={code.id}>
                                <TableCell>
                                    {code.qr_code_base64 && (
                                        <div className="relative w-10 h-10">
                                            <Image
                                                src={code.qr_code_base64}
                                                alt="QR"
                                                fill
                                                className="object-contain"
                                            />
                                        </div>
                                    )}
                                </TableCell>
                                <TableCell className="font-mono font-medium">{code.code}</TableCell>
                                <TableCell>{code.share_type}</TableCell>
                                <TableCell>{code.recipient_ids.length} Recipients</TableCell>
                                <TableCell>
                                    <span className={`inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium ${code.status === 'active' ? 'bg-green-100 text-green-800' : 'bg-gray-100 text-gray-800'
                                        }`}>
                                        {code.status}
                                    </span>
                                </TableCell>
                                <TableCell className="text-right space-x-2">
                                    <Button variant="ghost" size="icon" onClick={() => onCodeSelect(code)} title="View">
                                        <Eye className="h-4 w-4" />
                                    </Button>
                                    <Button variant="ghost" size="icon" title="Send (Mock)">
                                        <Send className="h-4 w-4" />
                                    </Button>
                                    <Button
                                        variant="ghost"
                                        size="icon"
                                        className="text-red-500 hover:text-red-700 hover:bg-red-50"
                                        onClick={() => handleRevoke(code.id)}
                                        title="Revoke"
                                    >
                                        <Trash2 className="h-4 w-4" />
                                    </Button>
                                </TableCell>
                            </TableRow>
                        ))
                    )}
                </TableBody>
            </Table>
        </div>
    );
};
