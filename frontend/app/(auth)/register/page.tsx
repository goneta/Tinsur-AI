"use client";

import Link from 'next/link';
import { Button } from "@/components/ui/button";
import { Building2, UserCircle2, ShieldCheck, CheckCircle2 } from "lucide-react";
import { useLanguage } from "@/contexts/language-context";
import { TinsurLogo } from "@/components/ui/tinsur-logo";
import { LanguageSwitcher } from "@/components/language-switcher";

export default function RegisterPage() {
    const { t } = useLanguage();

    return (
        <div className="min-h-screen bg-gray-50 flex items-center justify-center p-4 relative">
            {/* Header with Logo and Language Switcher */}
            <div className="absolute top-0 left-0 w-full p-6 flex justify-between items-center z-50">
                <TinsurLogo className="ml-2" />
                <div className="mr-2">
                    <LanguageSwitcher />
                </div>
            </div>


            <div className="max-w-4xl w-full pt-16">
                <div className="text-center mb-12">
                    <h1 className="text-4xl font-black text-gray-900 mb-4">
                        {t('register_home.title')}
                    </h1>
                    <p className="text-gray-500 text-lg">
                        {t('register_home.subtitle')}
                    </p>
                </div>

                <div className="grid md:grid-cols-2 gap-6">
                    {/* Client Registration Card */}
                    <div className="bg-white rounded-[30px] p-8 border hover:border-blue-500 hover:shadow-xl transition-all group cursor-pointer relative overflow-hidden">
                        <div className="absolute top-0 right-0 p-4 opacity-10 group-hover:opacity-20 transition-opacity">
                            <UserCircle2 className="w-32 h-32 text-blue-500" />
                        </div>
                        <div className="relative z-10 flex flex-col h-full">
                            <div className="bg-blue-50 w-16 h-16 rounded-2xl flex items-center justify-center mb-6 text-blue-600 group-hover:scale-110 transition-transform">
                                <UserCircle2 className="w-8 h-8" />
                            </div>
                            <h2 className="text-2xl font-bold text-gray-900 mb-2">{t('register_home.client_title')}</h2>
                            <div className="flex-grow">
                                <p className="text-gray-500 mb-6">
                                    {t('register_home.client_desc')}
                                </p>
                                <div className="space-y-3 mb-8">
                                    <div className="flex items-center gap-3 text-gray-600">
                                        <ShieldCheck className="w-5 h-5 text-blue-500" />
                                        <span className="font-medium">{t('register_home.client_feat_1')}</span>
                                    </div>
                                    <div className="flex items-center gap-3 text-gray-600">
                                        <ShieldCheck className="w-5 h-5 text-blue-500" />
                                        <span className="font-medium">{t('register_home.client_feat_2')}</span>
                                    </div>
                                    <div className="flex items-center gap-3 text-gray-600">
                                        <ShieldCheck className="w-5 h-5 text-blue-500" />
                                        <span className="font-medium">{t('register_home.client_feat_3')}</span>
                                    </div>
                                </div>
                            </div>
                            <Link href="/register/client" className="w-full">
                                <Button className="w-full h-12 rounded-xl text-lg font-bold bg-blue-600 hover:bg-blue-700">
                                    {t('register_home.client_btn')}
                                </Button>
                            </Link>
                        </div>
                    </div>

                    {/* Company Registration Card */}
                    <div className="bg-white rounded-[30px] p-8 border hover:border-purple-500 hover:shadow-xl transition-all group cursor-pointer relative overflow-hidden">
                        <div className="absolute top-0 right-0 p-4 opacity-10 group-hover:opacity-20 transition-opacity">
                            <Building2 className="w-32 h-32 text-purple-500" />
                        </div>
                        <div className="relative z-10 flex flex-col h-full">
                            <div className="bg-purple-50 w-16 h-16 rounded-2xl flex items-center justify-center mb-6 text-purple-600 group-hover:scale-110 transition-transform">
                                <Building2 className="w-8 h-8" />
                            </div>
                            <h2 className="text-2xl font-bold text-gray-900 mb-2">{t('register_home.company_title')}</h2>
                            <div className="flex-grow">
                                <p className="text-gray-500 mb-6">
                                    {t('register_home.company_desc')}
                                </p>
                                <div className="space-y-3 mb-8">
                                    <div className="flex items-center gap-3 text-gray-600">
                                        <CheckCircle2 className="w-5 h-5 text-purple-500" />
                                        <span className="font-medium">{t('register_home.company_feat_1')}</span>
                                    </div>
                                    <div className="flex items-center gap-3 text-gray-600">
                                        <CheckCircle2 className="w-5 h-5 text-purple-500" />
                                        <span className="font-medium">{t('register_home.company_feat_2')}</span>
                                    </div>
                                    <div className="flex items-center gap-3 text-gray-600">
                                        <CheckCircle2 className="w-5 h-5 text-purple-500" />
                                        <span className="font-medium">{t('register_home.company_feat_3')}</span>
                                    </div>
                                </div>
                            </div>
                            <Link href="/register/company" className="w-full">
                                <Button className="w-full h-12 rounded-xl text-lg font-bold bg-white text-purple-600 border-2 border-purple-100 hover:bg-purple-50 hover:border-purple-200">
                                    {t('register_home.company_btn')}
                                </Button>
                            </Link>
                        </div>
                    </div>
                </div>

                <div className="text-center mt-12">
                    <p className="text-gray-500">
                        {t('register_home.already_have_account')}{' '}
                        <Link href="/login" className="text-blue-600 font-bold hover:underline">
                            {t('register_home.login')}
                        </Link>
                    </p>
                </div>
            </div>
        </div>
    );
}
