/**
 * Registration page.
 */
'use client';

import { useState } from 'react';
import { useForm } from 'react-hook-form';
import { zodResolver } from '@hookform/resolvers/zod';
import * as z from 'zod';
import Link from 'next/link';
import { useAuth } from '@/lib/auth';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';

import { AuthHeader } from "@/components/layout/auth-header";
import { useLanguage } from '@/contexts/language-context';

export default function RegisterPage() {
    const [error, setError] = useState('');
    const [loading, setLoading] = useState(false);
    const { register: registerUser } = useAuth();
    const { t } = useLanguage();

    const registerSchema = z.object({
        email: z.string().email(t('Invalid email address')),
        password: z.string().min(8, t('Password must be at least 8 characters')),
        first_name: z.string().min(2, t('register.first_name', 'First name is required')),
        last_name: z.string().min(2, t('register.last_name', 'Last name is required')),
        phone: z.string().optional(),
        company_name: z.string().min(2, t('register.company_name', 'Company name is required')),
        company_subdomain: z
            .string()
            .min(3, t('Subdomain must be at least 3 characters'))
            .regex(/^[a-z0-9-]+$/, t('Subdomain must contain only lowercase letters, numbers, and hyphens')),
        address: z.string().optional(),
        rccm_number: z.string().optional(),
    });

    type RegisterFormData = z.infer<typeof registerSchema>;

    const {
        register,
        handleSubmit,
        formState: { errors },
    } = useForm<RegisterFormData>({
        resolver: zodResolver(registerSchema),
    });

    const onSubmit = async (data: RegisterFormData) => {
        setError('');
        setLoading(true);

        try {
            await registerUser(data);
        } catch (err: any) {
            console.error("Registration error:", err);
            const detail = err.response?.data?.detail;
            // Fallback to message or generic error
            setError(detail || err.message || t('Registration failed. Please try again.'));
        } finally {
            setLoading(false);
        }
    };

    return (
        <div className="flex min-h-screen items-center justify-center bg-gray-50 px-4 py-12 sm:px-6 lg:px-8 relative">
            <AuthHeader />
            <Card className="w-full max-w-2xl">
                <CardHeader className="space-y-1">
                    <CardTitle className="text-2xl font-bold text-center">{t('register.title', 'Create an Account')}</CardTitle>
                    <CardDescription className="text-center">
                        {t('register.subtitle', 'Register your insurance company and start managing policies')}
                    </CardDescription>
                </CardHeader>
                <CardContent>
                    <form onSubmit={handleSubmit(onSubmit)} className="space-y-4">
                        {error && (
                            <div className="rounded-md bg-red-50 p-3 text-sm text-red-800">
                                {error}
                            </div>
                        )}

                        <div className="grid grid-cols-1 gap-4 sm:grid-cols-2">
                            <div className="space-y-2">
                                <Label htmlFor="first_name">{t('register.first_name', 'First Name')}</Label>
                                <Input
                                    id="first_name"
                                    placeholder="John"
                                    {...register('first_name')}
                                    className={errors.first_name ? 'border-red-500' : ''}
                                />
                                {errors.first_name && (
                                    <p className="text-sm text-red-600">{errors.first_name.message}</p>
                                )}
                            </div>

                            <div className="space-y-2">
                                <Label htmlFor="last_name">{t('register.last_name', 'Last Name')}</Label>
                                <Input
                                    id="last_name"
                                    placeholder="Doe"
                                    {...register('last_name')}
                                    className={errors.last_name ? 'border-red-500' : ''}
                                />
                                {errors.last_name && (
                                    <p className="text-sm text-red-600">{errors.last_name.message}</p>
                                )}
                            </div>
                        </div>

                        <div className="space-y-2">
                            <Label htmlFor="email">{t('register.email', 'Email')}</Label>
                            <Input
                                id="email"
                                type="email"
                                placeholder="you@company.com"
                                {...register('email')}
                                className={errors.email ? 'border-red-500' : ''}
                            />
                            {errors.email && (
                                <p className="text-sm text-red-600">{errors.email.message}</p>
                            )}
                        </div>

                        <div className="space-y-2">
                            <Label htmlFor="password">{t('register.password', 'Password')}</Label>
                            <Input
                                id="password"
                                type="password"
                                placeholder="••••••••"
                                {...register('password')}
                                className={errors.password ? 'border-red-500' : ''}
                            />
                            {errors.password && (
                                <p className="text-sm text-red-600">{errors.password.message}</p>
                            )}
                        </div>

                        <div className="space-y-2">
                            <Label htmlFor="phone">{t('register.phone', 'Phone')} ({t('register.optional', 'Optional')})</Label>
                            <Input
                                id="phone"
                                type="tel"
                                placeholder="+225 07 00 00 00 00"
                                {...register('phone')}
                            />
                        </div>

                        <div className="space-y-2">
                            <Label htmlFor="address">{t('register.address', 'Address')} ({t('register.optional', 'Optional')})</Label>
                            <Input
                                id="address"
                                placeholder={t('123 Main St, City')}
                                {...register('address')}
                            />
                        </div>

                        <div className="border-t pt-4">
                            <h3 className="mb-4 text-sm font-semibold">{t('register.company_info', 'Company Information')}</h3>

                            <div className="space-y-4">
                                <div className="space-y-2">
                                    <Label htmlFor="company_name">{t('register.company_name', 'Company Name')}</Label>
                                    <Input
                                        id="company_name"
                                        placeholder="ABC Insurance Co."
                                        {...register('company_name')}
                                        className={errors.company_name ? 'border-red-500' : ''}
                                    />
                                    {errors.company_name && (
                                        <p className="text-sm text-red-600">{errors.company_name.message}</p>
                                    )}
                                </div>

                                <div className="space-y-2">
                                    <Label htmlFor="rccm_number">{t('register.rccm', 'Company Number (N° RCCM)')} ({t('register.optional', 'Optional')})</Label>
                                    <Input
                                        id="rccm_number"
                                        placeholder="RCCM-123456"
                                        {...register('rccm_number')}
                                    />
                                </div>

                                <div className="space-y-2">
                                    <Label htmlFor="company_subdomain">{t('register.subdomain', 'Company Subdomain')}</Label>
                                    <div className="flex">
                                        <Input
                                            id="company_subdomain"
                                            placeholder="abc-insurance"
                                            {...register('company_subdomain')}
                                            className={errors.company_subdomain ? 'border-red-500' : ''}
                                        />
                                        <span className="ml-2 flex items-center text-sm text-gray-500">
                                            .Tinsur.AI.com
                                        </span>
                                    </div>
                                    {errors.company_subdomain && (
                                        <p className="text-sm text-red-600">{errors.company_subdomain.message}</p>
                                    )}
                                    <p className="text-xs text-gray-500">
                                        {t('register.subdomain_desc', 'This will be your unique company identifier')}
                                    </p>
                                </div>
                            </div>
                        </div>

                        <Button type="submit" className="w-full" disabled={loading}>
                            {loading ? t('Creating account...') : t('register.create_btn', 'Create Account')}
                        </Button>

                        <div className="text-center text-sm">
                            <span className="text-gray-600">{t('register.already_have_account', 'Already have an account?')} </span>
                            <Link href="/login" className="font-medium text-blue-600 hover:text-blue-500">
                                {t('register.sign_in_link', 'Sign in')}
                            </Link>
                        </div>
                    </form>
                </CardContent>
            </Card>
        </div>
    );
}
