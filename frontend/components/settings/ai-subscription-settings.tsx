"use client"

import { useState, useEffect } from "react"
import { Bot, Key, CreditCard, Save, AlertCircle, Info, Plus } from "lucide-react"

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
import { RadioGroup, RadioGroupItem } from "@/components/ui/radio-group"
import { Badge } from "@/components/ui/badge"
import { useToast } from "@/components/ui/use-toast"
import { subscriptionApi, SubscriptionStatus, AiPlan, UsageStat } from "@/lib/subscription-api"
import {
    BarChart,
    Bar,
    XAxis,
    YAxis,
    CartesianGrid,
    Tooltip,
    ResponsiveContainer,
    Cell
} from 'recharts';
import { format, parseISO } from 'date-fns';
import { TopupDialog } from "./topup-dialog"
import { useAuth } from "@/lib/auth"
import { useLanguage } from "@/contexts/language-context"

export function AiSubscriptionSettings() {
    const { t, formatPrice } = useLanguage()
    const { toast } = useToast()
    const { refreshCredits } = useAuth()
    const [loading, setLoading] = useState(false)
    const [status, setStatus] = useState<SubscriptionStatus | null>(null)
    const [customKey, setCustomKey] = useState("")
    const [usageStats, setUsageStats] = useState<UsageStat[]>([])
    const [hoveredBar, setHoveredBar] = useState<number | null>(null);

    useEffect(() => {
        loadStatus()
    }, [])

    const loadStatus = async () => {
        try {
            // Fetch status first
            const statusData = await subscriptionApi.getStatus()
            setStatus(statusData)

            // Also refresh global context credits for the top badge
            refreshCredits()

            // Then attempt to fetch stats (don't block if it fails)
            try {
                const statsData = await subscriptionApi.getUsageStats()
                setUsageStats(statsData)
            } catch (err) {
                console.error("Failed to load usage stats:", err)
            }
        } catch (error) {
            console.error("Failed to load AI status:", error)
            toast({
                title: "Connection Error",
                description: "Failed to load AI subscription data. Please check your internet connection.",
                variant: "destructive"
            })
        }
    }

    const handleUpdatePlan = async (plan: AiPlan) => {
        setLoading(true)
        try {
            await subscriptionApi.updatePlan(plan)
            setStatus(prev => prev ? { ...prev, plan } : null)
            toast({
                title: "Plan updated",
                description: `Your AI plan has been changed to ${plan}.`,
            })
        } catch (error) {
            toast({
                title: "Error",
                description: "Failed to update plan. Please check your permissions.",
                variant: "destructive",
            })
        } finally {
            setLoading(false)
        }
    }

    const handleUpdateKey = async () => {
        if (!customKey) return
        setLoading(true)
        try {
            await subscriptionApi.updateCompanyKey(customKey)
            setStatus(prev => prev ? { ...prev, has_custom_key: true } : null)
            setCustomKey("")
            toast({
                title: "API Key updated",
                description: "Your custom API key has been encrypted and saved.",
            })
        } catch (error) {
            toast({
                title: "Error",
                description: "Failed to update API key.",
                variant: "destructive",
            })
        } finally {
            setLoading(false)
        }
    }

    if (!status) return null

    return (
        <Card>
            <CardHeader>
                <div className="flex justify-between items-center">
                    <div>
                        <CardTitle className="flex items-center gap-2">
                            <Bot className="h-5 w-5" />
                            {t('settings.ai.subscription_title', 'AI Subscription & Quotas')}
                        </CardTitle>
                        <CardDescription>
                            {t('settings.ai.subscription_desc', 'Configure how your company accesses and pays for AI Agent features')}
                        </CardDescription>
                    </div>
                </div>
            </CardHeader>
            <CardContent className="space-y-8">
                {/* Plan Selection */}
                <div className="space-y-4">
                    <Label className="text-base font-semibold">{t('settings.ai.select_plan', 'Select AI Plan')}</Label>
                    <RadioGroup
                        value={status.plan}
                        onValueChange={(v) => handleUpdatePlan(v as AiPlan)}
                        className="grid grid-cols-1 md:grid-cols-3 gap-4"
                        disabled={loading}
                    >
                        {/* Plan 1: BASIC */}
                        <div className="relative">
                            <RadioGroupItem value="BASIC" id="plan-basic" className="sr-only" />
                            <Label
                                htmlFor="plan-basic"
                                className={`flex flex-col p-4 border-2 rounded-xl cursor-pointer hover:border-primary/50 transition-all h-full ${status.plan === "BASIC" ? "border-primary bg-primary/5 shadow-md" : "border-muted"
                                    }`}
                            >
                                <div className="flex items-center justify-between mb-2">
                                    <span className="font-bold">{t('settings.ai.plan_basic', 'No AI Features')}</span>
                                    {status.plan === "BASIC" && <Badge>Active</Badge>}
                                </div>
                                <p className="text-sm text-muted-foreground flex-grow">
                                    {t('settings.ai.plan_basic_desc', 'Standard SaaS features only. AI Agent Manager will be disabled.')}
                                </p>
                                <div className="mt-4 pt-4 border-t text-sm font-semibold text-primary">
                                    {t('settings.ai.free', 'FREE')}
                                </div>
                            </Label>
                        </div>

                        {/* Plan 2: BYOK */}
                        <div className="relative">
                            <RadioGroupItem value="BYOK" id="plan-byok" className="sr-only" />
                            <Label
                                htmlFor="plan-byok"
                                className={`flex flex-col p-4 border-2 rounded-xl cursor-pointer hover:border-primary/50 transition-all h-full ${status.plan === "BYOK" ? "border-primary bg-primary/5 shadow-md" : "border-muted"
                                    }`}
                            >
                                <div className="flex items-center justify-between mb-2">
                                    <span className="font-bold">{t('settings.ai.plan_byok', 'Bring Your Own Key')}</span>
                                    {status.plan === "BYOK" && <Badge>Active</Badge>}
                                </div>
                                <p className="text-sm text-muted-foreground flex-grow">
                                    {t('settings.ai.plan_byok_desc', 'Use your own Google or Claude API keys. You manage your own AI costs.')}
                                </p>
                                <div className="mt-4 pt-4 border-t text-sm font-semibold text-primary">
                                    {t('settings.ai.saas_monthly', 'SaaS Monthly Only')}
                                </div>
                            </Label>
                        </div>

                        {/* Plan 3: CREDIT */}
                        <div className="relative">
                            <RadioGroupItem value="CREDIT" id="plan-credit" className="sr-only" />
                            <Label
                                htmlFor="plan-credit"
                                className={`flex flex-col p-4 border-2 rounded-xl cursor-pointer hover:border-primary/50 transition-all h-full ${status.plan === "CREDIT" ? "border-primary bg-primary/5 shadow-md" : "border-muted"
                                    }`}
                            >
                                <div className="flex items-center justify-between mb-2">
                                    <span className="font-bold">{t('settings.ai.plan_credit', 'Credit-Based')}</span>
                                    {status.plan === "CREDIT" && <Badge>Active</Badge>}
                                </div>
                                <p className="text-sm text-muted-foreground flex-grow">
                                    {t('settings.ai.plan_credit_desc', 'Pay as you go using SaaS-provided high-tier models.')}
                                </p>
                                <div className="mt-4 pt-4 border-t text-sm font-semibold text-primary">
                                    {t('settings.ai.cost_per_interaction', '$0.05 / interaction')}
                                </div>
                            </Label>
                        </div>
                    </RadioGroup>
                </div>

                {/* Credit Balance Card (Show if using CREDIT plan) */}
                {status.plan === "CREDIT" && (
                    <div className="p-4 bg-muted/30 border rounded-xl flex items-center justify-between">
                        <div className="flex items-center gap-3">
                            <div className="p-2 bg-primary/10 rounded-full text-primary">
                                <CreditCard className="h-5 w-5" />
                            </div>
                            <div>
                                <p className="text-sm font-medium">{t('settings.ai.credits', 'Available Credits')}</p>
                                <p className="text-2xl font-bold">{formatPrice(status.credits)}</p>
                            </div>
                        </div>
                        <div className="flex gap-2">
                            <TopupDialog onSuccess={loadStatus} />
                        </div>
                    </div>
                )}

                {/* API Key Management (Show if using BYOK plan) */}
                {(status.plan === "BYOK" || status.plan === "CREDIT") && (
                    <div className="space-y-4 pt-4 border-t">
                        <div className="flex items-center gap-2">
                            <Key className="h-5 w-5 text-muted-foreground" />
                            <Label className="font-semibold">
                                {status.plan === "BYOK" ? t('settings.ai.company_key', 'Company API Key') : t('settings.ai.secondary_key', 'Secondary Fallback Key (Optional)')}
                            </Label>
                        </div>
                        <div className="grid grid-cols-1 md:grid-cols-4 gap-4 items-end">
                            <div className="md:col-span-3 space-y-2">
                                <Input
                                    type="password"
                                    placeholder={status.has_custom_key ? "••••••••••••••••" : "Paste your Google AI API Key here"}
                                    value={customKey}
                                    onChange={(e) => setCustomKey(e.target.value)}
                                />
                                <p className="text-xs text-muted-foreground">
                                    {t('settings.ai.key_security_note', 'Your key is stored with AES-256 encryption and never exposed in the browser.')}
                                </p>
                            </div>
                            <Button
                                onClick={handleUpdateKey}
                                disabled={!customKey || loading}
                                className="w-full"
                            >
                                <Save className="mr-2 h-4 w-4" />
                                {t('settings.ai.save_key', 'Save Key')}
                            </Button>
                        </div>
                    </div>
                )}

                {/* Usage Visualization */}
                <div className="space-y-4 pt-4 border-t">
                    <div className="flex items-center justify-between">
                        <div className="space-y-1">
                            <Label className="text-base font-semibold">{t('settings.ai.usage_title', 'AI Usage (Last 30 Days)')}</Label>
                            <p className="text-xs text-muted-foreground">
                                {t('settings.ai.usage_desc', 'Detailed breakdown of credits consumed per day.')}
                            </p>
                        </div>
                        {usageStats.length > 0 && (
                            <Badge variant="secondary" className="gap-1">
                                Total: {formatPrice(usageStats.reduce((sum, s) => sum + s.credits, 0))}
                            </Badge>
                        )}
                    </div>

                    <div className="h-[250px] w-full mt-4 bg-muted/20 rounded-xl p-4 border border-dashed border-muted-foreground/20">
                        {usageStats.length === 0 ? (
                            <div className="h-full flex flex-col items-center justify-center text-muted-foreground space-y-2">
                                <Bot className="h-8 w-8 opacity-20" />
                                <p className="text-sm">{t('common.no_data', 'No usage data available for this period.')}</p>
                            </div>
                        ) : (
                            <ResponsiveContainer width="100%" height="100%">
                                <BarChart
                                    data={usageStats}
                                    onMouseMove={(state) => {
                                        if (typeof state.activeTooltipIndex === 'number') {
                                            setHoveredBar(state.activeTooltipIndex);
                                        }
                                    }}
                                    onMouseLeave={() => setHoveredBar(null)}
                                >
                                    <CartesianGrid strokeDasharray="3 3" vertical={false} stroke="currentColor" className="opacity-10" />
                                    <XAxis
                                        dataKey="date"
                                        tickFormatter={(str) => format(parseISO(str), 'MMM d')}
                                        stroke="currentColor"
                                        fontSize={10}
                                        tickLine={false}
                                        axisLine={false}
                                    />
                                    <YAxis
                                        stroke="currentColor"
                                        fontSize={10}
                                        tickLine={false}
                                        axisLine={false}
                                        tickFormatter={(val) => formatPrice(val)}
                                    />
                                    <Tooltip
                                        cursor={{ fill: 'currentColor', opacity: 0.1 }}
                                        content={({ active, payload }) => {
                                            if (active && payload && payload.length) {
                                                const data = payload[0].payload;
                                                return (
                                                    <div className="bg-background border rounded-lg shadow-lg p-3 text-xs space-y-1">
                                                        <p className="font-bold text-muted-foreground">{format(parseISO(data.date), 'MMMM do, yyyy')}</p>
                                                        <div className="flex justify-between gap-4">
                                                            <span>Credits:</span>
                                                            <span className="font-mono text-primary font-bold">{formatPrice(data.credits)}</span>
                                                        </div>
                                                        <div className="flex justify-between gap-4 border-t pt-1 mt-1">
                                                            <span>Interactions:</span>
                                                            <span className="font-mono">{data.count}</span>
                                                        </div>
                                                    </div>
                                                );
                                            }
                                            return null;
                                        }}
                                    />
                                    <Bar
                                        dataKey="credits"
                                        radius={[4, 4, 0, 0]}
                                        className="fill-primary"
                                    >
                                        {usageStats.map((entry, index) => (
                                            <Cell
                                                key={`cell-${index}`}
                                                fillOpacity={hoveredBar === null || hoveredBar === index ? 1 : 0.3}
                                                className="transition-opacity duration-300"
                                            />
                                        ))}
                                    </Bar>
                                </BarChart>
                            </ResponsiveContainer>
                        )}
                    </div>
                </div>

                {/* Help/Infor Section */}
                <div className="px-4 py-3 bg-blue-50 dark:bg-blue-900/20 rounded-lg flex gap-3 text-sm text-blue-800 dark:text-blue-300">
                    <Info className="h-5 w-5 shrink-0" />
                    <div>
                        <p className="font-semibold">{t('settings.ai.plan_help_title', 'Which plan should I choose?')}</p>
                        <p className="opacity-90">
                            {t('settings.ai.plan_help_desc', 'Use **Bring Your Own Key** if you already have a Google Cloud account. Choose **Credit-Based** for the simplest experience with managed quota and high performance.')}
                        </p>
                    </div>
                </div>
            </CardContent>
        </Card >
    )
}
