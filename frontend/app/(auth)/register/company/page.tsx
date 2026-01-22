'use client';

import React, { useState } from 'react';
import { useRouter } from 'next/navigation';
import { Button } from "@/components/ui/button";
import { Card } from "@/components/ui/card";
import { Label } from "@/components/ui/label";
import { Input } from "@/components/ui/input";
import { toast } from "@/components/ui/use-toast";
import { Building2 } from "lucide-react";
import { useAuth } from '@/lib/auth';
import { TinsurLogo } from "@/components/ui/tinsur-logo";
import { LanguageSwitcher } from "@/components/language-switcher";
import { useLanguage } from '@/contexts/language-context';

export default function CompanyRegistrationPage() {
    const { t } = useLanguage();
    const router = useRouter();
    const { login } = useAuth();
    const [loading, setLoading] = useState(false);
    const [formData, setFormData] = useState({
        first_name: '',
        last_name: '',
        email: '',
        phone: '',
        password: '',
        confirm_password: '',
        company_name: '',
        rccm: '',
        subdomain: '',
        sex: 'man',
        address: ''
    });
    const [errors, setErrors] = useState<Record<string, string>>({});

    const handleChange = (field: string, value: string) => {
        setFormData(prev => ({ ...prev, [field]: value }));
        if (errors[field]) {
            setErrors(prev => {
                const newErrors = { ...prev };
                delete newErrors[field];
                return newErrors;
            });
        }
    };

    const validateForm = () => {
        const newErrors: Record<string, string> = {};

        if (!formData.first_name.trim()) newErrors.first_name = t("register.validation.first_name_required", "First name is required");
        if (!formData.last_name.trim()) newErrors.last_name = t("register.validation.last_name_required", "Last name is required");
        if (!formData.email.trim()) {
            newErrors.email = t("register.validation.email_required", "Email is required");
        } else if (!/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(formData.email)) {
            newErrors.email = t("register.validation.email_invalid", "Invalid email format");
        }
        if (!formData.phone.trim()) newErrors.phone = t("register.validation.phone_required", "Phone number is required");

        if (!formData.company_name.trim()) newErrors.company_name = t("register.validation.company_name_required", "Company name is required");
        if (!formData.rccm.trim()) newErrors.rccm = t("register.validation.rccm_required", "RCCM number is required");
        if (!formData.subdomain.trim()) {
            newErrors.subdomain = t("register.validation.subdomain_required", "Subdomain is required");
        } else if (!/^[a-z0-9-]+$/.test(formData.subdomain)) {
            newErrors.subdomain = t("register.validation.subdomain_invalid", "Invalid subdomain format");
        }

        if (!formData.password) {
            newErrors.password = t("register.validation.password_required", "Password is required");
        } else if (formData.password.length < 8) {
            newErrors.password = t("register.validation.password_min_length", "Password must be at least 8 characters");
        }
        if (formData.password !== formData.confirm_password) {
            newErrors.confirm_password = t("register.validation.password_mismatch", "Passwords do not match");
        }

        setErrors(newErrors);
        return Object.keys(newErrors).length === 0;
    };

    const handleSubmit = async (e: React.FormEvent) => {
        e.preventDefault();

        if (!validateForm()) {
            toast({
                title: t("register.error.validation_title", "Validation Error"),
                description: t("register.error.validation_desc", "Please fix the errors in the form"),
                variant: "destructive"
            });
            return;
        }

        setLoading(true);
        try {
            // Registration logic here (similar to client but for company)
            // For now, let's assume we have a companyApi or similar
            // const registrationPayload = { ... };
            // await api.post('/auth/register/company', registrationPayload);

            toast({
                title: t("register.success.title", "Registration Successful!"),
                description: t("register.success.desc", "Welcome! Redirecting to your dashboard..."),
            });

            // await login(loginPayload, '/portal/dashboard');

        } catch (error: any) {
            console.error("Registration failed:", error);
            const errorMessage = error.response?.data?.detail || t("register.error.generic", "Registration failed. Please try again.");
            toast({
                title: t("register.error.title", "Registration Failed"),
                description: errorMessage,
                variant: "destructive"
            });
        } finally {
            setLoading(false);
        }
    };

    return (
        <div className="min-h-screen bg-gray-50 flex flex-col items-center p-4 relative pt-24 sm:pt-32">
            {/* Header with Logo and Language Switcher */}
            <div className="absolute top-0 left-0 w-full p-6 flex justify-between items-center z-50">
                <TinsurLogo className="ml-2" />
                <div className="mr-2">
                    <LanguageSwitcher />
                </div>
            </div>

            <div className="max-w-xl w-full mx-auto">
                <Card className="p-8 shadow-sm border-gray-200/60 rounded-2xl">
                    <div className="text-center mb-8">
                        <div className="flex justify-center mb-4">
                            <div className="bg-purple-100 p-1 rounded-2xl border-4 border-purple-50 overflow-hidden w-24 h-24 flex items-center justify-center">
                                {formData.sex === 'woman' ? (
                                    <img src="/avatars/woman.png" alt="Woman Avatar" className="w-full h-full object-cover" />
                                ) : (
                                    <img src="/avatars/man.png" alt="Man Avatar" className="w-full h-full object-cover" />
                                )}
                            </div>
                        </div>
                        <h1 className="text-3xl font-bold text-slate-700">{t("register.company.title", "Create an Account")}</h1>
                        <p className="mt-2 text-slate-400 font-medium">
                            {t("register.company.subtitle", "Register your insurance company and start managing policies")}
                        </p>
                    </div>

                    <form onSubmit={handleSubmit} className="space-y-5">
                        <div className="space-y-1.5">
                            <Label htmlFor="sex" className="text-slate-600 font-semibold">{t("register.sex", "Sex")} *</Label>
                            <select
                                id="sex"
                                value={formData.sex}
                                onChange={(e) => handleChange('sex', e.target.value)}
                                className="w-full h-11 rounded-lg border border-gray-200 bg-white px-3 py-2 text-sm focus:ring-1 focus:ring-slate-300 transition-all font-medium text-slate-600"
                            >
                                <option value="man">{t("register.man", "Man")}</option>
                                <option value="woman">{t("register.woman", "Woman")}</option>
                            </select>
                        </div>
                        <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
                            <div className="space-y-1.5">
                                <Label htmlFor="first_name" className="text-slate-600 font-semibold">{t("register.first_name", "First Name")}</Label>
                                <Input
                                    id="first_name"
                                    value={formData.first_name}
                                    onChange={(e) => handleChange('first_name', e.target.value)}
                                    placeholder={t("register.placeholders.first_name", "John")}
                                    className={`bg-white border-gray-200 h-11 px-4 rounded-lg focus:ring-1 focus:ring-slate-300 transition-all ${errors.first_name ? 'border-red-500' : ''}`}
                                />
                                {errors.first_name && (
                                    <p className="text-xs text-red-500 mt-1">{errors.first_name}</p>
                                )}
                            </div>

                            <div className="space-y-1.5">
                                <Label htmlFor="last_name" className="text-slate-600 font-semibold">{t("register.last_name", "Last Name")}</Label>
                                <Input
                                    id="last_name"
                                    value={formData.last_name}
                                    onChange={(e) => handleChange('last_name', e.target.value)}
                                    placeholder={t("register.placeholders.last_name", "Doe")}
                                    className={`bg-white border-gray-200 h-11 px-4 rounded-lg focus:ring-1 focus:ring-slate-300 transition-all ${errors.last_name ? 'border-red-500' : ''}`}
                                />
                                {errors.last_name && (
                                    <p className="text-xs text-red-500 mt-1">{errors.last_name}</p>
                                )}
                            </div>
                        </div>

                        <div className="space-y-1.5">
                            <Label htmlFor="email" className="text-slate-600 font-semibold">{t("register.email", "Email")}</Label>
                            <Input
                                id="email"
                                type="email"
                                value={formData.email}
                                onChange={(e) => handleChange('email', e.target.value)}
                                placeholder={t("register.placeholders.email", "admin@demoinsurance.com")}
                                className={`bg-blue-50/30 border-gray-200 h-11 px-4 rounded-lg focus:ring-1 focus:ring-slate-300 transition-all ${errors.email ? 'border-red-500' : ''}`}
                            />
                            {errors.email && (
                                <p className="text-xs text-red-500 mt-1">{errors.email}</p>
                            )}
                        </div>

                        <div className="space-y-1.5">
                            <Label htmlFor="password" className="text-slate-600 font-semibold">{t("register.password", "Password")}</Label>
                            <Input
                                id="password"
                                type="password"
                                value={formData.password}
                                onChange={(e) => handleChange('password', e.target.value)}
                                placeholder="••••••••"
                                className={`bg-blue-50/30 border-gray-200 h-11 px-4 rounded-lg focus:ring-1 focus:ring-slate-300 transition-all ${errors.password ? 'border-red-500' : ''}`}
                            />
                            {errors.password && (
                                <p className="text-xs text-red-500 mt-1">{errors.password}</p>
                            )}
                        </div>

                        <div className="space-y-1.5">
                            <Label htmlFor="phone" className="text-slate-600 font-semibold">{t("register.phone_optional", "Phone (Optional)")}</Label>
                            <Input
                                id="phone"
                                type="tel"
                                value={formData.phone}
                                onChange={(e) => handleChange('phone', e.target.value)}
                                placeholder={t("register.placeholders.phone", "+225 07 00 00 00 00")}
                                className={`bg-white border-gray-200 h-11 px-4 rounded-lg focus:ring-1 focus:ring-slate-300 transition-all ${errors.phone ? 'border-red-500' : ''}`}
                            />
                        </div>

                        <div className="space-y-1.5">
                            <Label htmlFor="address" className="text-slate-600 font-semibold">{t("register.address", "Address (Optional)")}</Label>
                            <Input
                                id="address"
                                value={formData.address || ''}
                                onChange={(e) => handleChange('address', e.target.value)}
                                placeholder={t("register.placeholders.address", "123 Main St, City")}
                                className="bg-white border-gray-200 h-11 px-4 rounded-lg focus:ring-1 focus:ring-slate-300 transition-all"
                            />
                        </div>

                        <div className="pt-4 border-t border-gray-100">
                            <h3 className="text-slate-600 font-bold mb-4">{t("register.company_info", "Company Information")}</h3>

                            <div className="space-y-5">
                                <div className="space-y-1.5">
                                    <Label htmlFor="company_name" className="text-slate-600 font-semibold">{t("register.company_name", "Company Name")}</Label>
                                    <Input
                                        id="company_name"
                                        value={formData.company_name}
                                        onChange={(e) => handleChange('company_name', e.target.value)}
                                        placeholder={t("register.placeholders.company_name", "ABC Insurance Co.")}
                                        className={`bg-white border-gray-200 h-11 px-4 rounded-lg focus:ring-1 focus:ring-slate-300 transition-all ${errors.company_name ? 'border-red-500' : ''}`}
                                    />
                                    {errors.company_name && (
                                        <p className="text-xs text-red-500 mt-1">{errors.company_name}</p>
                                    )}
                                </div>

                                <div className="space-y-1.5">
                                    <Label htmlFor="rccm" className="text-slate-600 font-semibold">{t("register.rccm", "Company Number (N° RCCM) (Optional)")}</Label>
                                    <Input
                                        id="rccm"
                                        value={formData.rccm}
                                        onChange={(e) => handleChange('rccm', e.target.value)}
                                        placeholder={t("register.placeholders.rccm", "RCCM-123456")}
                                        className={`bg-white border-gray-200 h-11 px-4 rounded-lg focus:ring-1 focus:ring-slate-300 transition-all ${errors.rccm ? 'border-red-500' : ''}`}
                                    />
                                </div>

                                <div className="space-y-1.5">
                                    <Label htmlFor="subdomain" className="text-slate-600 font-semibold">{t("register.subdomain", "Company Subdomain")}</Label>
                                    <div className="flex group">
                                        <Input
                                            id="subdomain"
                                            value={formData.subdomain}
                                            onChange={(e) => handleChange('subdomain', e.target.value)}
                                            placeholder={t("register.placeholders.subdomain", "abc-insurance")}
                                            className={`flex-1 bg-white border-gray-200 h-11 px-4 rounded-l-lg rounded-r-none border-r-0 focus:ring-0 focus:ring-offset-0 transition-all ${errors.subdomain ? 'border-red-500' : ''}`}
                                        />
                                        <div className="bg-slate-300/40 px-3 flex items-center justify-center border border-gray-200 rounded-r-lg border-l-0 text-slate-500 font-medium text-sm">
                                            .tinsur.AI
                                        </div>
                                    </div>
                                    <p className="text-[11px] text-slate-400 mt-1.5 font-medium">
                                        {t("register.subdomain_desc", "This will be your unique company identifier")}
                                    </p>
                                    {errors.subdomain && (
                                        <p className="text-xs text-red-500 mt-1">{errors.subdomain}</p>
                                    )}
                                </div>
                            </div>
                        </div>

                        <Button
                            type="submit"
                            className="w-full h-12 bg-black hover:bg-black/90 text-white font-bold rounded-xl mt-6 transition-all"
                            disabled={loading}
                        >
                            {loading ? t("register.loading", "Creating Account...") : t("register.create_btn", "Create Account")}
                        </Button>

                        <p className="text-sm text-center text-slate-500 font-medium pt-2">
                            {t("register_home.already_have_account", "Already have an account?")}{" "}
                            <a href="/login" className="text-blue-600 hover:underline font-bold">
                                {t("register_home.login", "Sign in")}
                            </a>
                        </p>
                    </form>
                </Card>
            </div>
        </div>
    );
}
