'use client';

import { useState, useEffect } from 'react';
import { useForm } from 'react-hook-form';
import { zodResolver } from '@hookform/resolvers/zod';
import * as z from 'zod';
import { useLanguage } from '@/contexts/language-context';
import { portalApi } from '@/lib/portal-api';
import { useToast } from '@/components/ui/use-toast';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { Switch } from '@/components/ui/switch';
import { Card, CardContent, CardDescription, CardHeader, CardTitle, CardFooter } from '@/components/ui/card';
import { Loader2, User, Phone, MapPin, Lock, ShieldAlert, Trash2, KeyRound } from 'lucide-react';
import {
    AlertDialog,
    AlertDialogAction,
    AlertDialogCancel,
    AlertDialogContent,
    AlertDialogDescription,
    AlertDialogFooter,
    AlertDialogHeader,
    AlertDialogTitle,
    AlertDialogTrigger,
} from "@/components/ui/alert-dialog";
import { useAuth } from '@/lib/auth';

// --- Schemas ---

const profileSchema = z.object({
    first_name: z.string().min(2, 'First name is too short'),
    last_name: z.string().min(2, 'Last name is too short'),
    phone: z.string().min(5, 'Phone number is too short').optional().or(z.literal('')),
    address: z.string().optional().or(z.literal('')),
    city: z.string().optional().or(z.literal('')),
});

const passwordSchema = z.object({
    current_password: z.string().min(1, 'Current password is required'),
    new_password: z.string().min(8, 'Password must be at least 8 characters'),
    confirm_password: z.string().min(8, 'Password must be at least 8 characters'),
}).refine((data) => data.new_password === data.confirm_password, {
    message: "Passwords don't match",
    path: ["confirm_password"],
});

type ProfileFormData = z.infer<typeof profileSchema>;
type PasswordFormData = z.infer<typeof passwordSchema>;

