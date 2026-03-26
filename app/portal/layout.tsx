'use client';

import React, { useEffect, useState } from 'react';
import { useRouter, usePathname } from 'next/navigation';
import Link from 'next/link';
import { useAuth } from '@/lib/auth';
import { Button } from '@/components/ui/button';
import { clientNavItems } from '@/lib/navigation';
import { cn } from '@/lib/utils';
import { LogOut, User as UserIcon, Menu, X, CircleUser } from 'lucide-react';
import { useBranding } from '@/components/branding-provider';
import { LanguageSwitcher } from '@/components/language-switcher';
// import { ModeToggle } from '@/components/mode-toggle';

export default function ClientPortalLayout({
    children,
}: {
    children: React.ReactNode;
}) {
    const { user, isAuthenticated, loading, logout } = useAuth();
    const router = useRouter();
    const pathname = usePathname();
    const [isMobileMenuOpen, setIsMobileMenuOpen] = useState(false);

    useEffect(() => {
        if (!loading) {
            if (!isAuthenticated) {
                router.push('/login');
            } else if (user?.role !== 'client') {
                // If not a client, redirect to main dashboard
                router.push('/dashboard');
            }
        }
    }, [isAuthenticated, loading, router, user]);

    const { logoUrl } = useBranding();

    const tabs = [
        { title: 'Your Account', href: '/portal' },
        { title: 'Insurance Details', href: '/portal/insurance-details' },
        { title: 'Make a Claim', href: '/portal/claims' },
        { title: 'Refer a Friend', href: '/portal/referrals' },
        { title: 'Contact Us', href: '/portal/support' },
    ];

    if (loading) {
        return (
            <div className="flex min-h-screen items-center justify-center">
                <div className="h-8 w-8 animate-spin rounded-full border-4 border-primary border-t-transparent"></div>
            </div>
        );
    }

    if (!isAuthenticated || user?.role !== 'client') {
        return null;
    }

    return (
        <div className="flex min-h-screen flex-col bg-white">
            {/* Top Navigation */}
            <header className="z-40 bg-white">
                <div className="container mx-auto flex h-20 items-center justify-between py-4 px-6 md:px-8">
                    <div className="flex items-center">
                        <Link href="/portal" className="flex items-center">
                            {logoUrl ? (
                                <img src={logoUrl} alt="Company Logo" className="h-12 w-auto object-contain" />
                            ) : (
                                <div className="flex items-center gap-2">
                                    <div className="flex h-10 w-10 items-center justify-center rounded-md bg-blue-700 text-white">
                                        <span className="text-xl font-bold">T</span>
                                    </div>
                                    <span className="text-2xl font-bold text-blue-900 tracking-tight">Tinsur Insurance</span>
                                </div>
                            )}
                        </Link>
                    </div>

                    <div className="flex items-center gap-8">
                        <div className="hidden md:flex items-center gap-4">
                            <LanguageSwitcher />
                            <div className="flex items-center gap-2">
                                <div className="h-10 w-10 rounded-full bg-blue-50 border border-blue-100 flex items-center justify-center text-blue-600">
                                    <CircleUser className="h-6 w-6" />
                                </div>
                                <div className="flex flex-col">
                                    <span className="text-[11px] text-gray-500 leading-none">Logged in as</span>
                                    <span className="text-sm font-bold text-blue-900 leading-tight">{user.first_name} {user.last_name}</span>
                                </div>
                            </div>
                            <Button
                                variant="outline"
                                size="sm"
                                onClick={logout}
                                className="rounded-full border-[#00539F] text-[#00539F] hover:bg-blue-50 px-6 font-bold"
                            >
                                Log out
                            </Button>
                        </div>
                        {/* Mobile Menu Toggle */}
                        <Button
                            variant="ghost"
                            className="md:hidden"
                            onClick={() => setIsMobileMenuOpen(!isMobileMenuOpen)}
                        >
                            {isMobileMenuOpen ? <X className="h-6 w-6" /> : <Menu className="h-6 w-6" />}
                        </Button>
                    </div>
                </div>

                {/* Tab Navigation Section */}
                <div className="border-t border-b border-gray-100 bg-white overflow-x-auto">
                    <div className="container mx-auto px-0 flex justify-center">
                        <nav className="flex items-center h-16 w-full max-w-[1700px]">
                            {tabs.map((tab, index) => {
                                const isActive = pathname === tab.href || (tab.href !== '/portal' && pathname?.startsWith(tab.href));
                                return (
                                    <React.Fragment key={tab.href}>
                                        <Link
                                            href={tab.href}
                                            className={cn(
                                                "flex-1 flex items-center justify-center h-full text-base font-bold transition-all relative px-4",
                                                isActive
                                                    ? "text-[#00539F] border-b-4 border-[#00539F]"
                                                    : "text-[#00539F] hover:bg-blue-50/50"
                                            )}
                                        >
                                            {tab.title}
                                        </Link>
                                        {index < tabs.length - 1 && (
                                            <div className="h-8 w-[1px] bg-gray-200 self-center" />
                                        )}
                                    </React.Fragment>
                                );
                            })}
                        </nav>
                    </div>
                </div>

                {/* Mobile Nav */}
                {isMobileMenuOpen && (
                    <div className="md:hidden border-t p-4 space-y-4 bg-white shadow-lg">
                        <nav className="flex flex-col space-y-3">
                            {tabs.map((tab) => (
                                <Link
                                    key={tab.href}
                                    href={tab.href}
                                    className={cn(
                                        "flex items-center p-3 rounded-lg text-sm font-bold transition-colors",
                                        pathname === tab.href ? "bg-blue-50 text-[#00539F]" : "text-gray-600 hover:bg-gray-50"
                                    )}
                                    onClick={() => setIsMobileMenuOpen(false)}
                                >
                                    {tab.title}
                                </Link>
                            ))}
                            <div className="border-t pt-4 mt-2">
                                <div className="flex items-center gap-2 mb-4 px-2">
                                    <CircleUser className="h-5 w-5 text-blue-600" />
                                    <span className="text-sm font-bold text-blue-900">{user.first_name} {user.last_name}</span>
                                </div>
                                <Button onClick={logout} className="w-full bg-[#00539F] hover:bg-blue-800 text-white font-bold rounded-full">
                                    Log out
                                </Button>
                            </div>
                        </nav>
                    </div>
                )}
            </header>

            <main className="flex-1 bg-white">
                <div className="container mx-auto max-w-[1700px] py-12 px-6 md:px-8">
                    {children}
                </div>
            </main>
        </div>
    );
}
