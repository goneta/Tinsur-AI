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

import { LanguageSwitcher } from '@/components/language-switcher';
import { useLanguage } from '@/contexts/language-context';

export default function RegisterPage() {
    const [error, setError] = useState('');
    const [loading, setLoading] = useState(false);
    const { register: registerUser } = useAuth();
    const { t } = useLanguage();

    const registerSchema = z.object({
        email: z.string().email(t('Invalid email address')),
        password: z.string().min(8, t('Password must be at least 8 characters')),
        first_name: z.string().min(2, t('First name is required')),
        last_name: z.string().min(2, t('Last name is required')),
        phone: z.string().optional(),
        company_name: z.string().min(2, t('Company name is required')),
        company_subdomain: z
            .string()
            .min(3, t('Subdomain must be at least 3 characters'))
            .regex(/^[a-z0-9-]+$/, t('Subdomain must contain only lowercase letters, numbers, and hyphens')),
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
            <div className="absolute top-4 right-4">
                <LanguageSwitcher />
            </div>
            <Card className="w-full max-w-2xl">
                <CardHeader className="space-y-1">
                    <CardTitle className="text-2xl font-bold text-center">{t('Create an Account')}</CardTitle>
                    <CardDescription className="text-center">
                        {t('Register your insurance company and start managing policies')}
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
                                <Label htmlFor="first_name">{t('First Name')}</Label>
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
                                <Label htmlFor="last_name">{t('Last Name')}</Label>
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
                            <Label htmlFor="email">{t('Email')}</Label>
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
                            <Label htmlFor="password">{t('Password')}</Label>
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
                            <Label htmlFor="phone">{t('Phone')} ({t('Optional')})</Label>
                            <Input
                                id="phone"
                                type="tel"
                                placeholder="+225 07 00 00 00 00"
                                {...register('phone')}
                            />
                        </div>

                        <div className="border-t pt-4">
                            <h3 className="mb-4 text-sm font-semibold">{t('Company Information')}</h3>

                            <div className="space-y-4">
                                <div className="space-y-2">
                                    <Label htmlFor="company_name">{t('Company Name')}</Label>
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
                                    <Label htmlFor="company_subdomain">{t('Company Subdomain')}</Label>
                                    <div className="flex">
                                        <Input
                                            id="company_subdomain"
                                            placeholder="abc-insurance"
                                            {...register('company_subdomain')}
                                            className={errors.company_subdomain ? 'border-red-500' : ''}
                                        />
                                        <span className="ml-2 flex items-center text-sm text-gray-500">
                                            .insurancesaas.com
                                        </span>
                                    </div>
                                    {errors.company_subdomain && (
                                        <p className="text-sm text-red-600">{errors.company_subdomain.message}</p>
                                    )}
                                    <p className="text-xs text-gray-500">
                                        {t('This will be your unique company identifier')}
                                    </p>
                                </div>
                            </div>
                        </div>

                        <Button type="submit" className="w-full" disabled={loading}>
                            {loading ? t('Creating account...') : t('Create Account')}
                        </Button>

                        <div className="text-center text-sm">
                            <span className="text-gray-600">{t('Already have an account?')} </span>
                            <Link href="/login" className="font-medium text-blue-600 hover:text-blue-500">
                                {t('Sign in')}
                            </Link>
                        </div>
                    </form>
                </CardContent>
            </Card>
        </div>
    );
}
