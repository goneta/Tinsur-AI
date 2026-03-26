'use client';

import { useState, useEffect } from 'react';
import { usePathname } from 'next/navigation';
import { cn } from '@/lib/utils';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { navGroups } from '@/lib/navigation';
import { Menu, Search, Bell, Sparkles, CreditCard, ShieldAlert, Cpu } from 'lucide-react';
import { HelpButton } from '@/components/help/help-button';
import {
    Popover,
    PopoverContent,
    PopoverTrigger,
} from "@/components/ui/popover";
import { notificationApi, Notification as NotifType } from '@/lib/notification-api';
import { formatDistanceToNow } from 'date-fns';
import { useAuth } from '@/lib/auth';
import { ClientOnly } from '@/components/ui/client-only';
import { LanguageSwitcher } from '@/components/language-switcher';

interface TopHeaderProps {
    onMobileMenuToggle: () => void;
    onAiToggle?: () => void;
    className?: string;
}

export function TopHeader({ onMobileMenuToggle, onAiToggle, className }: TopHeaderProps) {
    const pathname = usePathname();
    const { ai_credits_balance } = useAuth();
    const [notifications, setNotifications] = useState<NotifType[]>([]);
    const [loading, setLoading] = useState(false);

    const fetchNotifications = async () => {
        try {
            const data = await notificationApi.getNotifications({ unread_only: false, limit: 10 });
            setNotifications(data);
        } catch (error) {
            console.error('Failed to fetch notifications', error);
        }
    };

    useEffect(() => {
        fetchNotifications();
        // Poll for updates every 60 seconds
        const interval = setInterval(fetchNotifications, 60000);
        return () => clearInterval(interval);
    }, []);

    const unreadCount = notifications.filter(n => n.status !== 'read').length;

    const markAsRead = async (id: string) => {
        try {
            await notificationApi.markAsRead(id);
            setNotifications(prev => prev.map(n => n.id === id ? { ...n, status: 'read' as const } : n));
        } catch (error) {
            console.error('Failed to mark read', error);
        }
    };

    const getIcon = (type: string) => {
        switch (type) {
            case 'payment_received': return <CreditCard className="h-4 w-4 text-green-500" />;
            case 'low_balance_alert': return <ShieldAlert className="h-4 w-4 text-amber-500" />;
            case 'claim_assessment_ready': return <Cpu className="h-4 w-4 text-purple-500" />;
            default: return <Bell className="h-4 w-4" />;
        }
    };

    // Find current page title from nested groups
    const currentNav = navGroups
        .flatMap(group => group.items)
        .find((item) => pathname?.startsWith(item.href));

    const title = currentNav?.title || 'Dashboard';

    // Generate breadcrumbs (simple version)
    const segments = pathname?.split('/').filter(Boolean) || [];
    const breadcrumbs = segments.length > 1
        ? segments.map(s => s.charAt(0).toUpperCase() + s.slice(1)).join(' / ')
        : '';

    return (
        <header className={cn('flex h-14 items-center gap-4 border-b bg-background px-6', className)}>
            <Button variant="ghost" size="icon" className="md:hidden" onClick={onMobileMenuToggle}>
                <Menu className="h-5 w-5" />
                <span className="sr-only">Toggle menu</span>
            </Button>

            <div className="flex flex-col">
                <h1 className="text-lg font-semibold md:text-xl">{title}</h1>
                {breadcrumbs && (
                    <p className="hidden text-xs text-muted-foreground md:block">{breadcrumbs}</p>
                )}
            </div>

            <div className="ml-auto flex items-center gap-4">
                <div className="relative hidden w-full max-w-sm md:block">
                    <Search className="absolute left-2.5 top-2.5 h-4 w-4 text-muted-foreground" />
                    <Input
                        type="search"
                        placeholder="Search..."
                        className="w-64 pl-8 md:w-80 lg:w-96"
                    />
                </div>

                <LanguageSwitcher />

                <div className="flex items-center gap-1 px-3 py-1.5 bg-primary/5 border rounded-full hover:bg-primary/10 transition-colors cursor-pointer group"
                    onClick={() => {
                        if (onAiToggle) onAiToggle();
                    }}
                >
                    <Sparkles className="h-4 w-4 text-primary" />
                    <span className="text-xs font-bold text-primary font-mono">${ai_credits_balance.toFixed(2)}</span>
                    <Cpu className="h-3 w-3 text-primary/40 group-hover:text-primary transition-colors ml-1" />
                </div>

                <Button
                    variant="ghost"
                    size="icon"
                    className="relative text-primary font-bold hover:bg-primary/10"
                    onClick={onAiToggle}
                >
                    <Sparkles className="h-5 w-5" />
                    <span className="sr-only">AI Manager</span>
                </Button>

                <HelpButton />

                <Popover>
                    <PopoverTrigger asChild>
                        <Button variant="ghost" size="icon" className="relative">
                            <Bell className="h-5 w-5" />
                            {unreadCount > 0 && (
                                <span className="absolute top-2 right-2 flex h-2 w-2">
                                    <span className="animate-ping absolute inline-flex h-full w-full rounded-full bg-destructive opacity-75"></span>
                                    <span className="relative inline-flex rounded-full h-2 w-2 bg-destructive"></span>
                                </span>
                            )}
                            <span className="sr-only">Notifications</span>
                        </Button>
                    </PopoverTrigger>
                    <PopoverContent className="w-80 p-0" align="end">
                        <div className="p-4 border-b">
                            <h3 className="font-semibold text-sm">Notifications</h3>
                        </div>
                        <div className="max-h-[400px] overflow-y-auto">
                            {notifications.length === 0 ? (
                                <div className="p-8 text-center text-sm text-muted-foreground">
                                    No new notifications
                                </div>
                            ) : (
                                notifications.map((n) => (
                                    <div
                                        key={n.id}
                                        className={cn(
                                            "p-4 border-b last:border-0 hover:bg-slate-50 cursor-pointer transition-colors",
                                            n.status !== 'read' && "bg-blue-50/50"
                                        )}
                                        onClick={() => markAsRead(n.id)}
                                    >
                                        <div className="flex gap-3">
                                            <div className="mt-1">{getIcon(n.type)}</div>
                                            <div className="flex-1">
                                                <div className="flex justify-between items-start gap-2">
                                                    <p className="text-sm font-medium leading-none">{n.subject}</p>
                                                    <ClientOnly fallback={<span className="text-[10px] text-muted-foreground whitespace-nowrap">...</span>}>
                                                        <span className="text-[10px] text-muted-foreground whitespace-nowrap">
                                                            {formatDistanceToNow(new Date(n.created_at), { addSuffix: true })}
                                                        </span>
                                                    </ClientOnly>
                                                </div>
                                                <p className="text-xs text-muted-foreground mt-1 line-clamp-2">
                                                    {n.content}
                                                </p>
                                            </div>
                                        </div>
                                    </div>
                                ))
                            )}
                        </div>
                        {notifications.length > 0 && (
                            <div className="p-2 border-t text-center">
                                <Button variant="ghost" size="sm" className="text-xs w-full">
                                    View all
                                </Button>
                            </div>
                        )}
                    </PopoverContent>
                </Popover>
            </div>
        </header>
    );
}
