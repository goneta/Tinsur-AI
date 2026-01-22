'use client';

import React, { useState } from 'react';
import { useRouter } from 'next/navigation';
import Link from 'next/link';
import { Button } from "@/components/ui/button";
import { Card } from "@/components/ui/card";
import { Label } from "@/components/ui/label";
import { Input } from "@/components/ui/input";
import { toast } from "@/components/ui/use-toast";
import { UserPlus } from "lucide-react";
import { clientApi } from '@/lib/client-api';
import { useAuth } from '@/lib/auth';
import api from '@/lib/api';
import { TinsurLogo } from "@/components/ui/tinsur-logo";
import { LanguageSwitcher } from "@/components/language-switcher";

import { useLanguage } from '@/contexts/language-context';
import { SocialAuth } from "@/components/auth/social-auth";

export default function ClientRegistrationPage() {
    const { t } = useLanguage();
    const router = useRouter();
    const { login } = useAuth();
    const [loading, setLoading] = useState(false);
    const [showEmailForm, setShowEmailForm] = useState(false);
    const [formData, setFormData] = useState({
        first_name: '',
        last_name: '',
        email: '',
        phone: '',
        password: '',
        confirm_password: '',
        sex: 'man'
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
                title: t("register.validation_error", "Validation Error"),
                description: t("register.validation_error_desc", "Please fix the errors in the form"),
                variant: "destructive"
            });
            return;
        }

        setLoading(true);
        try {
            // Step 1: Register client (creates User + Client)
            const registrationPayload = {
                first_name: formData.first_name,
                last_name: formData.last_name,
                email: formData.email,
                phone: formData.phone,
                password: formData.password,
                client_type: "individual",
                status: "active"
            };

            const client = await clientApi.createClient(registrationPayload);

            const loginPayload = {
                email: formData.email,
                password: formData.password
            };

            await login(loginPayload, '/portal/insurance-details');

            toast({
                title: t("register.success.title", "Registration Successful!"),
                description: t("register.success.desc", "Welcome! Redirecting to your profile..."),
            });

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

            <div className="max-w-md w-full mx-auto">
                <div className="text-center mb-8">
                    <div className="flex justify-center mb-4">
                        <div className="bg-blue-100 p-1 rounded-2xl border-4 border-blue-50 overflow-hidden w-24 h-24 flex items-center justify-center">
                            {formData.sex === 'woman' ? (
                                <img src="/avatars/woman.png" alt="Woman Avatar" className="w-full h-full object-cover" />
                            ) : (
                                <img src="/avatars/man.png" alt="Man Avatar" className="w-full h-full object-cover" />
                            )}
                        </div>
                    </div>
                    <h1 className="text-3xl font-black text-gray-900">{t("register.client.title", "Create Your Account")}</h1>
                    <p className="mt-2 text-gray-600">{t("register.client.subtitle", "Join us to get started with your insurance")}</p>
                </div>

                <Card className="p-8">
                    {!showEmailForm ? (
                        <div className="space-y-6">
                            <SocialAuth
                                onEmailClick={() => setShowEmailForm(true)}
                                isLoading={loading}
                            />

                            <div className="text-center text-xs text-gray-400 font-medium px-4">
                                By continuing, you agree to our <a href="#" className="underline">Terms of Service</a> and <a href="#" className="underline">Privacy Policy</a>.
                            </div>

                            <div className="text-center text-sm pt-2">
                                <span className="text-gray-600">{t("register_home.already_have_account")}{" "}</span>
                                <Link href="/login" className="font-medium text-blue-600 hover:text-blue-500">
                                    {t("register_home.login")}
                                </Link>
                            </div>
                        </div>
                    ) : (
                        <form onSubmit={handleSubmit} className="space-y-6">
                            <div className="space-y-2">
                                <Label htmlFor="sex" className="text-slate-600 font-semibold">{t("register.sex", "Sex")} *</Label>
                                <select
                                    id="sex"
                                    value={formData.sex}
                                    onChange={(e) => handleChange('sex', e.target.value)}
                                    className="w-full flex h-11 rounded-lg border border-gray-200 bg-white px-3 py-2 text-sm focus:ring-1 focus:ring-slate-300 transition-all font-medium text-slate-600"
                                >
                                    <option value="man">{t("register.man", "Man")}</option>
                                    <option value="woman">{t("register.woman", "Woman")}</option>
                                </select>
                            </div>
                            <div className="grid grid-cols-2 gap-4">
                                <div className="space-y-2">
                                    <Label htmlFor="first_name">{t("register.first_name", "First Name")} *</Label>
                                    <Input
                                        id="first_name"
                                        value={formData.first_name}
                                        onChange={(e) => handleChange('first_name', e.target.value)}
                                        placeholder={t("register.placeholders.first_name", "John")}
                                        className={errors.first_name ? 'border-red-500' : ''}
                                    />
                                    {errors.first_name && (
                                        <p className="text-sm text-red-500">{errors.first_name}</p>
                                    )}
                                </div>

                                <div className="space-y-2">
                                    <Label htmlFor="last_name">{t("register.last_name", "Last Name")} *</Label>
                                    <Input
                                        id="last_name"
                                        value={formData.last_name}
                                        onChange={(e) => handleChange('last_name', e.target.value)}
                                        placeholder={t("register.placeholders.last_name", "Doe")}
                                        className={errors.last_name ? 'border-red-500' : ''}
                                    />
                                    {errors.last_name && (
                                        <p className="text-sm text-red-500">{errors.last_name}</p>
                                    )}
                                </div>
                            </div>

                            <div className="space-y-2">
                                <Label htmlFor="email">{t("register.email", "Email")} *</Label>
                                <Input
                                    id="email"
                                    type="email"
                                    value={formData.email}
                                    onChange={(e) => handleChange('email', e.target.value)}
                                    placeholder={t("register.placeholders.email", "john.doe@example.com")}
                                    className={errors.email ? 'border-red-500' : ''}
                                />
                                {errors.email && (
                                    <p className="text-sm text-red-500">{errors.email}</p>
                                )}
                            </div>

                            <div className="space-y-2">
                                <Label htmlFor="phone">{t("register.phone", "Phone Number")} *</Label>
                                <Input
                                    id="phone"
                                    type="tel"
                                    value={formData.phone}
                                    onChange={(e) => handleChange('phone', e.target.value)}
                                    placeholder={t("register.placeholders.phone", "+33 6 12 34 56 78")}
                                    className={errors.phone ? 'border-red-500' : ''}
                                />
                                {errors.phone && (
                                    <p className="text-sm text-red-500">{errors.phone}</p>
                                )}
                            </div>

                            <div className="space-y-2">
                                <Label htmlFor="password">{t("register.password", "Password")} *</Label>
                                <Input
                                    id="password"
                                    type="password"
                                    value={formData.password}
                                    onChange={(e) => handleChange('password', e.target.value)}
                                    placeholder="••••••••"
                                    className={errors.password ? 'border-red-500' : ''}
                                />
                                {errors.password && (
                                    <p className="text-sm text-red-500">{errors.password}</p>
                                )}
                            </div>

                            <div className="space-y-2">
                                <Label htmlFor="confirm_password">{t("register.confirm_password", "Confirm Password")} *</Label>
                                <Input
                                    id="confirm_password"
                                    type="password"
                                    value={formData.confirm_password}
                                    onChange={(e) => handleChange('confirm_password', e.target.value)}
                                    placeholder="••••••••"
                                    className={errors.confirm_password ? 'border-red-500' : ''}
                                />
                                {errors.confirm_password && (
                                    <p className="text-sm text-red-500">{errors.confirm_password}</p>
                                )}
                            </div>

                            <Button
                                type="submit"
                                className="w-full h-12 rounded-xl bg-blue-600 hover:bg-blue-700 font-bold"
                                disabled={loading}
                            >
                                {loading ? t("register.loading", "Creating Account...") : t("register.create_btn", "Create Account")}
                            </Button>

                            <div className="flex flex-col gap-4 text-center text-sm">
                                <button
                                    type="button"
                                    onClick={() => setShowEmailForm(false)}
                                    className="text-gray-500 hover:text-gray-700"
                                >
                                    ← Back to social options
                                </button>

                                <div>
                                    <span className="text-gray-600">{t("register_home.already_have_account")}{" "}</span>
                                    <Link href="/login" className="text-blue-600 hover:underline font-medium">
                                        {t("register_home.login")}
                                    </Link>
                                </div>
                            </div>
                        </form>
                    )}
                </Card>
            </div>
        </div>
    );
}
