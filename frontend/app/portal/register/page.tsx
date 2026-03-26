'use client';

import { useState, useEffect } from 'react';
import { useForm } from 'react-hook-form';
import { zodResolver } from '@hookform/resolvers/zod';
import * as z from 'zod';
import Link from 'next/link';
import { useRouter, useSearchParams } from 'next/navigation';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { Card, CardContent, CardDescription, CardHeader, CardTitle, CardFooter } from '@/components/ui/card';
import { ShieldCheck, Scan, User, Lock, Mail, Phone, CheckCircle2, Loader2, ArrowRight, ArrowLeft } from 'lucide-react';
import { portalApi } from '@/lib/portal-api';
import { clientApi } from '@/lib/client-api';
import { useToast } from '@/components/ui/use-toast';
import { formatApiError } from '@/lib/api';
import { useLanguage } from '@/contexts/language-context';

const registerSchema = z.object({
    email: z.string().email('Invalid email address'),
    password: z.string().min(8, 'Password must be at least 8 characters'),
    first_name: z.string().min(2, 'First name is required'),
    last_name: z.string().min(2, 'Last name is required'),
    phone: z.string().min(1, 'Phone is required'),
    client_type: z.enum(['individual', 'corporate']).default('individual'),
    id_number: z.string().optional(),
    date_of_birth: z.string().optional(),
    nationality: z.string().optional(),
    referral_code: z.string().optional(),
});

type RegisterFormData = z.infer<typeof registerSchema>;

