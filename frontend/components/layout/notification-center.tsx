"use client";

import { useState, useEffect } from "react";
import { Bell, Check } from "lucide-react";
import { Button } from "@/components/ui/button";
import {
    Popover,
    PopoverContent,
    PopoverTrigger,
} from "@/components/ui/popover";
import { ScrollArea } from "@/components/ui/scroll-area";
import { api } from "@/lib/api";
import { Badge } from "@/components/ui/badge";
import { formatDistanceToNow } from "date-fns";
import { fr, enGB } from "date-fns/locale";
import { ClientOnly } from '@/components/ui/client-only';
import { useLanguage } from '@/contexts/language-context';

export interface Notification {
    id: string;
    type: string;
    channel: string;
    subject: string;
    content: string;
    status: string;
    created_at: string;
    metadata: any;
}

export function NotificationCenter() {
    const { t, language } = useLanguage();
    const [notifications, setNotifications] = useState<Notification[]>([]);
    const [unreadCount, setUnreadCount] = useState(0);
    const [open, setOpen] = useState(false);

    const fetchNotifications = async () => {
        try {
            const response = await api.get<Notification[]>("/notifications?limit=10");
            setNotifications(response.data);
            setUnreadCount(response.data.filter((n) => n.status !== "read").length);
        } catch (error) {
            console.error("Failed to fetch notifications");
        }
    };

    useEffect(() => {
        fetchNotifications();

        // Poll every 30 seconds for new notifications
        const interval = setInterval(fetchNotifications, 30000);
        return () => clearInterval(interval);
    }, []);

    const markAsRead = async (id: string) => {
        try {
            await api.patch(`/notifications/${id}/read`);
            // Optimistic update
            setNotifications(
                notifications.map((n) =>
                    n.id === id ? { ...n, status: "read" } : n
                )
            );
            setUnreadCount((prev) => Math.max(0, prev - 1));
        } catch (error) {
            console.error("Failed to mark as read");
        }
    };

    return (
        <Popover open={open} onOpenChange={setOpen}>
            <PopoverTrigger asChild>
                <Button variant="ghost" size="icon" className="relative">
                    <Bell className="h-5 w-5" />
                    {unreadCount > 0 && (
                        <span className="absolute top-1 right-1 h-2 w-2 rounded-full bg-red-600 ring-2 ring-white" />
                    )}
                </Button>
            </PopoverTrigger>
            <PopoverContent className="w-80 p-0" align="end">
                <div className="flex items-center justify-between border-b p-4">
                    <h4 className="font-semibold text-sm">{t('Notifications')}</h4>
                    {unreadCount > 0 && (
                        <Badge variant="secondary" className="text-xs">
                            {unreadCount} {t('new')}
                        </Badge>
                    )}
                </div>
                <ScrollArea className="h-[300px]">
                    {notifications.length === 0 ? (
                        <div className="flex h-full items-center justify-center p-4 text-sm text-muted-foreground">
                            {t('No notifications')}
                        </div>
                    ) : (
                        <div className="flex flex-col">
                            {notifications.map((notification) => (
                                <div
                                    key={notification.id}
                                    className={`flex flex-col gap-1 border-b p-4 text-sm hover:bg-muted/50 ${notification.status !== "read" ? "bg-blue-50/50" : ""
                                        }`}
                                >
                                    <div className="flex items-start justify-between gap-2">
                                        <span className="font-medium leading-none">
                                            {notification.subject || notification.type}
                                        </span>
                                        {notification.status !== "read" && (
                                            <Button
                                                variant="ghost"
                                                size="icon"
                                                className="h-4 w-4 text-muted-foreground hover:text-primary"
                                                onClick={(e) => {
                                                    e.stopPropagation();
                                                    markAsRead(notification.id);
                                                }}
                                            >
                                                <span className="sr-only">{t('Mark as read')}</span>
                                                <div className="h-2 w-2 rounded-full bg-blue-600" />
                                            </Button>
                                        )}
                                    </div>
                                    <p className="line-clamp-2 text-xs text-muted-foreground">
                                        {notification.content}
                                    </p>
                                    <span className="text-[10px] text-muted-foreground">
                                        <ClientOnly fallback="...">
                                            {formatDistanceToNow(new Date(notification.created_at), {
                                                addSuffix: true,
                                                locale: language === 'fr' ? fr : enGB
                                            })}
                                        </ClientOnly>
                                    </span>
                                </div>
                            ))}
                        </div>
                    )}
                </ScrollArea>
            </PopoverContent>
        </Popover>
    );
}
