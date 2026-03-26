"use client";

import React, { useState, useEffect, useCallback } from 'react';
import { Checkbox } from "@/components/ui/checkbox";
import { Input } from "@/components/ui/input";
import { Avatar, AvatarFallback, AvatarImage } from "@/components/ui/avatar";
import { ScrollArea } from "@/components/ui/scroll-area";
import { Search, Loader2 } from "lucide-react";
import { api } from "@/lib/api";
import { SharingScope } from './sharing-settings';

// Generic Recipient Interface
export interface Recipient {
    id: string;
    name: string;
    avatarUrl?: string;
    description?: string; // e.g. Email (B2E) or Company Name (B2B)
    type: 'user' | 'company' | 'client';
}

interface RecipientSelectorProps {
    scope: SharingScope;
    selectedIds: string[];
    onSelectionChange: (ids: string[]) => void;
}

export function RecipientSelector({ scope, selectedIds, onSelectionChange }: RecipientSelectorProps) {
    const [searchTerm, setSearchTerm] = useState("");
    const [data, setData] = useState<Recipient[]>([]);
    const [loading, setLoading] = useState(false);

    // Determines fetch URL based on scope
    const getFetchUrl = useCallback((scope: SharingScope) => {
        switch (scope) {
            case 'B2B':
            case 'C2B': // Assuming C2B means Client sharing with Business (Companies)
                return '/companies';
            case 'B2C':
            case 'E2C':
            case 'C2C':
                return '/clients';
            case 'B2E':
            case 'E2E':
                return '/users';
            default: return '/users';
        }
    }, []);

    // Fetch data with debounce
    useEffect(() => {
        const fetchRecipients = async () => {
            setLoading(true);
            try {
                const endpoint = getFetchUrl(scope);
                const params = new URLSearchParams();
                if (searchTerm) params.append('search', searchTerm);
                // Maybe limit? params.append('limit', '20');

                const res = await api.get(`${endpoint}?${params.toString()}`);

                // Map response to generic recipient format
                let mappedData: Recipient[] = [];

                if (scope === 'B2B' || scope === 'C2B') {
                    // Company Response
                    mappedData = res.data.map((item: any) => ({
                        id: item.id,
                        name: item.name,
                        avatarUrl: item.logo_url,
                        description: item.email || item.country,
                        type: 'company'
                    }));
                } else if (scope === 'B2C' || scope === 'E2C' || scope === 'C2C') {
                    // Client Response
                    mappedData = res.data.map((item: any) => ({
                        id: item.id,
                        name: `${item.first_name} ${item.last_name}`,
                        avatarUrl: item.avatar_url, // Assuming client has avatar
                        description: item.email,
                        type: 'client'
                    }));
                } else {
                    // User Response (B2E, E2E)
                    mappedData = res.data.map((item: any) => ({
                        id: item.id,
                        name: `${item.first_name} ${item.last_name}`,
                        avatarUrl: item.profile_image_url || "/avatars/01.png", // fallback or actual field
                        description: item.email,
                        type: 'user'
                    }));
                }

                setData(mappedData);
            } catch (error) {
                console.error("Failed to fetch recipients", error);
                // Optionally show error state or toast
            } finally {
                setLoading(false);
            }
        };

        const timer = setTimeout(() => {
            fetchRecipients();
        }, 300); // 300ms debounce

        return () => clearTimeout(timer);
    }, [scope, searchTerm, getFetchUrl]);

    const handleToggle = (id: string) => {
        if (selectedIds.includes(id)) {
            onSelectionChange(selectedIds.filter(x => x !== id));
        } else {
            onSelectionChange([...selectedIds, id]);
        }
    };

    return (
        <div className="flex flex-col h-full bg-background rounded-lg">
            <div className="p-4 border-b dark:border-border">
                <h3 className="font-semibold mb-3 text-foreground">Select the recipient you want to share with</h3>
                <div className="relative w-full">
                    <Search className="absolute left-3 top-3 h-4 w-4 text-muted-foreground" />
                    <Input
                        placeholder="Type here to find your recipient..."
                        className="pl-9 w-2/3 rounded-full border-green-500 focus-visible:ring-green-500 bg-background text-foreground placeholder:text-muted-foreground"
                        value={searchTerm}
                        onChange={(e) => setSearchTerm(e.target.value)}
                    />
                </div>
            </div>

            <div className="flex-1 overflow-hidden flex flex-col p-4">
                <h4 className="text-lg font-medium mb-4 text-foreground">Recipients</h4>

                <ScrollArea className="flex-1 pr-4">
                    {loading ? (
                        <div className="flex justify-center items-center py-10">
                            <Loader2 className="h-8 w-8 animate-spin text-muted-foreground" />
                        </div>
                    ) : (
                        <div className="space-y-4">
                            {data.length === 0 ? (
                                <p className="text-center text-muted-foreground py-6">No recipients found.</p>
                            ) : (
                                data.map((recipient) => (
                                    <div key={recipient.id} className="flex items-start space-x-3 group p-2 hover:bg-muted/50 rounded-lg transition-colors">
                                        <Checkbox
                                            id={`recipient-${recipient.id}`}
                                            checked={selectedIds.includes(recipient.id)}
                                            onCheckedChange={() => handleToggle(recipient.id)}
                                            className="mt-2 h-5 w-5 rounded border-2 border-slate-400 bg-white dark:bg-slate-950 dark:border-slate-600 data-[state=checked]:border-primary data-[state=checked]:bg-primary data-[state=checked]:text-primary-foreground"
                                        />
                                        <div className="flex-1 flex gap-3 items-center">
                                            <Avatar className="h-10 w-10 text-zinc-950 bg-muted" suppressHydrationWarning>
                                                <AvatarImage src={recipient.avatarUrl} />
                                                <AvatarFallback>{recipient.name.charAt(0).toUpperCase()}</AvatarFallback>
                                            </Avatar>
                                            <div className="grid gap-1">
                                                <label
                                                    htmlFor={`recipient-${recipient.id}`}
                                                    className="font-medium text-base cursor-pointer group-hover:text-primary transition-colors text-foreground"
                                                >
                                                    {recipient.name}
                                                </label>
                                                <p className="text-sm text-muted-foreground line-clamp-1">{recipient.description}</p>
                                            </div>
                                        </div>
                                    </div>
                                ))
                            )}
                        </div>
                    )}
                </ScrollArea>
            </div>
        </div>
    );
}
