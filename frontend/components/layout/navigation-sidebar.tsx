'use client';

import { useState } from 'react';
import Link from 'next/link';
import { usePathname } from 'next/navigation';
import { cn } from '@/lib/utils';
import { Button } from '@/components/ui/button';
import { ScrollArea } from '@/components/ui/scroll-area';
import { Separator } from '@/components/ui/separator';
import { useAuth } from '@/lib/auth';
import { useBranding } from '@/components/branding-provider';
import { getNavGroupsForRole, NavGroup, NavItem } from '@/lib/navigation';
import Image from 'next/image';
import { LogOut, User as UserIcon, ChevronLeft, ChevronRight, ChevronDown } from 'lucide-react';
import { useLanguage } from '@/contexts/language-context';
import { LanguageSwitcher } from '@/components/language-switcher';

interface NavigationSidebarProps {
    className?: string;
    isCollapsed?: boolean;
    onToggleCollapse?: () => void;
}

export function NavigationSidebar({ className, isCollapsed, onToggleCollapse }: NavigationSidebarProps) {
    const pathname = usePathname();
    const { user, logout } = useAuth();
    const branding = useBranding();
    const navigationGroups = getNavGroupsForRole(user?.role);

    // State for expanded groups - default all open
    const [expandedGroups, setExpandedGroups] = useState<Record<string, boolean>>({
        "overview": true,
        "operations": true,
        "finance": true,
        "management": true,
        "tools": true
    });

    const toggleGroup = (groupId: string) => {
        setExpandedGroups(prev => ({
            ...prev,
            [groupId]: !prev[groupId]
        }));
    };

    const getColorClasses = (color?: string) => {
        // Light mode: no color (inherit text color)
        // Dark mode: text color specific to the item
        switch (color) {
            case 'blue': return 'dark:text-blue-400';
            case 'green': return 'dark:text-green-400';
            case 'red': return 'dark:text-red-400';
            case 'orange': return 'dark:text-orange-400';
            case 'purple': return 'dark:text-purple-400';
            case 'pink': return 'dark:text-pink-400';
            case 'indigo': return 'dark:text-indigo-400';
            case 'violet': return 'dark:text-violet-400';
            case 'amber': return 'dark:text-amber-400';
            case 'cyan': return 'dark:text-cyan-400';
            case 'rose': return 'dark:text-rose-400';
            case 'slate': return 'dark:text-slate-400';
            default: return 'text-muted-foreground';
        }
    };

    const { t } = useLanguage();

    // Recursive translation function for nav items
    const translateNavItems = (items: NavItem[]): NavItem[] => {
        return items.map(item => ({
            ...item,
            title: t(`nav.${item.id}`, item.title), // Use default fallback
            items: item.items ? translateNavItems(item.items) : undefined
        }));
    };

    // Translate groups
    const translatedGroups = navigationGroups.map(group => ({
        ...group,
        title: t(`nav.${group.id}`, group.title),
        items: translateNavItems(group.items)
    }));

    return (
        <div
            className={cn(
                'flex h-full flex-col border-r bg-sidebar text-sidebar-foreground',
                className
            )}
        >
            <div className={cn("flex h-14 items-center border-b px-4", isCollapsed ? "justify-center" : "justify-between")}>
                <Link href="/dashboard" className="flex items-center gap-2 font-semibold">
                    {branding.logoUrl ? (
                        <div className="relative h-9 w-auto shrink-0 overflow-hidden rounded-lg bg-white p-1 shadow-sm">
                            <Image
                                src={branding.logoUrl}
                                alt="Company Logo"
                                fill
                                className="object-contain"
                            />
                        </div>
                    ) : isCollapsed ? (
                        <div className="relative h-9 w-9 shrink-0 overflow-hidden">
                            <Image
                                src="/images/tinsurAI_logo.png"
                                alt="Tinsur.AI Logo"
                                fill
                                className="object-contain"
                            />
                        </div>
                    ) : (
                        <Image
                            src="/images/tinsurAI_logo.png"
                            alt="Tinsur.AI Logo"
                            width={160}
                            height={40}
                            priority
                            className="object-contain h-10 w-auto"
                        />
                    )}
                </Link>
                {!isCollapsed && onToggleCollapse && (
                    <Button
                        variant="ghost"
                        size="icon"
                        onClick={onToggleCollapse}
                        className="h-8 w-8 text-muted-foreground hover:text-foreground"
                    >
                        <ChevronLeft className="h-4 w-4" />
                    </Button>
                )}
                {isCollapsed && onToggleCollapse && (
                    <Button
                        variant="ghost"
                        size="icon"
                        onClick={onToggleCollapse}
                        className="absolute -right-3 top-3.5 z-50 h-6 w-6 rounded-full border bg-background shadow-sm hover:bg-accent md:flex hidden"
                    >
                        <ChevronRight className="h-3 w-3" />
                    </Button>
                )}
            </div>

            <ScrollArea className="flex-1 py-4">
                <div className="grid gap-4 px-2">
                    {translatedGroups.map((group) => (
                        <div key={group.id} className="flex flex-col gap-1">
                            {!isCollapsed && (
                                <button
                                    onClick={() => toggleGroup(group.id)}
                                    className="flex items-center justify-between px-3 py-1 text-xs font-semibold uppercase text-muted-foreground hover:text-foreground transition-colors group"
                                >
                                    {group.title}
                                    <ChevronDown
                                        className={cn(
                                            "h-3 w-3 transition-transform",
                                            !expandedGroups[group.id] && "-rotate-90"
                                        )}
                                    />
                                </button>
                            )}
                            {isCollapsed && (
                                <div className="h-px mx-2 bg-border my-2 first:hidden" />
                            )}

                            {(expandedGroups[group.id] || isCollapsed) && (
                                <nav className="grid gap-1">
                                    {group.items.map((item: NavItem, index: number) => {
                                        const isActive = pathname === item.href || pathname?.startsWith(`${item.href}/`);
                                        const colorClass = getColorClasses(item.color);

                                        return (
                                            <Link
                                                key={index}
                                                href={item.href}
                                                className={cn(
                                                    'flex items-center gap-3 rounded-md px-3 py-2 text-sm font-medium transition-all group',
                                                    isActive ? 'bg-sidebar-accent text-sidebar-accent-foreground' : 'transparent hover:bg-sidebar-accent/50',
                                                    isCollapsed && 'justify-center px-2'
                                                )}
                                                title={isCollapsed ? item.title : undefined}
                                            >
                                                <div className={cn(
                                                    "flex h-8 w-8 shrink-0 items-center justify-center transition-transform group-hover:scale-110",
                                                    colorClass // Applied directly to text, no bg
                                                )}>
                                                    <item.icon className="h-4 w-4 stroke-[2.5px]" />
                                                </div>
                                                {!isCollapsed && <span>{item.title}</span>}
                                            </Link>
                                        );
                                    })}
                                </nav>
                            )}
                        </div>
                    ))}
                </div>
            </ScrollArea>

            <div className="mt-auto p-4">
                <Separator className="mb-4" />
                <div className={cn("flex items-center gap-4", isCollapsed ? "justify-center" : "justify-between")}>
                    {!isCollapsed && (
                        <div className="flex items-center gap-3 overflow-hidden">
                            <div className="flex h-9 w-9 shrink-0 items-center justify-center rounded-full bg-muted/20">
                                <UserIcon className="h-5 w-5" />
                            </div>
                            <div className="grid gap-0.5 truncate text-left">
                                <span className="truncate text-sm font-medium">{user?.first_name} {user?.last_name}</span>
                                <span className="truncate text-xs text-muted-foreground">{user?.email}</span>
                            </div>
                        </div>
                    )}

                    <div className="flex items-center gap-1">
                        <LanguageSwitcher />
                        <Button
                            variant="ghost"
                            size="icon"
                            onClick={() => setTimeout(() => logout(), 0)}
                            title={t('btn.logout', 'Logout')}
                            className={cn("shrink-0", isCollapsed ? "h-9 w-9" : "h-8 w-8")}
                        >
                            <LogOut className="h-4 w-4" />
                            <span className="sr-only">{t('btn.logout', 'Logout')}</span>
                        </Button>
                    </div>
                </div>
            </div>
        </div>
    );
}
