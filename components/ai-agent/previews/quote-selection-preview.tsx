'use client';

import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import { FileText, ArrowRight } from 'lucide-react';

interface QuoteEntry {
    id: string;
    quote_number: string;
    client_name: string;
    policy_type: string;
    created_at: string;
}

interface QuoteSelectionPreviewProps {
    data: {
        quotes: QuoteEntry[];
    };
    onAction?: (action: string, data: any) => void;
}

export function QuoteSelectionPreview({ data, onAction }: QuoteSelectionPreviewProps) {
    if (!data?.quotes || data.quotes.length === 0) {
        return (
            <div className="flex flex-col items-center justify-center p-8 text-center text-muted-foreground">
                <p>No draft quotes found.</p>
            </div>
        );
    }

    return (
        <div className="space-y-4">
            <h2 className="text-xl font-bold text-gray-800">Select Quote to Convert</h2>
            <p className="text-sm text-gray-500 mb-6">Found {data.quotes.length} draft quotes available for conversion.</p>

            <div className="overflow-hidden rounded-xl border border-gray-100 shadow-sm bg-white">
                <table className="w-full text-left border-collapse">
                    <thead>
                        <tr className="bg-gray-50/50 border-b border-gray-100">
                            <th className="px-4 py-3 text-[10px] font-bold text-gray-400 uppercase tracking-wider">Date</th>
                            <th className="px-4 py-3 text-[10px] font-bold text-gray-400 uppercase tracking-wider">Quote #</th>
                            <th className="px-4 py-3 text-[10px] font-bold text-gray-400 uppercase tracking-wider">Client</th>
                            <th className="px-4 py-3 text-[10px] font-bold text-gray-400 uppercase tracking-wider">Type</th>
                            <th className="px-4 py-3 text-[10px] font-bold text-gray-400 uppercase tracking-wider text-right">Action</th>
                        </tr>
                    </thead>
                    <tbody className="divide-y divide-gray-50">
                        {data.quotes.map((quote) => (
                            <tr key={quote.id} className="hover:bg-gray-50/50 transition-colors group">
                                <td className="px-4 py-4 text-xs text-gray-600">
                                    {new Date(quote.created_at).toLocaleDateString()}
                                </td>
                                <td className="px-4 py-4">
                                    <span className="text-xs font-mono font-bold text-blue-600 bg-blue-50 px-2 py-1 rounded">
                                        {quote.quote_number}
                                    </span>
                                </td>
                                <td className="px-4 py-4 text-xs font-medium text-gray-700">
                                    {quote.client_name}
                                </td>
                                <td className="px-4 py-4">
                                    <Badge variant="secondary" className="text-[10px] bg-gray-100 text-gray-600 border-none px-2 py-0">
                                        {quote.policy_type}
                                    </Badge>
                                </td>
                                <td className="px-4 py-4 text-right">
                                    <Button
                                        size="sm"
                                        variant="ghost"
                                        className="h-8 text-[11px] font-bold text-black border border-black/10 hover:bg-black hover:text-white transition-all rounded-full group-hover:border-black"
                                        onClick={() => onAction?.('convert_to_policy', { quote_id: quote.id, quote_number: quote.quote_number })}
                                    >
                                        Convert to Policy
                                        <ArrowRight className="ml-1 h-3 w-3" />
                                    </Button>
                                </td>
                            </tr>
                        ))}
                    </tbody>
                </table>
            </div>
        </div>
    );
}