export default function ClientRegisterPage() {
    const { t } = useLanguage();
    const [step, setStep] = useState(1);
    const [error, setError] = useState('');
    const [loading, setLoading] = useState(false);
    const [isScanning, setIsScanning] = useState(false);
    const [registrationSuccess, setRegistrationSuccess] = useState(false);

    const router = useRouter();
    const searchParams = useSearchParams();
    const { toast } = useToast();

    const companyId = searchParams.get('company_id');
    const subdomain = searchParams.get('subdomain');
    const urlReferral = searchParams.get('ref');

    const {
        register,
        handleSubmit,
        setValue,
        watch,
        formState: { errors, isValid },
    } = useForm<RegisterFormData>({
        resolver: zodResolver(registerSchema) as any,
        mode: 'onChange',
        defaultValues: {
            client_type: 'individual',
            referral_code: urlReferral || ''
        }
    });

    useEffect(() => {
        if (urlReferral) {
            setValue('referral_code', urlReferral);
        }
    }, [urlReferral, setValue]);

    const handleIdScan = async (e: React.ChangeEvent<HTMLInputElement>) => {
        const file = e.target.files?.[0];
        if (!file) return;

        setIsScanning(true);
        setError('');
        try {
            const result = await clientApi.uploadAndParseKycDocument(file, 'identity_document');

            if (result.full_name) {
                const parts = result.full_name.split(' ');
                if (parts.length > 1) {
                    setValue('first_name', parts[0], { shouldValidate: true });
                    setValue('last_name', parts.slice(1).join(' '), { shouldValidate: true });
                } else {
                    setValue('first_name', result.full_name, { shouldValidate: true });
                }
            }
            if (result.id_number) setValue('id_number', result.id_number, { shouldValidate: true });
            if (result.dob) setValue('date_of_birth', result.dob, { shouldValidate: true });
            if (result.nationality) setValue('nationality', result.nationality, { shouldValidate: true });

            toast({
                title: t('register.id_scanned', "ID Scanned"),
                description: t('register.id_scanned_desc', "Information successfully extracted and filled."),
            });
        } catch (err: any) {
            setError(formatApiError(err.response?.data?.detail) || "Failed to scan document. You can still fill it manually.");
        } finally {
            setIsScanning(false);
        }
    };

    const onSubmit = async (data: RegisterFormData) => {
        setError('');
        setLoading(true);

        try {
            await portalApi.registerClient({
                ...data,
                company_id: companyId,
                subdomain: subdomain || (typeof window !== 'undefined' ? window.location.host.split('.')[0] : undefined)
            });
            setRegistrationSuccess(true);
        } catch (err: any) {
            setError(formatApiError(err.response?.data?.detail) || t('register.failed', 'Registration failed'));
        } finally {
            setLoading(false);
        }
    };

    if (registrationSuccess) {
        return (
            <div className="flex min-h-screen items-center justify-center bg-slate-50 px-4">
                <Card className="w-full max-w-md border-green-100 shadow-xl shadow-green-900/5">
                    <CardContent className="pt-12 text-center space-y-4">
                        <div className="mx-auto flex h-16 w-16 items-center justify-center rounded-full bg-green-100">
                            <CheckCircle2 className="h-10 w-10 text-green-600" />
                        </div>
                        <CardTitle className="text-2xl font-bold text-slate-900">{t('register.success_title', 'Registration Successful!')}</CardTitle>
                        <CardDescription className="text-slate-600 text-base">
                            {t('register.success_desc', 'Your account has been created. Your identity documents are currently under review.')}
                        </CardDescription>
                        <div className="pt-6">
                            <Button asChild className="w-full bg-blue-600 hover:bg-blue-700 h-11">
                                <Link href="/login">{t('register.sign_in', 'Sign in to your Portal')}</Link>
                            </Button>
                        </div>
                    </CardContent>
                </Card>
            </div>
        );
    }

    return (
        <div className="flex min-h-screen items-center justify-center bg-slate-50 px-4 py-12">
            <Card className="w-full max-w-xl border-slate-200 shadow-2xl">
                <CardHeader className="space-y-2 pb-8 text-center border-b bg-white rounded-t-xl">
                    <div className="mx-auto flex h-12 w-12 items-center justify-center rounded-full bg-blue-50 text-blue-600 mb-2">
                        <ShieldCheck className="h-6 w-6" />
                    </div>
                    <CardTitle className="text-3xl font-extrabold text-slate-900 tracking-tight">{t('register.portal_title', 'Portal Registration')}</CardTitle>
                    <CardDescription className="text-slate-500 font-medium">
                        {t('register.portal_desc', "Join your insurance provider's digital platform")}
                    </CardDescription>

                    {/* Stepper */}
                    <div className="flex items-center justify-center gap-2 pt-4">
                        <div className={`h-2 w-12 rounded-full ${step === 1 ? 'bg-blue-600' : 'bg-blue-100'}`} />
                        <div className={`h-2 w-12 rounded-full ${step === 2 ? 'bg-blue-600' : 'bg-blue-100'}`} />
                    </div>
                </CardHeader>

                <form onSubmit={handleSubmit(onSubmit)}>
                    <CardContent className="pt-8 space-y-6">
                        {error && (
                            <div className="rounded-lg bg-red-50 p-4 text-sm text-red-800 border border-red-100 font-medium">
                                {error}
                            </div>
                        )}

                        {step === 1 && (
                            <div className="space-y-6 animate-in fade-in slide-in-from-right-4 duration-300">
                                <div>
                                    <Label className="text-slate-700 font-bold mb-3 block">{t('register.ai_onboarding', 'AI Onboarding (Scan ID)')}</Label>
                                    <div className="relative group">
                                        <Input
                                            type="file"
                                            className="hidden"
                                            id="id-scan-portal"
                                            accept="image/*"
                                            onChange={handleIdScan}
                                            disabled={isScanning}
                                        />
                                        <label
                                            htmlFor="id-scan-portal"
                                            className={`flex flex-col items-center justify-center w-full h-32 border-2 border-dashed rounded-xl cursor-pointer transition-all
                                              ${isScanning ? 'bg-slate-50 border-blue-200' : 'bg-blue-50/30 border-blue-100 hover:border-blue-400 hover:bg-blue-50'}`}
                                        >
                                            {isScanning ? (
                                                <div className="flex flex-col items-center gap-2">
                                                    <Loader2 className="h-8 w-8 animate-spin text-blue-600" />
                                                    <span className="text-sm font-bold text-blue-700">{t('register.analyzing', 'Gemini is analyzing your document...')}</span>
                                                </div>
                                            ) : (
                                                <div className="flex flex-col items-center gap-2 text-blue-700">
                                                    <Scan className="h-8 w-8 text-blue-500" />
                                                    <span className="text-sm font-bold">{t('register.fast_track', 'Fast-track with ID/DL Photo')}</span>
                                                    <span className="text-[11px] text-slate-500">{t('register.auto_fill', 'Automatically fills your profile info')}</span>
                                                </div>
                                            )}
                                        </label>
                                    </div>
                                </div>

                                <div className="grid grid-cols-2 gap-4 pt-2">
                                    <div className="space-y-2">
                                        <Label htmlFor="first_name" className="text-slate-600 font-semibold">{t('register.first_name', 'First Name')}</Label>
                                        <div className="relative">
                                            <User className="absolute left-3 top-3 h-4 w-4 text-slate-400" />
                                            <Input
                                                id="first_name"
                                                placeholder="John"
                                                className="pl-9 h-11"
                                                {...register('first_name')}
                                            />
                                        </div>
                                        {errors.first_name && <p className="text-[11px] text-red-600 mt-1">{t(errors.first_name.message || '')}</p>}
                                    </div>
                                    <div className="space-y-2">
                                        <Label htmlFor="last_name" className="text-slate-600 font-semibold">{t('register.last_name', 'Last Name')}</Label>
                                        <Input
                                            id="last_name"
                                            placeholder="Doe"
                                            className="h-11"
                                            {...register('last_name')}
                                        />
                                        {errors.last_name && <p className="text-[11px] text-red-600 mt-1">{t(errors.last_name.message || '')}</p>}
                                    </div>
                                </div>

                                <div className="space-y-2">
                                    <Label htmlFor="phone" className="text-slate-600 font-semibold">{t('register.phone', 'Phone Number')}</Label>
                                    <div className="relative">
                                        <Phone className="absolute left-3 top-3 h-4 w-4 text-slate-400" />
                                        <Input
                                            id="phone"
                                            placeholder="+225 07 00 00 00 00"
                                            className="pl-9 h-11"
                                            {...register('phone')}
                                        />
                                    </div>
                                    {errors.phone && <p className="text-[11px] text-red-600 mt-1">{t(errors.phone.message || '')}</p>}
                                </div>

                                <div className="space-y-2">
                                    <Label htmlFor="id_number" className="text-slate-600 font-semibold">{t('register.id_number', 'ID Number (Extracted from Scan)')}</Label>
                                    <Input
                                        id="id_number"
                                        placeholder="C00000000"
                                        className="h-11 border-slate-200"
                                        readOnly={isScanning}
                                        {...register('id_number')}
                                    />
                                </div>
                            </div>
                        )}

                        {step === 2 && (
                            <div className="space-y-6 animate-in fade-in slide-in-from-right-4 duration-300">
                                <div className="space-y-2">
                                    <Label htmlFor="email" className="text-slate-600 font-semibold">{t('register.email', 'Email Address')}</Label>
                                    <div className="relative">
                                        <Mail className="absolute left-3 top-3 h-4 w-4 text-slate-400" />
                                        <Input
                                            id="email"
                                            type="email"
                                            placeholder="john.doe@example.com"
                                            className="pl-9 h-11"
                                            {...register('email')}
                                        />
                                    </div>
                                    {errors.email && <p className="text-[11px] text-red-600 mt-1">{t(errors.email.message || '')}</p>}
                                </div>

                                <div className="space-y-2">
                                    <Label htmlFor="password" className="text-slate-600 font-semibold">{t('register.password', 'Security Password')}</Label>
                                    <div className="relative">
                                        <Lock className="absolute left-3 top-3 h-4 w-4 text-slate-400" />
                                        <Input
                                            id="password"
                                            type="password"
                                            placeholder="••••••••"
                                            className="pl-9 h-11"
                                            {...register('password')}
                                        />
                                    </div>
                                    {errors.password && <p className="text-[11px] text-red-600 mt-1">{t(errors.password.message || '')}</p>}
                                </div>

                                <div className="space-y-2">
                                    <Label htmlFor="referral_code" className="text-slate-600 font-semibold text-xs flex justify-between">
                                        {t('register.referral', 'Referral Code (Optional)')}
                                        {watch('referral_code') && <span className="text-blue-600 flex items-center gap-1"><CheckCircle2 className="h-3 w-3" /> {t('register.applied', 'Applied')}</span>}
                                    </Label>
                                    <Input
                                        id="referral_code"
                                        placeholder="REF-12345"
                                        className="h-10 text-sm"
                                        {...register('referral_code')}
                                    />
                                    <p className="text-[10px] text-slate-400">{t('register.referral_hint', 'If a friend referred you, enter their code for bonus points.')}</p>
                                </div>

                                <div className="bg-slate-50 p-4 rounded-lg border border-slate-100 flex gap-3">
                                    <ShieldCheck className="h-5 w-5 text-blue-500 mt-0.5" />
                                    <div>
                                        <p className="text-xs font-bold text-slate-700">{t('register.id_verification', 'Digital Identity Verification')}</p>
                                        <p className="text-[10px] text-slate-500">{t('register.terms', 'By registering, you agree to our terms of service and consent to the automated processing of your ID information for compliance checks.')}</p>
                                    </div>
                                </div>
                            </div>
                        )}
                    </CardContent>

                    <CardFooter className="pt-4 pb-8 flex justify-between gap-3">
                        {step === 1 ? (
                            <Button
                                type="button"
                                variant="outline"
                                className="w-1/3 h-11"
                                asChild
                            >
                                <Link href="/login">{t('register.back_login', 'Back to Login')}</Link>
                            </Button>
                        ) : (
                            <Button
                                type="button"
                                variant="outline"
                                className="w-1/3 h-11"
                                onClick={() => setStep(1)}
                            >
                                <ArrowLeft className="h-4 w-4 mr-2" /> {t('common.previous', 'Previous')}
                            </Button>
                        )}

                        {step === 1 ? (
                            <Button
                                type="button"
                                className="flex-1 bg-blue-600 hover:bg-blue-700 h-11"
                                onClick={() => setStep(2)}
                                disabled={!watch('first_name') || !watch('last_name') || !watch('phone')}
                            >
                                {t('register.next_step', 'Next Step')} <ArrowRight className="h-4 w-4 ml-2" />
                            </Button>
                        ) : (
                            <Button
                                type="submit"
                                className="flex-1 bg-blue-600 hover:bg-blue-700 h-11"
                                disabled={loading || !isValid}
                            >
                                {loading ? (
                                    <>
                                        <Loader2 className="h-4 w-4 mr-2 animate-spin" /> {t('register.finalizing', 'Finalizing Account...')}
                                    </>
                                ) : t('register.complete', 'Complete Registration')}
                            </Button>
                        )}
                    </CardFooter>
                </form>
            </Card>
        </div>
    );
}
