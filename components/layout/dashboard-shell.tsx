'use client';

import { useState, useEffect } from 'react';
import { NavigationSidebar } from '@/components/layout/navigation-sidebar';
import { TopHeader } from '@/components/layout/top-header';
import { Button } from '@/components/ui/button';
import { cn } from '@/lib/utils';
import { usePathname } from 'next/navigation';
import { AgentWorkspace } from "@/components/ai-agent/agent-workspace";
import { X, Sparkles } from "lucide-react";
import { useChat } from "@/context/chat-context";

import { useLanguage } from '@/contexts/language-context';

interface DashboardShellProps {
    children: React.ReactNode;
}

export function DashboardShell({ children }: DashboardShellProps) {
    const { t } = useLanguage();
    // State for layout controls
    const [isSidebarOpen, setIsSidebarOpen] = useState(true); // Mobile specific
    const [isSidebarCollapsed, setIsSidebarCollapsed] = useState(false); // Desktop specific
    const [isMobile, setIsMobile] = useState(false);
    const { isAiOpen, setIsAiOpen } = useChat();
    const pathname = usePathname();

    // Handle responsive behavior and route-based collapsing
    useEffect(() => {
        const checkMobile = () => {
            const mobile = window.innerWidth < 768;
            setIsMobile(mobile);
            if (mobile) {
                setIsSidebarOpen(false);
            } else {
                setIsSidebarOpen(true);
            }
        };

        // Initial check
        checkMobile();

        if (pathname?.includes('/dashboard/ai-manager')) {
            setIsSidebarCollapsed(true);
        }

        // Event listener
        window.addEventListener('resize', checkMobile);
        return () => window.removeEventListener('resize', checkMobile);
    }, [pathname]);

    const toggleSidebar = () => {
        if (isMobile) {
            setIsSidebarOpen(!isSidebarOpen);
        } else {
            setIsSidebarCollapsed((collapsed) => !collapsed);
        }
    };

    return (
        <div className="flex h-screen overflow-hidden bg-background">
            {isMobile ? (
                /* Mobile Layout (Legacy Overlay) */
                <>
                    <aside
                        className={cn(
                            'fixed inset-y-0 left-0 z-20 flex flex-col transition-all duration-300',
                            'w-64',
                            !isSidebarOpen && '-translate-x-full',
                            isSidebarOpen && 'translate-x-0 shadow-lg'
                        )}
                    >
                        <NavigationSidebar isCollapsed={false} />
                    </aside>

                    {isSidebarOpen && (
                        <div
                            className="fixed inset-0 z-10 bg-black/50 md:hidden"
                            onClick={() => setIsSidebarOpen(false)}
                        />
                    )}

                    <main className="flex min-w-0 flex-1 flex-col overflow-hidden transition-all duration-300">
                        <TopHeader
                            onMobileMenuToggle={() => setIsSidebarOpen(true)}
                            onAiToggle={() => setIsAiOpen(!isAiOpen)}
                        />
                        <div className="flex flex-1 overflow-hidden">
                            <div className="flex-1 overflow-y-auto p-4">
                                <div className={cn(
                                    "mx-auto space-y-8 animate-in fade-in duration-500",
                                    pathname?.includes('/dashboard/ai-manager') ? "max-w-full h-full p-0" : "max-w-6xl"
                                )}>
                                    {children}
                                </div>
                            </div>
                        </div>

                        {/* Mobile AI Panel Overlay */}
                        {isAiOpen && (
                            <div className="fixed inset-0 z-30 flex flex-col bg-background animate-in slide-in-from-right duration-300">
                                <div className="flex h-14 items-center justify-between border-b px-4 bg-muted/30">
                                    <div className="flex items-center gap-2">
                                        <div className="flex h-6 w-6 items-center justify-center rounded-full bg-primary/20 text-primary">
                                            <Sparkles className="h-4 w-4" />
                                        </div>
                                        <span className="text-sm font-semibold">{t('dashboard.ai_assistant')}</span>
                                    </div>
                                    <Button variant="ghost" size="icon" onClick={() => setIsAiOpen(false)}>
                                        <X className="h-4 w-4" />
                                    </Button>
                                </div>
                                <div className="flex-1 overflow-hidden">
                                    <AgentWorkspace isGlobal />
                                </div>
                            </div>
                        )}
                    </main>
                </>
            ) : (
                /* Desktop Layout */
                <>
                    <aside
                        className={cn(
                            "flex h-full shrink-0 flex-col border-r bg-sidebar transition-[width] duration-300 ease-in-out",
                            isSidebarCollapsed ? "w-[72px]" : "w-72"
                        )}
                    >
                        <NavigationSidebar isCollapsed={isSidebarCollapsed} onToggleCollapse={toggleSidebar} />
                    </aside>

                    <main className="flex h-full min-w-0 flex-1 flex-col overflow-hidden">
                        <TopHeader
                            onMobileMenuToggle={() => setIsSidebarOpen(true)}
                            onAiToggle={() => setIsAiOpen(!isAiOpen)}
                            className="border-b"
                        />

                        <div className="flex-1 overflow-y-auto bg-background p-6 lg:p-8">
                            <div className={cn(
                                "mx-auto space-y-8 animate-in fade-in duration-500",
                                pathname?.includes('/dashboard/ai-manager') ? "h-full max-w-full p-0" : "max-w-6xl"
                            )}>
                                {children}
                            </div>
                        </div>
                    </main>

                    {isAiOpen && (
                        <aside className="hidden h-full w-[35vw] min-w-[360px] max-w-[420px] shrink-0 border-l bg-background lg:block">
                            <div className="flex h-full flex-col">
                                <div className="flex h-14 items-center justify-between border-b px-4 bg-muted/30">
                                    <div className="flex items-center gap-2">
                                        <div className="flex h-6 w-6 items-center justify-center rounded-full bg-primary/20 text-primary">
                                            <Sparkles className="h-4 w-4" />
                                        </div>
                                        <span className="text-sm font-semibold text-foreground">{t('dashboard.ai_manager_title')}</span>
                                    </div>
                                    <Button variant="ghost" size="icon" className="h-8 w-8 text-muted-foreground hover:text-foreground" onClick={() => setIsAiOpen(false)}>
                                        <X className="h-4 w-4" />
                                        <span className="sr-only">{t('dashboard.close_ai_panel')}</span>
                                    </Button>
                                </div>
                                <div className="flex-1 overflow-hidden">
                                    <AgentWorkspace isGlobal />
                                </div>
                            </div>
                        </aside>
                    )}
                </>
            )}
        </div>
    );
}
