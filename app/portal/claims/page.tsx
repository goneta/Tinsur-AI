'use client';

import React, { useState, useEffect } from 'react';
import { ChevronRight, ArrowLeft, Loader2 } from 'lucide-react';
import { Button } from '@/components/ui/button';
import { PortalClaimDialog } from '@/components/portal/portal-claim-dialog';
import { portalApi, DashboardStats } from '@/lib/portal-api';
import { useSearchParams } from 'next/navigation';

export default function PortalClaimsPage() {
    const searchParams = useSearchParams();
    const policyIdParam = searchParams.get('policyId');
    const [view, setView] = useState<'summary' | 'guide'>(
        searchParams.get('view') === 'guide' ? 'guide' : 'summary'
    );
    const [claimDialogOpen, setClaimDialogOpen] = useState(false);
    const [stats, setStats] = useState<DashboardStats | null>(null);
    const [isLoading, setIsLoading] = useState(true);

    useEffect(() => {
        const fetchStats = async () => {
            try {
                const data = await portalApi.getDashboardStats();
                setStats(data);
            } catch (error) {
                console.error("Failed to fetch dashboard stats", error);
            } finally {
                setIsLoading(false);
            }
        };
        fetchStats();
    }, []);

    const claimCards = [
        {
            title: "Make a Car Insurance claim",
            description: "Make your claim and manage it online through our self-service claims portal.",
            primaryAction: {
                label: "Make a Car claim",
                onClick: () => setView('guide')
            },
            links: []
        },
        {
            title: "Claim for damaged glass or using the wrong fuel",
            description: "Get help for glass damage or if you've used the wrong fuel.",
            links: [
                { label: "Claim for damaged glass", href: "#" },
                { label: "Claim for the wrong fuel", href: "#" }
            ]
        },
        {
            title: "Claim for Breakdown Cover or Key Cover",
            description: "Make a claim if you have these optional extras on your policy.",
            links: [
                { label: "Claim for Breakdown Cover", href: "#" },
                { label: "Claim for Key Cover", href: "#" }
            ]
        }
    ];

    if (isLoading) {
        return (
            <div className="flex h-[400px] items-center justify-center">
                <Loader2 className="h-8 w-8 animate-spin text-muted-foreground" />
            </div>
        );
    }

    if (view === 'guide') {
        const sidebarItems = [
            { label: "Make a new Car claim", active: true },
            { label: "Continue a Car claim" },
            { label: "Manage an existing claim" },
            { label: "Claim for Breakdown Cover" },
            { label: "Claim for Key Cover" },
            { label: "Claim for damaged glass" },
            { label: "Claim for the wrong fuel" },
        ];

        return (
            <div className="space-y-12 max-w-[1700px] mx-auto animate-in fade-in slide-in-from-right-4 duration-500">
                <button
                    onClick={() => setView('summary')}
                    className="flex items-center gap-2 text-[#00539F] font-bold hover:underline mb-8"
                >
                    <ArrowLeft className="h-5 w-5" />
                    Back to Make a claim
                </button>

                <h1 className="text-2xl font-bold text-gray-900 mb-12">Follow our guide for claims and support</h1>

                <div className="grid grid-cols-1 lg:grid-cols-12 gap-12">
                    {/* Sidebar */}
                    <div className="lg:col-span-4 bg-white border border-gray-100 shadow-sm divide-y divide-gray-100 h-fit">
                        {sidebarItems.map((item, idx) => (
                            <button
                                key={idx}
                                className={`w-full flex items-center justify-between p-6 text-left font-bold transition-all group ${item.active
                                    ? "bg-[#00539F] text-white"
                                    : "text-[#00539F] hover:bg-blue-50"
                                    }`}
                            >
                                <span className="text-lg">{item.label}</span>
                                <ChevronRight className={`h-5 w-5 ${item.active ? "text-white" : "text-[#00539F]"} group-hover:translate-x-1 transition-transform`} />
                            </button>
                        ))}
                    </div>

                    {/* Main Content */}
                    <div className="lg:col-span-8 space-y-8">
                        <h2 className="text-lg font-bold text-gray-900">Make a new claim online</h2>

                        <p className="text-xl text-gray-700 leading-relaxed">
                            Join thousands of customers who got their claims sorted quickly and easily online.
                        </p>

                        <ul className="space-y-6 list-none pl-0">
                            {[
                                "We'll guide you through the easy process, step by step",
                                "You can stop at any time - we'll save your information at each step",
                                "It should only take about 30 minutes",
                                "We're only a phone call away if you need help"
                            ].map((text, idx) => (
                                <li key={idx} className="flex items-start gap-4 text-xl text-gray-700 font-medium">
                                    <span className="text-2xl mt-[-4px]">•</span>
                                    {text}
                                </li>
                            ))}
                        </ul>

                        <div className="pt-4 space-y-6">
                            <Button
                                onClick={() => setClaimDialogOpen(true)}
                                className="bg-[#00539F] hover:bg-blue-800 text-white font-bold rounded-full px-12 py-8 text-2xl flex items-center gap-2 w-fit transition-all shadow-md group"
                            >
                                Make a new Car claim online
                                <ChevronRight className="h-6 w-6 group-hover:translate-x-1 transition-transform" />
                            </Button>

                            <p className="text-xl text-gray-700">
                                Or call us on <span className="text-[#00539F] font-bold border-b-2 border-[#00539F] cursor-pointer hover:text-blue-800 hover:border-blue-800 transition-colors">
                                    {stats?.insurance_company_phone || "0345 677 3377"}
                                </span>*.
                            </p>
                        </div>
                    </div>
                </div>

                <PortalClaimDialog
                    open={claimDialogOpen}
                    onOpenChange={setClaimDialogOpen}
                    onSuccess={() => setView('summary')}
                    defaultPolicyId={policyIdParam || undefined}
                />
            </div>
        );
    }

    return (
        <div className="space-y-12 max-w-[1700px] mx-auto animate-in fade-in duration-500">
            <div className="flex flex-col md:flex-row md:items-center justify-between gap-6">
                <h1 className="text-2xl font-bold text-gray-900">Get started with your claim</h1>
                {policyIdParam && stats?.policies && (
                    <div className="px-6 py-3 bg-blue-50 border border-blue-100 rounded-2xl flex items-center gap-3">
                        <span className="text-sm font-bold text-[#00539F]">Selected Policy:</span>
                        <span className="text-sm font-black text-[#00539F] bg-white px-3 py-1 rounded-lg border border-blue-200">
                            {stats.policies.find((p: any) => p.id === policyIdParam)?.policy_number || '...'}
                        </span>
                    </div>
                )}
            </div>

            <div className="grid grid-cols-1 md:grid-cols-3 gap-8">
                {claimCards.map((card, idx) => (
                    <div key={idx} className="bg-white border border-gray-100 shadow-sm p-8 flex flex-col min-h-[400px]">
                        <h2 className="text-lg font-bold text-gray-900 mb-6 leading-tight">
                            {card.title}
                        </h2>

                        <p className="text-lg text-gray-600 mb-8 flex-grow">
                            {card.description}
                        </p>

                        <div className="space-y-4">
                            {card.primaryAction && (
                                <Button
                                    onClick={card.primaryAction.onClick}
                                    className="bg-[#00539F] hover:bg-blue-800 text-white font-bold rounded-full px-8 py-6 text-lg flex items-center gap-2 w-fit transition-all shadow-md group"
                                >
                                    {card.primaryAction.label}
                                    <ChevronRight className="h-5 w-5 group-hover:translate-x-1 transition-transform" />
                                </Button>
                            )}

                            {card.links.map((link, lIdx) => (
                                <a
                                    key={lIdx}
                                    href={link.href}
                                    className="flex items-center gap-2 text-[#00539F] font-bold text-lg hover:underline transition-all group"
                                >
                                    {link.label}
                                    <ChevronRight className="h-5 w-5 group-hover:translate-x-1 transition-transform" />
                                </a>
                            ))}
                        </div>
                    </div>
                ))}
            </div>

            <PortalClaimDialog
                open={claimDialogOpen}
                onOpenChange={setClaimDialogOpen}
                onSuccess={() => {
                    console.log("Claim submitted successfully");
                }}
                defaultPolicyId={policyIdParam || undefined}
            />
        </div>
    );
}
