'use client';

import { useEffect, useState } from 'react';
import { useRouter } from 'next/navigation';
import { useAuth } from '@/lib/auth';
import { useLanguage } from '@/contexts/language-context';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import {
    Download, Share2, PlayCircle, ArrowRightCircle, FileText, Eye, UserPlus,
    Coins, Trash2, Lock, Users, Search, Upload, ListTodo,
    CircleChevronRight, CircleChevronDown, Shield, AlertCircle,
    CreditCard, Clock, Loader2, PlusCircle, CheckCircle, Heart, CarFront, Settings
} from 'lucide-react';
import { portalApi, DashboardStats } from '@/lib/portal-api';
import { policyApi } from '@/lib/policy-api';
import { formatCurrency } from '@/lib/utils';
import { PortalClaimDialog } from '@/components/portal/portal-claim-dialog';
import { PortalPaymentDialog } from '@/components/portal/portal-payment-dialog';
import { PortalPaymentsTab } from '@/components/portal/portal-payments-tab';
import { PortalQuoteWizard } from '@/components/portal/portal-quote-wizard';
import { PortalExcessDialog } from '@/components/portal/portal-excess-dialog';
import { PortalShareModal } from '@/components/portal/portal-share-modal';
import { PortalSettingsTab } from '@/components/portal/portal-settings-tab';
import { Button } from '@/components/ui/button';
import { useSearchParams } from 'next/navigation';
import { ChevronLeft, ChevronRight as ChevronRightIcon } from 'lucide-react';


