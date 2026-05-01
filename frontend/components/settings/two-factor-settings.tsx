'use client';

import { useState, useEffect } from 'react';
import { Shield, ShieldCheck, ShieldOff, Loader2, Copy, Check, RefreshCw } from 'lucide-react';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import {
    Card,
    CardContent,
    CardDescription,
    CardHeader,
    CardTitle,
} from '@/components/ui/card';
import { useToast } from '@/components/ui/use-toast';
import { useLanguage } from '@/contexts/language-context';
import api from '@/lib/api';

interface TwoFAStatus {
    mfa_enabled: boolean;
}

interface SetupData {
    qr_code: string; // base64 PNG
    secret: string;
    backup_codes: string[];
}

export function TwoFactorSettings() {
    const { t } = useLanguage();
    const { toast } = useToast();

    const [enabled, setEnabled] = useState(false);
    const [loading, setLoading] = useState(true);
    const [setupData, setSetupData] = useState<SetupData | null>(null);
    const [verifyCode, setVerifyCode] = useState('');
    const [verifying, setVerifying] = useState(false);
    const [disableCode, setDisableCode] = useState('');
    const [disabling, setDisabling] = useState(false);
    const [backupCodes, setBackupCodes] = useState<string[]>([]);
    const [copiedSecret, setCopiedSecret] = useState(false);

    useEffect(() => {
        fetchStatus();
    }, []);

    const fetchStatus = async () => {
        setLoading(true);
        try {
            const res = await api.get<TwoFAStatus>('/users/me');
            setEnabled(res.data.mfa_enabled);
        } catch {
            // silently fail
        } finally {
            setLoading(false);
        }
    };

    const handleStartSetup = async () => {
        try {
            const res = await api.post<SetupData>('/2fa/setup');
            setSetupData(res.data);
        } catch (err: any) {
            toast({
                title: t('settings.2fa.setup_error', 'Setup failed'),
                description: err.response?.data?.detail || t('common.error.try_again', 'Please try again.'),
                variant: 'destructive',
            });
        }
    };

    const handleVerify = async () => {
        if (!verifyCode || verifyCode.length !== 6) return;
        setVerifying(true);
        try {
            await api.post('/2fa/verify-setup', { code: verifyCode });
            setEnabled(true);
            setSetupData(null);
            setVerifyCode('');
            toast({
                title: t('settings.2fa.enabled_title', '2FA Enabled'),
                description: t('settings.2fa.enabled_desc', 'Two-factor authentication is now active on your account.'),
            });
        } catch (err: any) {
            toast({
                title: t('settings.2fa.invalid_code', 'Invalid Code'),
                description: err.response?.data?.detail || t('settings.2fa.code_hint', 'Enter the 6-digit code from your authenticator app.'),
                variant: 'destructive',
            });
        } finally {
            setVerifying(false);
        }
    };

    const handleDisable = async () => {
        if (!disableCode || disableCode.length !== 6) return;
        setDisabling(true);
        try {
            await api.post('/2fa/disable', { code: disableCode });
            setEnabled(false);
            setDisableCode('');
            toast({
                title: t('settings.2fa.disabled_title', '2FA Disabled'),
                description: t('settings.2fa.disabled_desc', 'Two-factor authentication has been removed from your account.'),
            });
        } catch (err: any) {
            toast({
                title: t('settings.2fa.invalid_code', 'Invalid Code'),
                description: err.response?.data?.detail || t('settings.2fa.code_hint', 'Enter the 6-digit code from your authenticator app.'),
                variant: 'destructive',
            });
        } finally {
            setDisabling(false);
        }
    };

    const handleRegenerateBackupCodes = async () => {
        try {
            const res = await api.post<{ backup_codes: string[] }>('/2fa/backup-codes');
            setBackupCodes(res.data.backup_codes);
            toast({
                title: t('settings.2fa.backup_regenerated', 'Backup Codes Regenerated'),
                description: t('settings.2fa.backup_save_hint', 'Save these codes in a safe place. Each can only be used once.'),
            });
        } catch (err: any) {
            toast({
                title: t('common.error', 'Error'),
                description: err.response?.data?.detail || t('common.error.try_again', 'Please try again.'),
                variant: 'destructive',
            });
        }
    };

    const copySecret = (text: string) => {
        navigator.clipboard.writeText(text);
        setCopiedSecret(true);
        setTimeout(() => setCopiedSecret(false), 2000);
    };

    if (loading) {
        return (
            <Card>
                <CardHeader>
                    <CardTitle className="flex items-center gap-2">
                        <Shield className="h-5 w-5" />
                        {t('settings.2fa.title', 'Two-Factor Authentication')}
                    </CardTitle>
                </CardHeader>
                <CardContent className="flex justify-center py-8">
                    <Loader2 className="h-6 w-6 animate-spin text-muted-foreground" />
                </CardContent>
            </Card>
        );
    }

    return (
        <Card>
            <CardHeader>
                <CardTitle className="flex items-center gap-2">
                    {enabled
                        ? <ShieldCheck className="h-5 w-5 text-green-500" />
                        : <Shield className="h-5 w-5 text-muted-foreground" />
                    }
                    {t('settings.2fa.title', 'Two-Factor Authentication')}
                </CardTitle>
                <CardDescription>
                    {enabled
                        ? t('settings.2fa.enabled_status', '2FA is active. Your account has an extra layer of security.')
                        : t('settings.2fa.disabled_status', 'Add an extra layer of security by requiring a code from your authenticator app.')
                    }
                </CardDescription>
            </CardHeader>
            <CardContent className="space-y-6">

                {/* ── Not enrolled ─────────────────────────────────────── */}
                {!enabled && !setupData && (
                    <Button onClick={handleStartSetup} className="flex items-center gap-2">
                        <Shield className="h-4 w-4" />
                        {t('settings.2fa.enable_btn', 'Enable 2FA')}
                    </Button>
                )}

                {/* ── Setup flow ────────────────────────────────────────── */}
                {setupData && (
                    <div className="space-y-6">
                        <div className="space-y-2">
                            <p className="text-sm font-medium">
                                {t('settings.2fa.scan_qr', '1. Scan this QR code with your authenticator app (Google Authenticator, Authy, etc.)')}
                            </p>
                            <div className="flex flex-col sm:flex-row items-start gap-6">
                                {/* QR code */}
                                <img
                                    src={`data:image/png;base64,${setupData.qr_code}`}
                                    alt="2FA QR Code"
                                    className="w-44 h-44 border rounded-lg"
                                />
                                {/* Manual entry secret */}
                                <div className="space-y-2 flex-1">
                                    <p className="text-xs text-muted-foreground">
                                        {t('settings.2fa.manual_entry', 'Or enter this key manually:')}
                                    </p>
                                    <div className="flex items-center gap-2">
                                        <code className="text-xs bg-muted px-3 py-2 rounded font-mono break-all flex-1">
                                            {setupData.secret}
                                        </code>
                                        <Button
                                            size="icon"
                                            variant="outline"
                                            onClick={() => copySecret(setupData.secret)}
                                        >
                                            {copiedSecret ? <Check className="h-4 w-4 text-green-500" /> : <Copy className="h-4 w-4" />}
                                        </Button>
                                    </div>
                                    {setupData.backup_codes.length > 0 && (
                                        <div className="space-y-1 mt-4">
                                            <p className="text-xs font-medium text-amber-600">
                                                {t('settings.2fa.backup_codes_label', 'Save these backup codes — each can only be used once:')}
                                            </p>
                                            <div className="grid grid-cols-2 gap-1">
                                                {setupData.backup_codes.map((code, i) => (
                                                    <code key={i} className="text-xs bg-amber-50 border border-amber-200 px-2 py-1 rounded font-mono">
                                                        {code}
                                                    </code>
                                                ))}
                                            </div>
                                        </div>
                                    )}
                                </div>
                            </div>
                        </div>

                        <div className="space-y-2">
                            <Label htmlFor="verify-code">
                                {t('settings.2fa.enter_code', '2. Enter the 6-digit code from your app to confirm')}
                            </Label>
                            <div className="flex gap-3">
                                <Input
                                    id="verify-code"
                                    value={verifyCode}
                                    onChange={(e) => setVerifyCode(e.target.value.replace(/\D/g, '').slice(0, 6))}
                                    placeholder="000000"
                                    maxLength={6}
                                    className="w-36 text-center text-lg tracking-widest font-mono"
                                />
                                <Button
                                    onClick={handleVerify}
                                    disabled={verifyCode.length !== 6 || verifying}
                                >
                                    {verifying && <Loader2 className="h-4 w-4 mr-2 animate-spin" />}
                                    {t('settings.2fa.verify_btn', 'Verify & Enable')}
                                </Button>
                                <Button variant="ghost" onClick={() => setSetupData(null)}>
                                    {t('common.cancel', 'Cancel')}
                                </Button>
                            </div>
                        </div>
                    </div>
                )}

                {/* ── Enrolled — management options ─────────────────────── */}
                {enabled && (
                    <div className="space-y-6">
                        {/* Regenerate backup codes */}
                        <div className="space-y-3">
                            <div className="flex items-center justify-between">
                                <div>
                                    <p className="text-sm font-medium">{t('settings.2fa.backup_codes_title', 'Backup Codes')}</p>
                                    <p className="text-xs text-muted-foreground">
                                        {t('settings.2fa.backup_codes_desc', 'Backup codes let you sign in if you lose access to your authenticator app.')}
                                    </p>
                                </div>
                                <Button variant="outline" size="sm" onClick={handleRegenerateBackupCodes}>
                                    <RefreshCw className="h-4 w-4 mr-2" />
                                    {t('settings.2fa.regenerate_btn', 'Regenerate')}
                                </Button>
                            </div>
                            {backupCodes.length > 0 && (
                                <div className="grid grid-cols-2 gap-1 p-3 bg-amber-50 border border-amber-200 rounded-lg">
                                    {backupCodes.map((code, i) => (
                                        <code key={i} className="text-xs font-mono px-2 py-1">
                                            {code}
                                        </code>
                                    ))}
                                </div>
                            )}
                        </div>

                        {/* Disable 2FA */}
                        <div className="space-y-2 pt-2 border-t">
                            <p className="text-sm font-medium text-destructive">
                                {t('settings.2fa.disable_title', 'Disable Two-Factor Authentication')}
                            </p>
                            <p className="text-xs text-muted-foreground">
                                {t('settings.2fa.disable_warning', 'Removing 2FA will make your account less secure. Enter your authenticator code to confirm.')}
                            </p>
                            <div className="flex gap-3">
                                <Input
                                    value={disableCode}
                                    onChange={(e) => setDisableCode(e.target.value.replace(/\D/g, '').slice(0, 6))}
                                    placeholder="000000"
                                    maxLength={6}
                                    className="w-36 text-center text-lg tracking-widest font-mono"
                                />
                                <Button
                                    variant="destructive"
                                    onClick={handleDisable}
                                    disabled={disableCode.length !== 6 || disabling}
                                >
                                    {disabling && <Loader2 className="h-4 w-4 mr-2 animate-spin" />}
                                    <ShieldOff className="h-4 w-4 mr-2" />
                                    {t('settings.2fa.disable_btn', 'Disable 2FA')}
                                </Button>
                            </div>
                        </div>
                    </div>
                )}
            </CardContent>
        </Card>
    );
}
