"use client"

import { useState, useEffect, useCallback } from "react"
import { Shield, ShieldCheck, ShieldOff, QrCode, Key, RefreshCw, Loader2 } from "lucide-react"

import { Button } from "@/components/ui/button"
import {
    Card,
    CardContent,
    CardDescription,
    CardHeader,
    CardTitle,
} from "@/components/ui/card"
import { Input } from "@/components/ui/input"
import { Label } from "@/components/ui/label"
import { Badge } from "@/components/ui/badge"
import {
    Alert,
    AlertDescription,
    AlertTitle,
} from "@/components/ui/alert"
import { useToast } from "@/components/ui/use-toast"
import { api } from "@/lib/api"

interface TwoFASetupData {
    secret: string
    totp_uri: string
    qr_code: string | null
    backup_codes: string[]
    message: string
}

interface TwoFAStatus {
    enabled: boolean
}

export function TwoFactorSettings() {
    const { toast } = useToast()

    // Current 2FA state
    const [enabled, setEnabled] = useState(false)
    const [loadingStatus, setLoadingStatus] = useState(true)

    // Setup flow
    const [setupData, setSetupData] = useState<TwoFASetupData | null>(null)
    const [verifyCode, setVerifyCode] = useState("")
    const [disableCode, setDisableCode] = useState("")
    const [regenCode, setRegenCode] = useState("")

    // Loading states
    const [settingUp, setSettingUp] = useState(false)
    const [verifying, setVerifying] = useState(false)
    const [disabling, setDisabling] = useState(false)
    const [regenerating, setRegenerating] = useState(false)

    // Backup codes display
    const [newBackupCodes, setNewBackupCodes] = useState<string[]>([])

    // ── Fetch current 2FA status from user profile ──────────────────────────
    const fetchStatus = useCallback(async () => {
        try {
            setLoadingStatus(true)
            const res = await api.get("/users/me")
            setEnabled(!!res.data?.mfa_enabled)
        } catch {
            // ignore — user not authenticated or endpoint unavailable
        } finally {
            setLoadingStatus(false)
        }
    }, [])

    useEffect(() => { fetchStatus() }, [fetchStatus])

    // ── Initiate setup ───────────────────────────────────────────────────────
    const handleSetup = async () => {
        setSettingUp(true)
        try {
            const res = await api.post<TwoFASetupData>("/2fa/setup")
            setSetupData(res.data)
            setVerifyCode("")
        } catch (err: any) {
            toast({
                title: "Setup failed",
                description: err?.response?.data?.detail || "Could not initiate 2FA setup.",
                variant: "destructive",
            })
        } finally {
            setSettingUp(false)
        }
    }

    // ── Verify and activate ──────────────────────────────────────────────────
    const handleVerifySetup = async () => {
        if (!verifyCode) return
        setVerifying(true)
        try {
            await api.post("/2fa/verify-setup", { code: verifyCode })
            setEnabled(true)
            setSetupData(null)
            setVerifyCode("")
            toast({
                title: "2FA Enabled",
                description: "Two-factor authentication is now active on your account.",
            })
        } catch (err: any) {
            toast({
                title: "Verification failed",
                description: err?.response?.data?.detail || "Invalid code. Try again.",
                variant: "destructive",
            })
        } finally {
            setVerifying(false)
        }
    }

    // ── Disable 2FA ──────────────────────────────────────────────────────────
    const handleDisable = async () => {
        if (!disableCode) return
        setDisabling(true)
        try {
            await api.post("/2fa/disable", { code: disableCode })
            setEnabled(false)
            setDisableCode("")
            toast({
                title: "2FA Disabled",
                description: "Two-factor authentication has been removed from your account.",
            })
        } catch (err: any) {
            toast({
                title: "Disable failed",
                description: err?.response?.data?.detail || "Invalid code.",
                variant: "destructive",
            })
        } finally {
            setDisabling(false)
        }
    }

    // ── Regenerate backup codes ──────────────────────────────────────────────
    const handleRegenBackupCodes = async () => {
        if (!regenCode) return
        setRegenerating(true)
        try {
            const res = await api.post<{ backup_codes: string[]; message: string }>(
                "/2fa/backup-codes",
                { code: regenCode }
            )
            setNewBackupCodes(res.data.backup_codes)
            setRegenCode("")
            toast({ title: "New backup codes generated", description: res.data.message })
        } catch (err: any) {
            toast({
                title: "Regeneration failed",
                description: err?.response?.data?.detail || "Invalid code.",
                variant: "destructive",
            })
        } finally {
            setRegenerating(false)
        }
    }

    if (loadingStatus) {
        return (
            <Card>
                <CardContent className="pt-6 flex items-center gap-2">
                    <Loader2 className="h-4 w-4 animate-spin" />
                    <span className="text-sm text-muted-foreground">Loading security settings…</span>
                </CardContent>
            </Card>
        )
    }

    return (
        <Card>
            <CardHeader>
                <div className="flex items-center gap-2">
                    {enabled ? (
                        <ShieldCheck className="h-5 w-5 text-green-600" />
                    ) : (
                        <Shield className="h-5 w-5 text-muted-foreground" />
                    )}
                    <CardTitle>Two-Factor Authentication</CardTitle>
                    <Badge variant={enabled ? "default" : "secondary"}>
                        {enabled ? "Enabled" : "Disabled"}
                    </Badge>
                </div>
                <CardDescription>
                    Add an extra layer of security to your account. When enabled, you will need your
                    authenticator app (Google Authenticator, Authy, etc.) to sign in.
                </CardDescription>
            </CardHeader>
            <CardContent className="space-y-6">

                {/* ── Not enabled: show setup flow ────────────────────────── */}
                {!enabled && !setupData && (
                    <div className="space-y-4">
                        <Alert>
                            <Shield className="h-4 w-4" />
                            <AlertTitle>2FA is not active</AlertTitle>
                            <AlertDescription>
                                Enable two-factor authentication to protect your account from
                                unauthorized access.
                            </AlertDescription>
                        </Alert>
                        <Button onClick={handleSetup} disabled={settingUp}>
                            {settingUp && <Loader2 className="mr-2 h-4 w-4 animate-spin" />}
                            <QrCode className="mr-2 h-4 w-4" />
                            Set Up Two-Factor Authentication
                        </Button>
                    </div>
                )}

                {/* ── Setup initiated: show QR + verify form ──────────────── */}
                {!enabled && setupData && (
                    <div className="space-y-6">
                        <Alert className="border-blue-200 bg-blue-50">
                            <QrCode className="h-4 w-4 text-blue-600" />
                            <AlertTitle className="text-blue-800">Scan the QR code</AlertTitle>
                            <AlertDescription className="text-blue-700">
                                Open your authenticator app and scan the QR code below. Then enter
                                the 6-digit code to activate 2FA.
                            </AlertDescription>
                        </Alert>

                        {/* QR Code */}
                        {setupData.qr_code ? (
                            <div className="flex flex-col items-center gap-3 p-4 border rounded-lg bg-white w-fit mx-auto">
                                <img
                                    src={setupData.qr_code}
                                    alt="2FA QR Code"
                                    width={200}
                                    height={200}
                                    className="rounded"
                                />
                                <p className="text-xs text-muted-foreground text-center max-w-[240px]">
                                    Can&apos;t scan? Enter this key manually:
                                </p>
                                <code className="text-xs font-mono bg-muted px-2 py-1 rounded break-all text-center">
                                    {setupData.secret}
                                </code>
                            </div>
                        ) : (
                            <div className="p-4 border rounded-lg bg-muted">
                                <p className="text-sm font-medium">Manual setup key:</p>
                                <code className="text-sm font-mono break-all">{setupData.secret}</code>
                            </div>
                        )}

                        {/* Backup codes — show once */}
                        <div className="space-y-2">
                            <Label className="flex items-center gap-2 text-sm font-medium">
                                <Key className="h-4 w-4" />
                                Backup Codes (save these now — shown once only)
                            </Label>
                            <div className="grid grid-cols-2 gap-2 p-3 border rounded-lg bg-muted font-mono text-sm">
                                {setupData.backup_codes.map((code) => (
                                    <span key={code}>{code}</span>
                                ))}
                            </div>
                        </div>

                        {/* Verify code input */}
                        <div className="space-y-3">
                            <Label htmlFor="totp-verify">Enter the 6-digit code from your app</Label>
                            <div className="flex gap-2">
                                <Input
                                    id="totp-verify"
                                    placeholder="000000"
                                    maxLength={6}
                                    value={verifyCode}
                                    onChange={(e) => setVerifyCode(e.target.value.replace(/\D/g, ""))}
                                    className="max-w-[160px] tracking-widest text-center"
                                />
                                <Button
                                    onClick={handleVerifySetup}
                                    disabled={verifyCode.length !== 6 || verifying}
                                >
                                    {verifying && <Loader2 className="mr-2 h-4 w-4 animate-spin" />}
                                    Activate 2FA
                                </Button>
                                <Button
                                    variant="ghost"
                                    onClick={() => { setSetupData(null); setVerifyCode("") }}
                                >
                                    Cancel
                                </Button>
                            </div>
                        </div>
                    </div>
                )}

                {/* ── Enabled: show management options ────────────────────── */}
                {enabled && (
                    <div className="space-y-6">
                        <Alert className="border-green-200 bg-green-50">
                            <ShieldCheck className="h-4 w-4 text-green-600" />
                            <AlertTitle className="text-green-800">
                                Two-factor authentication is active
                            </AlertTitle>
                            <AlertDescription className="text-green-700">
                                Your account is protected. You will need your authenticator app each
                                time you sign in.
                            </AlertDescription>
                        </Alert>

                        {/* Regenerate backup codes */}
                        <div className="space-y-3 border-t pt-4">
                            <h4 className="text-sm font-medium flex items-center gap-2">
                                <RefreshCw className="h-4 w-4" />
                                Regenerate Backup Codes
                            </h4>
                            <p className="text-sm text-muted-foreground">
                                If you have used most of your backup codes, generate a new set. This
                                will invalidate all existing backup codes.
                            </p>
                            <div className="flex gap-2">
                                <Input
                                    placeholder="6-digit TOTP code to confirm"
                                    maxLength={6}
                                    value={regenCode}
                                    onChange={(e) =>
                                        setRegenCode(e.target.value.replace(/\D/g, ""))
                                    }
                                    className="max-w-[220px] tracking-widest text-center"
                                />
                                <Button
                                    variant="outline"
                                    onClick={handleRegenBackupCodes}
                                    disabled={regenCode.length !== 6 || regenerating}
                                >
                                    {regenerating && (
                                        <Loader2 className="mr-2 h-4 w-4 animate-spin" />
                                    )}
                                    Regenerate
                                </Button>
                            </div>
                            {newBackupCodes.length > 0 && (
                                <div className="space-y-2">
                                    <Label className="flex items-center gap-2 text-sm font-medium text-amber-700">
                                        <Key className="h-4 w-4" />
                                        New Backup Codes (save these now)
                                    </Label>
                                    <div className="grid grid-cols-2 gap-2 p-3 border rounded-lg bg-amber-50 font-mono text-sm">
                                        {newBackupCodes.map((code) => (
                                            <span key={code}>{code}</span>
                                        ))}
                                    </div>
                                    <Button
                                        size="sm"
                                        variant="ghost"
                                        onClick={() => setNewBackupCodes([])}
                                    >
                                        Dismiss
                                    </Button>
                                </div>
                            )}
                        </div>

                        {/* Disable 2FA */}
                        <div className="space-y-3 border-t pt-4">
                            <h4 className="text-sm font-medium flex items-center gap-2 text-destructive">
                                <ShieldOff className="h-4 w-4" />
                                Disable Two-Factor Authentication
                            </h4>
                            <p className="text-sm text-muted-foreground">
                                Enter your current TOTP code (or a backup code) to remove 2FA from
                                your account.
                            </p>
                            <div className="flex gap-2">
                                <Input
                                    placeholder="6-digit code or backup code"
                                    value={disableCode}
                                    onChange={(e) => setDisableCode(e.target.value.trim())}
                                    className="max-w-[220px]"
                                />
                                <Button
                                    variant="destructive"
                                    onClick={handleDisable}
                                    disabled={!disableCode || disabling}
                                >
                                    {disabling && (
                                        <Loader2 className="mr-2 h-4 w-4 animate-spin" />
                                    )}
                                    Disable 2FA
                                </Button>
                            </div>
                        </div>
                    </div>
                )}
            </CardContent>
        </Card>
    )
}