export default function ClientPortalPage() {
    const router = useRouter();
    const { user } = useAuth();
    const { t, language } = useLanguage();
    const [stats, setStats] = useState<DashboardStats | null>(null);
    const [isLoading, setIsLoading] = useState(true);

    const [claimDialogOpen, setClaimDialogOpen] = useState(false);
    const [paymentDialogOpen, setPaymentDialogOpen] = useState(false);
    const [quoteWizardOpen, setQuoteWizardOpen] = useState(false);
    const [excessDialogOpen, setExcessDialogOpen] = useState(false);
    const [activeSubTab, setActiveSubTab] = useState<'home' | 'documents' | 'upload' | 'payment' | 'settings'>('home');
    const [shareModalOpen, setShareModalOpen] = useState(false);
    const [selectedDoc, setSelectedDoc] = useState('');
    const [activeDocCategory, setActiveDocCategory] = useState<'my' | 'shared' | 'public' | 'referrals' | 'settlements'>('my');
    const searchParams = useSearchParams();
    const policyIdParam = searchParams.get('policyId');
    const [currentPolicyIndex, setCurrentPolicyIndex] = useState(0);
    const [realPolicyDocuments, setRealPolicyDocuments] = useState<any[]>([]);

    useEffect(() => {
        const tabParam = searchParams.get('tab');
        if (tabParam && ['home', 'documents', 'upload', 'payment', 'settings'].includes(tabParam)) {
            setActiveSubTab(tabParam as any);
        }
    }, [searchParams]);

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

    useEffect(() => {
        fetchStats();
    }, []);

    useEffect(() => {
        if (stats?.policies && policyIdParam) {
            const index = stats.policies.findIndex(p => p.id === policyIdParam);
            if (index !== -1) {
                setCurrentPolicyIndex(index);
            }
        }
    }, [stats, policyIdParam]);

    const activePolicy = stats?.policies?.[currentPolicyIndex] || stats?.primary_policy;

    useEffect(() => {
        const fetchDocuments = async () => {
            if (activeSubTab === 'documents' && activePolicy?.id) {
                try {
                    const docs = await policyApi.getPolicyDocuments(activePolicy.id);
                    // Map string[] to UI format
                    const mappedDocs = docs.map((docPath: string, index: number) => {
                        const fileName = docPath.split('/').pop() || 'Document';
                        // Clean up filename for display
                        const label = fileName.replace('.html', '').replace(/_[^_]+$/, '').replace(/_/g, ' ');

                        return {
                            id: `doc-${index}`,
                            name: fileName, // Keep extension for icon logic if needed
                            label: 'Policy Document',
                            displayLabel: label,
                            size: 'PDF', // Placeholder
                            date: new Date().toISOString().split('T')[0],
                            visibility: 'PRIVATE',
                            recipients: [],
                            policyId: activePolicy.id,
                            // endpoint: /api/v1/documents/policy/{policy_id}/{filename}
                            downloadUrl: `/api/v1/documents/policy/${activePolicy.id}/${fileName}`
                        };
                    });
                    setRealPolicyDocuments(mappedDocs);
                } catch (error) {
                    console.error("Failed to fetch documents", error);
                    setRealPolicyDocuments([]);
                }
            }
        };
        fetchDocuments();
    }, [activeSubTab, activePolicy]);

    const handleNextPolicy = () => {
        if (!stats?.policies) return;
        const nextIndex = (currentPolicyIndex + 1) % stats.policies.length;
        const nextPolicy = stats.policies[nextIndex];
        router.push(`/portal?policyId=${nextPolicy.id}`);
    };

    const handlePrevPolicy = () => {
        if (!stats?.policies) return;
        const prevIndex = (currentPolicyIndex - 1 + stats.policies.length) % stats.policies.length;
        const prevPolicy = stats.policies[prevIndex];
        router.push(`/portal?policyId=${prevPolicy.id}`);
    };

    if (isLoading) {
        return (
            <div className="flex h-[400px] items-center justify-center">
                <Loader2 className="h-8 w-8 animate-spin text-muted-foreground" />
            </div>
        );
    }

    return (
        <div className="space-y-12">
            <div className="grid grid-cols-1 lg:grid-cols-12 gap-12">
                {/* Left Column: Car Card */}
                <div className="lg:col-span-12 xl:col-span-4 space-y-8">
                    <div className="flex flex-col space-y-6">
                        <div className="flex items-start gap-4">

                            <div className="p-1">
                                <CarFront className="h-10 w-10 text-[#00539F] fill-[#00539F]" />
                            </div>
                            <div className="flex flex-col">
                                <h2 className="text-lg font-bold text-[#00539F] leading-tight">
                                    {activePolicy?.vehicles?.[0] ? `${activePolicy.vehicles[0].make} ${activePolicy.vehicles[0].model}` : 'KIA CEE\'D 2 CRDI'}
                                    <br />
                                    ({activePolicy?.vehicles?.[0]?.year || '126'})
                                </h2>
                                <div className="mt-3 inline-block bg-white border border-gray-400 px-3 py-1 font-mono text-base font-bold tracking-wider text-black">
                                    {activePolicy?.vehicles?.[0]?.registration || 'LG13MWC'}
                                </div>
                            </div>
                        </div>

                        <div className="pt-4">
                            <p className="text-base font-bold text-gray-900">
                                {t('portal.policy_label', 'Policy:')} {activePolicy?.policy_number || '5151136N'}
                            </p>
                        </div>

                        <div className="border-t border-gray-200 pt-8 max-w-sm">
                            <p className="text-sm text-gray-700 leading-relaxed">
                                {t('portal.check_details', "Please make sure the details in the 'Your Cover' section and your documents are accurate and still meet your needs.")}
                            </p>
                        </div>
                    </div>
                </div>

                {/* Right Column: Renewal Card */}
                <div className="lg:col-span-12 xl:col-span-8">
                    <div className="rounded-none overflow-hidden shadow-lg border-l-[12px] border-[#00539F] h-full flex flex-col">
                        <div className="bg-[#00539F] px-8 py-5 flex items-center justify-between relative min-h-[72px]">
                            {/* Left Navigation: Previous Policy */}
                            <div className="flex items-center">
                                {stats?.policies && stats.policies.length > 1 && (
                                    <button
                                        onClick={handlePrevPolicy}
                                        disabled={currentPolicyIndex === 0}
                                        className={`flex items-center gap-4 transition-all ${currentPolicyIndex === 0
                                            ? 'opacity-20 cursor-not-allowed'
                                            : 'text-white/70 hover:text-white hover:scale-105 active:scale-95'
                                            }`}
                                    >
                                        <ChevronLeft className="h-7 w-7" strokeWidth={3} />
                                        <span className="text-sm font-black uppercase tracking-widest hidden sm:inline">
                                            {t('portal.prev_policy', 'Previous policy')}
                                        </span>
                                    </button>
                                )}
                            </div>

                            {/* Center: Renewal Date */}
                            <div className="flex-1 flex justify-center px-4">
                                <h3 className="text-lg font-bold text-white tracking-tight text-center">
                                    {t('portal.renewal_date', 'Renewal date:')} {activePolicy?.renewal_date ? new Date(activePolicy.renewal_date).toLocaleDateString(language === 'fr' ? 'fr-FR' : 'en-GB', { day: 'numeric', month: 'long', year: 'numeric' }) : '25 May 2026'}
                                </h3>
                            </div>

                            {/* Right Navigation: Next Policy X/Y */}
                            <div className="flex items-center justify-end">
                                {stats?.policies && stats.policies.length > 1 && (
                                    <button
                                        onClick={handleNextPolicy}
                                        disabled={currentPolicyIndex === stats.policies.length - 1}
                                        className={`flex items-center gap-4 transition-all ${currentPolicyIndex === stats.policies.length - 1
                                            ? 'opacity-20 cursor-not-allowed'
                                            : 'text-white/70 hover:text-white hover:scale-105 active:scale-95'
                                            }`}
                                    >
                                        <span className="text-sm font-black uppercase tracking-widest hidden sm:inline">
                                            {t('portal.next_policy', 'Next policy')} {currentPolicyIndex + 1} / {stats.policies.length}
                                        </span>
                                        <ChevronRightIcon className="h-7 w-7" strokeWidth={3} />
                                    </button>
                                )}
                            </div>
                        </div>
                        <div className="bg-[#EBF7FD] px-8 py-6 flex-1 flex items-center">
                            <p className="text-sm text-[#002B52] leading-snug">
                                {t('portal.renewal_notice', "When it's time for your renewal you'll be able to view it from this page.")}
                            </p>
                        </div>
                    </div>
                </div>
            </div>

            {/* Detailed Policy Cover Section */}
            <div className={`max-w-[1700px] mx-auto space-y-6 transition-all duration-500 px-4 md:px-12`}>
                <div className="text-center space-y-4 mb-8">
                    <h2 className="text-2xl font-black text-gray-900 tracking-tight">
                        {activePolicy?.policy_type_name ? `${t('common.your', 'Your')} ${activePolicy.policy_type_name}` : stats?.premium_tier ? `${t('common.your', 'Your')} ${stats.premium_tier} ${t('common.cover', 'Cover')}` : t('portal.your_cover', 'Your Insurance Cover')}
                    </h2>
                    <p className="text-gray-400 text-lg font-bold">{t('portal.manage_policy', 'Manage your policy details, documents, and renewals in one place.')}</p>

                    <div className="flex items-center justify-center gap-24 border-b border-gray-100 pb-4 mt-8">
                        <button
                            onClick={() => setActiveSubTab('home')}
                            className={`flex items-center gap-3 font-black text-base transition-all group pb-4 px-12 ${activeSubTab === 'home' ? 'text-black border-b-[5px] border-[#00539F] -mb-[21px]' : 'text-gray-400 hover:text-[#00539F]'}`}
                        >
                            <CircleChevronRight className="h-7 w-7 group-hover:scale-110 transition-transform" />
                            {t('portal.tab_summary', 'Policy summary')}
                        </button>
                        <button
                            onClick={() => setActiveSubTab('documents')}
                            className={`flex items-center gap-3 font-black text-base transition-all group pb-4 px-12 ${activeSubTab === 'documents' ? 'text-black border-b-[5px] border-[#00539F] -mb-[21px]' : 'text-gray-400 hover:text-[#00539F]'}`}
                        >
                            <ListTodo className="h-7 w-7 group-hover:scale-110 transition-transform" />
                            {t('portal.tab_docs', 'View documents')}
                        </button>
                        <button
                            onClick={() => setActiveSubTab('upload')}
                            className={`flex items-center gap-3 font-black text-base transition-all group pb-4 px-12 ${activeSubTab === 'upload' ? 'text-black border-b-[5px] border-[#00539F] -mb-[21px]' : 'text-gray-400 hover:text-[#00539F]'}`}
                        >
                            <Upload className="h-7 w-7 group-hover:scale-110 transition-transform" />
                            {t('portal.tab_upload', 'Upload documents')}
                        </button>
                        <button
                            onClick={() => setActiveSubTab('payment')}
                            className={`flex items-center gap-3 font-black text-base transition-all group pb-4 px-12 ${activeSubTab === 'payment' ? 'text-black border-b-[5px] border-[#00539F] -mb-[21px]' : 'text-gray-400 hover:text-[#00539F]'}`}
                        >
                            <CreditCard className="h-7 w-7 group-hover:scale-110 transition-transform" />
                            {t('portal.tab_payment', 'Payment')}
                        </button>
                        <button
                            onClick={() => setActiveSubTab('settings')}
                            className={`flex items-center gap-3 font-black text-base transition-all group pb-4 px-12 ${activeSubTab === 'settings' ? 'text-black border-b-[5px] border-[#00539F] -mb-[21px]' : 'text-gray-400 hover:text-[#00539F]'}`}
                        >
                            <Settings className="h-7 w-7 group-hover:scale-110 transition-transform" />
                            {t('portal.tab_settings', 'Settings')}
                        </button>
                    </div>
                </div>

                <div className="bg-white border border-gray-100 shadow-xl rounded-[40px] p-6 md:p-16">
                    {activeSubTab === 'home' ? (
                        <div className="space-y-12 animate-in fade-in duration-500">
                            {/* Your Policy Overview Card */}
                            <div className="pb-12">
                                <h3 className="text-4xl font-black text-gray-900 mb-10">{t('portal.overview_title', 'Your policy overview')}</h3>
                                <div className="grid grid-cols-1 lg:grid-cols-2 gap-x-24 gap-y-8 bg-gray-50/50 p-10 rounded-[30px] border border-gray-100">
                                    <div className="space-y-6">
                                        <div className="flex justify-between items-baseline py-2 border-b border-gray-100/50">
                                            <span className="text-base text-gray-400 font-bold">{t('portal.policy_num', 'Policy number:')}</span>
                                            <span className="text-base text-black font-black">{activePolicy?.policy_number || '5151136N'}</span>
                                        </div>
                                        <div className="flex justify-between items-baseline py-2 border-b border-gray-100/50">
                                            <span className="text-base text-gray-400 font-bold">{t('portal.cover_level', 'Cover level:')}</span>
                                            <span className="text-base text-black font-black">{activePolicy?.cover_type || t('portal.default_cover_type')}</span>
                                        </div>
                                        <div className="flex justify-between items-baseline py-2 border-b border-gray-100/50">
                                            <span className="text-base text-gray-400 font-bold">{t('portal.start_date', 'Start date:')}</span>
                                            <span className="text-base text-black font-black">
                                                {activePolicy?.start_date ? new Date(activePolicy.start_date).toLocaleDateString(language === 'fr' ? 'fr-FR' : 'en-GB', { day: 'numeric', month: 'long', year: 'numeric' }) : '25 May 2025'}
                                            </span>
                                        </div>
                                        <div className="flex justify-between items-baseline py-2 border-b border-gray-100/50">
                                            <span className="text-base text-gray-400 font-bold">{t('portal.renewal_date', 'Renewal date:')}</span>
                                            <span className="text-base text-black font-black">
                                                {activePolicy?.renewal_date ? new Date(activePolicy.renewal_date).toLocaleDateString(language === 'fr' ? 'fr-FR' : 'en-GB', { day: 'numeric', month: 'long', year: 'numeric' }) : '25 May 2026'}
                                            </span>
                                        </div>
                                    </div>

                                    <div className="space-y-6">
                                        <div className="flex justify-between items-baseline py-2 border-b border-gray-100/50">
                                            <span className="text-base text-gray-400 font-bold">{t('portal.underwritten_by', 'Underwritten by:')}</span>
                                            <span className="text-base text-black font-black">{stats?.insurance_company || 'Tesco Underwriting Limited'}</span>
                                        </div>
                                        <div className="flex justify-between items-baseline py-2 border-b border-gray-100/50">
                                            <span className="text-base text-gray-400 font-bold">{t('portal.ncd', 'No Claims Discount:')}</span>
                                            <span className="text-base text-black font-black">{activePolicy?.ncd_years ?? 7} {t('common.years', 'years')}</span>
                                        </div>
                                        <div className="flex justify-between items-baseline py-2 border-b border-gray-100/50">
                                            <span className="text-base text-gray-400 font-bold">{t('portal.ncd_protected', 'NCD protected:')}</span>
                                            <span className="text-base text-black font-black">{activePolicy?.ncd_protected ? t('common.yes', 'Yes') : t('common.no', 'No')}</span>
                                        </div>
                                    </div>
                                </div>
                            </div>

                            {/* Categories Grid */}
                            <div className="grid grid-cols-1 md:grid-cols-3 gap-16">
                                <div className="p-8 rounded-[30px] border border-gray-100 bg-white hover:shadow-lg transition-all space-y-6">
                                    <h3 className="text-lg font-black text-black">{t('portal.vehicle', 'Vehicle')}</h3>
                                    <div className="space-y-3 text-base text-gray-600 font-bold">
                                        {activePolicy?.vehicles?.map((v, i) => (
                                            <div key={i} className="p-4 bg-gray-50 rounded-2xl">
                                                <p className="text-black text-xl font-black tracking-tight">{v.registration}</p>
                                                <p className="mt-1">{v.make} {v.model}</p>
                                            </div>
                                        )) || (
                                                <div className="p-4 bg-gray-50 rounded-2xl">
                                                    <p className="text-black text-xl font-black tracking-tight">LG13MWC</p>
                                                    <p className="mt-1">KIA CEE&apos;D 2 CRDI (126)</p>
                                                </div>
                                            )}
                                    </div>
                                </div>
                                <div className="p-8 rounded-[30px] border border-gray-100 bg-white hover:shadow-lg transition-all space-y-6">
                                    <h3 className="text-lg font-black text-black">{t('portal.cover_use', 'Cover and use')}</h3>
                                    <div className="space-y-4 text-base text-gray-600 font-bold">
                                        <div className="bg-blue-50 p-6 rounded-2xl border border-blue-100">
                                            <p className="text-sm font-black text-[#00539F] uppercase mb-1">{t('portal.policy_type_label', 'Policy Type')}</p>
                                            <p className="text-black text-lg font-black">{activePolicy?.cover_type || t('portal.default_cover_type')}</p>
                                        </div>
                                        <p className="px-2">{activePolicy?.usage || t('portal.default_usage')}</p>
                                    </div>
                                </div>
                                <div className="p-8 rounded-[30px] border border-gray-100 bg-white hover:shadow-lg transition-all space-y-6">
                                    <h3 className="text-2xl font-black text-black">{t('portal.extras', 'Optional extras')}</h3>
                                    <div className="flex flex-wrap gap-2">
                                        {activePolicy?.services && activePolicy.services.length > 0 ? (
                                            activePolicy.services.map((service, i) => (
                                                <span key={i} className="px-4 py-2 bg-gray-100 text-gray-700 rounded-full text-sm font-black">{service.name_en}</span>
                                            ))
                                        ) : (
                                            <p className="text-gray-400 italic">{t('portal.no_extras', 'No optional extras purchased')}</p>
                                        )}
                                    </div>
                                </div>
                            </div>

                            <div className="grid grid-cols-1 md:grid-cols-3 gap-16">
                                <div className="p-8 rounded-[30px] border border-gray-100 bg-white hover:shadow-lg transition-all space-y-6">
                                    <h3 className="text-lg font-black text-black">{t('portal.excesses', 'Excesses')}</h3>
                                    <div className="space-y-4">
                                        <div className="flex justify-between">
                                            <span className="text-gray-400 font-bold">{t('portal.voluntary', 'Voluntary:')}</span>
                                            <span className="text-black font-black">£{activePolicy?.voluntary_excess ?? 250}</span>
                                        </div>
                                        <div className="flex justify-between">
                                            <span className="text-gray-400 font-bold">{t('portal.compulsory', 'Compulsory:')}</span>
                                            <span className="text-black font-black">£{activePolicy?.compulsory_excess ?? 200}</span>
                                        </div>
                                        <button
                                            onClick={() => setExcessDialogOpen(true)}
                                            className="w-full flex items-center justify-center gap-2 py-4 bg-[#00539F] text-white rounded-2xl font-black hover:bg-[#004380] transition-all"
                                        >
                                            <CircleChevronDown className="h-5 w-5 fill-white" />
                                            {t('portal.view_excesses', 'View all excesses')}
                                        </button>
                                    </div>
                                </div>
                                <div className="p-8 rounded-[30px] border border-gray-100 bg-white hover:shadow-lg transition-all space-y-6">
                                    <h3 className="text-lg font-black text-black">{t('portal.drivers', 'Drivers')}</h3>
                                    <div className="space-y-3">
                                        {activePolicy?.drivers?.map((d, i) => (
                                            <div key={i} className="flex justify-between items-center py-2 border-b border-gray-50 last:border-0">
                                                <span className="text-gray-600 font-bold">{d.name}</span>
                                                <span className="px-3 py-1 bg-green-100 text-green-700 text-xs font-black rounded-full uppercase">{d.type}</span>
                                            </div>
                                        )) || (
                                                <div className="flex justify-between items-center py-2">
                                                    <span className="text-gray-600 font-bold">Kenneth Cisse</span>
                                                    <span className="px-3 py-1 bg-green-100 text-green-700 text-xs font-black rounded-full uppercase">Main</span>
                                                </div>
                                            )}
                                        <button className="w-full flex items-center justify-center gap-2 py-4 border-2 border-gray-100 text-black rounded-2xl font-black hover:bg-gray-50 transition-all mt-4">
                                            <Users className="h-5 w-5" />
                                            {t('portal.manage_drivers', 'Manage drivers')}
                                        </button>
                                    </div>
                                </div>
                                <div className="p-8 rounded-[30px] border border-gray-100 bg-white hover:shadow-lg transition-all space-y-6">
                                    <h3 className="text-lg font-black text-black">{t('portal.claims', 'Claims')}</h3>
                                    <div className="flex flex-col items-center justify-center h-full text-center py-4">
                                        <div className="h-16 w-16 bg-green-50 rounded-full flex items-center justify-center mb-4">
                                            <CheckCircle className="h-8 w-8 text-green-500" />
                                        </div>
                                        <p className="text-gray-400 font-bold max-w-[180px]">{t('portal.no_claims', 'No claims or convictions in last 5 years')}</p>
                                    </div>
                                </div>
                            </div>
                        </div>
                    ) : activeSubTab === 'documents' ? (
                        /* Your Documents View */
                        <div className="space-y-12 animate-in fade-in duration-500">
                            {/* Document Categories Tabs */}
                            <div className="flex items-center gap-6 border-b border-gray-100 pb-2 mb-10 overflow-x-auto">
                                {[
                                    { id: 'my', label: t('portal.my_docs', 'My Documents'), icon: FileText },
                                    { id: 'shared', label: t('portal.shared_docs', 'Shared with me'), icon: Shield },
                                    { id: 'public', label: t('portal.public_dataset', 'Public Dataset'), icon: Eye },
                                    { id: 'referrals', label: t('portal.referrals', 'Referrals'), icon: UserPlus },
                                    { id: 'settlements', label: t('portal.settlements', 'Network Settlements'), icon: Coins },
                                ].map((cat) => (
                                    <button
                                        key={cat.id}
                                        onClick={() => setActiveDocCategory(cat.id as any)}
                                        className={`flex items-center gap-4 px-8 py-5 transition-all whitespace-nowrap rounded-t-[25px] ${activeDocCategory === cat.id
                                            ? 'text-black bg-gray-50 border-b-4 border-black font-black text-base'
                                            : 'text-gray-400 border-transparent hover:text-[#00539F] font-bold text-base'
                                            }`}
                                    >
                                        <cat.icon className={`h-6 w-6 ${activeDocCategory === cat.id ? 'text-black' : 'text-gray-400'}`} />
                                        <span>{cat.label}</span>
                                    </button>
                                ))}
                            </div>

                            <div className="bg-white rounded-[40px] border border-gray-100 p-10 shadow-sm">
                                <div className="mb-12">
                                    <h3 className="text-2xl font-black text-gray-900 mb-2">{t('portal.my_docs_title', 'My Documents')}</h3>
                                    <p className="text-gray-400 text-base font-bold">{t('portal.my_docs_desc', 'Manage the files you own. Configure sharing permissions.')}</p>
                                </div>

                                {activeDocCategory === 'my' ? (
                                    <div className="space-y-6">
                                        {(realPolicyDocuments.length > 0 ? realPolicyDocuments : []).map((doc, idx) => (
                                            <div key={idx} className="grid grid-cols-12 items-center gap-5 p-6 border border-gray-100 rounded-[25px] bg-white hover:bg-gray-50/50 transition-all shadow-sm">
                                                {/* Document Info Column */}
                                                <div className="col-span-12 lg:col-span-8 flex items-center gap-4">
                                                    <div className="p-4 bg-[#00539F]/10 rounded-[20px] flex-shrink-0 shadow-inner">
                                                        <FileText className="h-6 w-6 text-[#00539F]" />
                                                    </div>
                                                    <div>
                                                        <h4 className="text-lg font-black text-gray-900 line-clamp-1">{doc.name}</h4>
                                                        <div className="flex items-center gap-4 mt-3">
                                                            <span className="px-4 py-1.5 bg-gray-100 text-gray-600 text-xs font-black rounded-full uppercase tracking-wider">{doc.label}</span>
                                                            {doc.size && (
                                                                <>
                                                                    <span className="text-gray-400 font-black">•</span>
                                                                    <span className="text-gray-400 font-bold">{doc.size}</span>
                                                                </>
                                                            )}
                                                            <span className="text-gray-400 font-black">•</span>
                                                            <span className="text-gray-400 font-bold">{doc.date}</span>
                                                        </div>
                                                    </div>
                                                </div>

                                                {/* Visibility column */}
                                                <div className="col-span-6 lg:col-span-2 flex flex-col items-center">
                                                    <span className={`px-4 py-1.5 ${doc.visibility === 'PUBLIC' ? 'bg-black text-white' : 'bg-gray-100 text-gray-400'} text-[10px] font-bold rounded-full uppercase tracking-[0.2em] shadow-sm mb-3`}>
                                                        {doc.visibility}
                                                    </span>
                                                    {doc.scope && (
                                                        <span className="text-[11px] font-black text-[#00539F] bg-blue-100/50 px-4 py-1.5 rounded-full uppercase tracking-tighter">{doc.scope} Access</span>
                                                    )}
                                                </div>

                                                {/* Actions Column */}
                                                <div className="col-span-6 lg:col-span-2 flex gap-2 justify-end">
                                                    <a
                                                        href={doc.downloadUrl}
                                                        target="_blank"
                                                        rel="noopener noreferrer"
                                                        className="w-10 h-8 flex items-center justify-center rounded-[10px] bg-blue-50 text-[#00539F] hover:bg-blue-100 transition-all"
                                                    >
                                                        <Eye className="h-4 w-4" />
                                                    </a>
                                                    <Button
                                                        className="w-fit rounded-[10px] gap-2 bg-[#00539F] text-white font-bold hover:bg-[#004380] py-1 h-8 text-xs shadow-md hover:shadow-[0_4px_12px_-3px_rgba(0,83,159,0.3)] transition-all active:scale-95 px-4"
                                                        onClick={() => {
                                                            setSelectedDoc(doc.name);
                                                            setShareModalOpen(true);
                                                        }}
                                                    >
                                                        <Share2 className="h-3 w-3" /> {t('common.share', 'Share')}
                                                    </Button>
                                                </div>
                                            </div>
                                        ))}
                                    </div>
                                ) : (
                                    <div className="py-24 text-center animate-in fade-in slide-in-from-bottom-4 duration-500">
                                        <div className="inline-block p-10 bg-gray-50 rounded-full mb-8">
                                            <Shield className="h-20 w-20 text-gray-200" />
                                        </div>
                                        <h3 className="text-xl font-black text-gray-300 capitalize">
                                            {t('portal.empty_cat', 'Empty category:')} {activeDocCategory.replace('-', ' ')}
                                        </h3>
                                        <p className="text-gray-400 mt-3 text-base font-bold">{t('portal.select_tab', 'Try selecting another tab to view your items.')}</p>
                                    </div>
                                )}
                            </div>
                        </div>
                    ) : activeSubTab === 'upload' ? (
                        /* Upload View */
                        <div className="animate-in fade-in duration-500 space-y-12">
                            <div className="flex flex-col items-center justify-center py-16 border-4 border-dashed border-gray-100 rounded-[50px] bg-gray-50 hover:bg-white hover:border-[#00539F]/30 transition-all group">
                                <div className="p-10 bg-white shadow-xl rounded-[40px] mb-8 group-hover:scale-110 transition-transform">
                                    <Upload className="h-16 w-16 text-[#00539F]" />
                                </div>
                                <h3 className="text-xl font-black text-gray-900 mb-4">{t('portal.drag_upload', 'Click or drag files here')}</h3>
                                <p className="text-gray-400 text-base font-bold mb-8">{t('portal.upload_support', 'Support for PDF, JPG, PNG up to 10MB')}</p>
                                <Button className="px-12 py-8 rounded-[25px] bg-black text-white font-black text-lg hover:bg-zinc-800 transition-all shadow-2xl">
                                    {t('portal.browse_files', 'Browse Files')}
                                </Button>
                            </div>
                        </div>
                    ) : activeSubTab === 'payment' ? (
                        <PortalPaymentsTab onMakePayment={() => setPaymentDialogOpen(true)} />
                    ) : (
                        <PortalSettingsTab />
                    )}
                </div>
            </div>

            {/* Support Dialogs */}
            <PortalClaimDialog
                open={claimDialogOpen}
                onOpenChange={setClaimDialogOpen}
                onSuccess={fetchStats}
                defaultPolicyId={activePolicy?.id}
            />
            <PortalPaymentDialog
                open={paymentDialogOpen}
                onOpenChange={setPaymentDialogOpen}
                onSuccess={fetchStats}
            />
            <PortalQuoteWizard
                open={quoteWizardOpen}
                onOpenChange={setQuoteWizardOpen}
                onSuccess={fetchStats}
            />
            <PortalExcessDialog
                open={excessDialogOpen}
                onOpenChange={setExcessDialogOpen}
                stats={stats}
            />
            <PortalShareModal
                open={shareModalOpen}
                onOpenChange={setShareModalOpen}
                documentName={selectedDoc}
            />
        </div>
    );
}