export function PortalSettingsTab() {
    const { t } = useLanguage();
    const { toast } = useToast();
    const { logout } = useAuth();

    const [isLoading, setIsLoading] = useState(true);
    const [isSavingProfile, setIsSavingProfile] = useState(false);
    const [isSavingPassword, setIsSavingPassword] = useState(false);
    const [isDeleting, setIsDeleting] = useState(false);
    const [mfaEnabled, setMfaEnabled] = useState(false);

    // Profile Form
    const { register: registerProfile, handleSubmit: handleSubmitProfile, setValue: setValueProfile, formState: { errors: errorsProfile } } = useForm<ProfileFormData>({
        resolver: zodResolver(profileSchema)
    });

    // Password Form
    const { register: registerPassword, handleSubmit: handleSubmitPassword, reset: resetPassword, formState: { errors: errorsPassword } } = useForm<PasswordFormData>({
        resolver: zodResolver(passwordSchema)
    });

    useEffect(() => {
        const fetchProfile = async () => {
            try {
                const data = await portalApi.getProfile();
                setValueProfile('first_name', data.first_name);
                setValueProfile('last_name', data.last_name);
                setValueProfile('phone', data.phone || '');
                setValueProfile('address', data.address || '');
                setValueProfile('city', data.city || '');
                setMfaEnabled(data.mfa_enabled);
            } catch (error) {
                console.error("Failed to fetch profile", error);
                toast({
                    title: "Error",
                    description: "Failed to load profile details",
                    variant: "destructive"
                });
            } finally {
                setIsLoading(false);
            }
        };
        fetchProfile();
    }, [setValueProfile, toast]);

    const onUpdateProfile = async (data: ProfileFormData) => {
        setIsSavingProfile(true);
        try {
            await portalApi.updateProfile(data);
            toast({
                title: t('settings.profile_updated', "Profile Updated"),
                description: t('settings.profile_updated_desc', "Your personal details have been saved."),
            });
        } catch (error) {
            toast({
                title: "Error",
                description: "Failed to update profile",
                variant: "destructive"
            });
        } finally {
            setIsSavingProfile(false);
        }
    };

    const onChangePassword = async (data: PasswordFormData) => {
        setIsSavingPassword(true);
        try {
            await portalApi.changePassword({
                current_password: data.current_password,
                new_password: data.new_password
            });
            toast({
                title: t('settings.password_changed', "Password Changed"),
                description: t('settings.password_changed_desc', "Your password has been updated successfully."),
            });
            resetPassword();
        } catch (error: any) {
            toast({
                title: "Error",
                description: error.response?.data?.detail || "Failed to change password",
                variant: "destructive"
            });
        } finally {
            setIsSavingPassword(false);
        }
    };

    const onToggleMFA = async (checked: boolean) => {
        try {
            await portalApi.toggle2FA({ enabled: checked });
            setMfaEnabled(checked);
            toast({
                title: checked ? t('settings.2fa_enabled', "2FA Enabled") : t('settings.2fa_disabled', "2FA Disabled"),
                description: checked
                    ? t('settings.2fa_enabled_desc', "Two-factor authentication is now active.")
                    : t('settings.2fa_disabled_desc', "Two-factor authentication has been disabled."),
            });
        } catch (error) {
            // Revert switch on error
            setMfaEnabled(!checked);
            toast({
                title: "Error",
                description: "Failed to update 2FA settings",
                variant: "destructive"
            });
        }
    };

    const onDeleteAccount = async () => {
        setIsDeleting(true);
        try {
            await portalApi.deleteAccount();
            toast({
                title: t('settings.account_deleted', "Account Deleted"),
                description: t('settings.account_deleted_desc', "Your account has been deactivated. Logging out..."),
            });
            setTimeout(() => {
                logout();
            }, 2000);
        } catch (error) {
            setIsDeleting(false);
            toast({
                title: "Error",
                description: "Failed to delete account",
                variant: "destructive"
            });
        }
    };

    if (isLoading) {
        return (
            <div className="flex justify-center items-center py-20">
                <Loader2 className="h-8 w-8 animate-spin text-gray-400" />
            </div>
        );
    }

    return (
        <div className="space-y-8 animate-in fade-in duration-500 max-w-5xl mx-auto">
            <div className="mb-6">
                <h2 className="text-3xl font-black text-gray-900">{t('settings.title', 'Account Settings')}</h2>
                <p className="text-gray-500 font-bold">{t('settings.subtitle', 'Manage your personal information and security preferences.')}</p>
            </div>

            <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
                {/* 1. Edit Details */}
                <Card className="lg:col-span-2 border-gray-100 shadow-sm rounded-[25px]">
                    <CardHeader>
                        <CardTitle className="flex items-center gap-2">
                            <User className="h-5 w-5 text-[#00539F]" />
                            {t('settings.personal_info', 'Personal Information')}
                        </CardTitle>
                        <CardDescription>
                            {t('settings.personal_info_desc', 'Update your contact details and address.')}
                        </CardDescription>
                    </CardHeader>
                    <form onSubmit={handleSubmitProfile(onUpdateProfile)}>
                        <CardContent className="space-y-4">
                            <div className="grid grid-cols-2 gap-4">
                                <div className="space-y-2">
                                    <Label htmlFor="first_name">{t('register.first_name', 'First Name')}</Label>
                                    <Input id="first_name" {...registerProfile('first_name')} />
                                    {errorsProfile.first_name && <p className="text-xs text-red-500">{errorsProfile.first_name.message}</p>}
                                </div>
                                <div className="space-y-2">
                                    <Label htmlFor="last_name">{t('register.last_name', 'Last Name')}</Label>
                                    <Input id="last_name" {...registerProfile('last_name')} />
                                    {errorsProfile.last_name && <p className="text-xs text-red-500">{errorsProfile.last_name.message}</p>}
                                </div>
                            </div>
                            <div className="space-y-2">
                                <Label htmlFor="phone">{t('register.phone', 'Phone Number')}</Label>
                                <div className="relative">
                                    <Phone className="absolute left-3 top-3 h-4 w-4 text-gray-400" />
                                    <Input id="phone" className="pl-9" {...registerProfile('phone')} />
                                </div>
                                {errorsProfile.phone && <p className="text-xs text-red-500">{errorsProfile.phone.message}</p>}
                            </div>
                            <div className="grid grid-cols-3 gap-4">
                                <div className="col-span-2 space-y-2">
                                    <Label htmlFor="address">{t('common.address', 'Address')}</Label>
                                    <div className="relative">
                                        <MapPin className="absolute left-3 top-3 h-4 w-4 text-gray-400" />
                                        <Input id="address" className="pl-9" {...registerProfile('address')} />
                                    </div>
                                </div>
                                <div className="space-y-2">
                                    <Label htmlFor="city">{t('common.city', 'City')}</Label>
                                    <Input id="city" {...registerProfile('city')} />
                                </div>
                            </div>
                        </CardContent>
                        <CardFooter className="bg-gray-50/50 rounded-b-[25px] flex justify-end py-4">
                            <Button type="submit" disabled={isSavingProfile} className="bg-[#00539F] hover:bg-[#004380] text-white font-bold rounded-full">
                                {isSavingProfile && <Loader2 className="mr-2 h-4 w-4 animate-spin" />}
                                {t('common.save_changes', 'Save Changes')}
                            </Button>
                        </CardFooter>
                    </form>
                </Card>

                {/* 2. Security & Account */}
                <div className="space-y-8">
                    {/* Security */}
                    <Card className="border-gray-100 shadow-sm rounded-[25px]">
                        <CardHeader>
                            <CardTitle className="flex items-center gap-2">
                                <Lock className="h-5 w-5 text-[#00539F]" />
                                {t('settings.security', 'Security')}
                            </CardTitle>
                        </CardHeader>
                        <CardContent className="space-y-6">
                            {/* 2FA Toggle */}
                            <div className="flex items-center justify-between">
                                <div className="space-y-0.5">
                                    <Label className="text-base font-bold">{t('settings.2fa', 'Two-factor Authentication')}</Label>
                                    <p className="text-xs text-gray-500">{t('settings.2fa_help', 'Add an extra layer of security.')}</p>
                                </div>
                                <Switch
                                    checked={mfaEnabled}
                                    onCheckedChange={onToggleMFA}
                                />
                            </div>

                            <hr className="border-gray-100" />

                            {/* Change Password */}
                            <form onSubmit={handleSubmitPassword(onChangePassword)} className="space-y-4">
                                <div className="space-y-2">
                                    <Label htmlFor="current_password">{t('settings.current_password', 'Current Password')}</Label>
                                    <Input id="current_password" type="password" {...registerPassword('current_password')} />
                                    {errorsPassword.current_password && <p className="text-xs text-red-500">{errorsPassword.current_password.message}</p>}
                                </div>
                                <div className="space-y-2">
                                    <Label htmlFor="new_password">{t('settings.new_password', 'New Password')}</Label>
                                    <Input id="new_password" type="password" {...registerPassword('new_password')} />
                                    {errorsPassword.new_password && <p className="text-xs text-red-500">{errorsPassword.new_password.message}</p>}
                                </div>
                                <div className="space-y-2">
                                    <Label htmlFor="confirm_password">{t('settings.confirm_password', 'Confirm New Password')}</Label>
                                    <Input id="confirm_password" type="password" {...registerPassword('confirm_password')} />
                                    {errorsPassword.confirm_password && <p className="text-xs text-red-500">{errorsPassword.confirm_password.message}</p>}
                                </div>

                                <Button type="submit" disabled={isSavingPassword} variant="outline" className="w-full font-bold border-gray-200">
                                    {isSavingPassword ? <Loader2 className="mr-2 h-4 w-4 animate-spin" /> : <KeyRound className="mr-2 h-4 w-4" />}
                                    {t('settings.change_password', 'Update Password')}
                                </Button>
                            </form>
                        </CardContent>
                    </Card>

                    {/* Danger Zone */}
                    <Card className="border-red-100 bg-red-50/30 shadow-sm rounded-[25px]">
                        <CardHeader>
                            <CardTitle className="flex items-center gap-2 text-red-600">
                                <ShieldAlert className="h-5 w-5" />
                                {t('settings.danger_zone', 'Danger Zone')}
                            </CardTitle>
                        </CardHeader>
                        <CardContent>
                            <AlertDialog>
                                <AlertDialogTrigger asChild>
                                    <Button variant="destructive" className="w-full font-bold bg-red-600 hover:bg-red-700 rounded-full">
                                        <Trash2 className="mr-2 h-4 w-4" />
                                        {t('settings.delete_account', 'Delete My Account')}
                                    </Button>
                                </AlertDialogTrigger>
                                <AlertDialogContent className="rounded-[20px]">
                                    <AlertDialogHeader>
                                        <AlertDialogTitle>{t('settings.delete_confirm_title', 'Are you absolutely sure?')}</AlertDialogTitle>
                                        <AlertDialogDescription>
                                            {t('settings.delete_confirm_desc', 'This action cannot be undone. This will permanently deactivate your account and access to the portal.')}
                                        </AlertDialogDescription>
                                    </AlertDialogHeader>
                                    <AlertDialogFooter>
                                        <AlertDialogCancel className="rounded-full font-bold">{t('common.cancel', 'Cancel')}</AlertDialogCancel>
                                        <AlertDialogAction onClick={onDeleteAccount} className="bg-red-600 hover:bg-red-700 rounded-full font-bold">
                                            {isDeleting ? <Loader2 className="animate-spin h-4 w-4" /> : t('common.confirm_delete', 'Yes, Delete Account')}
                                        </AlertDialogAction>
                                    </AlertDialogFooter>
                                </AlertDialogContent>
                            </AlertDialog>
                        </CardContent>
                    </Card>
                </div>
            </div>
        </div>
    );
}
