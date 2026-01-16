/**
 * Login page.
 */
'use client';

import { useState } from 'react';
import { useForm } from 'react-hook-form';
import { zodResolver } from '@hookform/resolvers/zod';
import * as z from 'zod';
import Link from 'next/link';
import { useAuth } from '@/lib/auth';
import { useLanguage } from '@/contexts/language-context';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';


type LoginFormData = z.infer<typeof baseSchema>;

// Define schema outside initially for type inference, but we will recreate it inside for translation
const baseSchema = z.object({
    email: z.string().email(),
    password: z.string().min(6),
});


export default function LoginPage() {
    const [error, setError] = useState('');
    const [loading, setLoading] = useState(false);
    const { login } = useAuth();
    const { t } = useLanguage();

    // specific schema with translated messages
    const loginSchema = z.object({
        email: z.string().email(t('Invalid email address')),
        password: z.string().min(6, t('Password must be at least 6 characters')),
    });

    const {
        register,
        handleSubmit,
        formState: { errors },
    } = useForm<LoginFormData>({
        resolver: zodResolver(loginSchema),
    });

    const onSubmit = async (data: LoginFormData) => {
        setError('');
        setLoading(true);

        try {
            await login(data);
        } catch (err: any) {
            console.error(err);
            const detail = err.response?.data?.detail;
            const status = err.response?.status;
            setError(detail ? `(${status}) ${detail}` : `Connection Error: ${err.message}`);
        } finally {
            setLoading(false);
        }
    };

    return (
        <div className="flex min-h-screen items-center justify-center bg-gray-50 px-4 py-12 sm:px-6 lg:px-8">
            <Card className="w-full max-w-md">
                <CardHeader className="space-y-1">
                    <CardTitle className="text-2xl font-bold text-center" suppressHydrationWarning>{t('Welcome Back')}</CardTitle>
                    <CardDescription className="text-center">
                        {t('Sign in to your Insurance SaaS account')}
                    </CardDescription>
                </CardHeader>
                <CardContent>
                    <form onSubmit={handleSubmit(onSubmit)} className="space-y-4">
                        {error && (
                            <div className="rounded-md bg-red-50 p-3 text-sm text-red-800">
                                {error}
                            </div>
                        )}

                        <div className="space-y-2">
                            <Label htmlFor="email">{t('Email')}</Label>
                            <Input
                                id="email"
                                type="email"
                                placeholder="you@example.com"
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

                        <Button type="submit" className="w-full" disabled={loading}>
                            {loading ? t('Signing in...') : t('Sign In')}
                        </Button>

                        <div className="text-center text-sm">
                            <span className="text-gray-600">{t("Don't have an account? ")}</span>
                            <Link href="/register" className="font-medium text-blue-600 hover:text-blue-500">
                                {t('Register now')}
                            </Link>
                        </div>
                    </form>
                </CardContent>
            </Card>
        </div>
    );
}
