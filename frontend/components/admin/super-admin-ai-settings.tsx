import { useState, useEffect } from "react"
import { Shield, Save, Bot, Sparkles, Activity, Loader2, Info } from "lucide-react"

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
import { useToast } from "@/components/ui/use-toast"
import { useLanguage } from "@/contexts/language-context"
import {
    Table,
    TableBody,
    TableCell,
    TableHead,
    TableHeader,
    TableRow,
} from "@/components/ui/table"
import { subscriptionApi } from "@/lib/subscription-api"
import api from "@/lib/api"

interface AiUsageLog {
    id: string
    company_id: string
    user_id: string
    agent_name: string
    action: string
    credits_consumed: number
    created_at: string
}

export function SuperAdminAISettings() {
    const { t } = useLanguage()
    const { toast } = useToast()
    const [loading, setLoading] = useState(false)
    const [logsLoading, setLogsLoading] = useState(false)
    const [logs, setLogs] = useState<AiUsageLog[]>([])
    const [keys, setKeys] = useState({
        google: "",
        openai: "",
        anthropic: ""
    })

    useEffect(() => {
        fetchLogs()
    }, [])

    const fetchLogs = async () => {
        setLogsLoading(true)
        try {
            const response = await api.get("/subscription/system/usage?limit=50")
            setLogs(response.data)
        } catch (error) {
            console.error("Failed to fetch AI logs:", error)
        } finally {
            setLogsLoading(false)
        }
    }

    const handleUpdateKey = async (provider: string) => {
        const key = keys[provider as keyof typeof keys]
        if (!key) return

        setLoading(true)
        try {
            await subscriptionApi.updateSystemKey(provider, key)
            setKeys(prev => ({ ...prev, [provider]: "" }))
            toast({
                title: "System Key Updated",
                description: `The global ${provider} AI key has been updated and is now live for all 'Credit Plan' users.`,
            })
        } catch (error) {
            toast({
                title: "Error",
                description: "Failed to update system key. Ensure you have Super Admin privileges.",
                variant: "destructive",
            })
        } finally {
            setLoading(false)
        }
    }

    return (
        <div className="space-y-6">
            <Card className="border-2 border-primary/20">
                <CardHeader className="bg-primary/5">
                    <div className="flex items-center gap-3">
                        <div className="p-2 bg-primary text-primary-foreground rounded-lg">
                            <Shield className="h-6 w-6" />
                        </div>
                        <div>
                            <CardTitle>{t('settings.ai.global_config_title', 'Global AI Configuration')}</CardTitle>
                            <CardDescription>
                                {t('settings.ai.global_config_desc', 'Main SaaS elements of the **credit-based AI plan**. They power all tenant agents.')}
                            </CardDescription>
                        </div>
                    </div>
                </CardHeader>
                <CardContent className="space-y-6 pt-6">
                    {/* Google Gemini */}
                    <div className="space-y-4 p-4 border rounded-xl bg-accent/30">
                        <div className="flex items-center justify-between">
                            <div className="flex items-center gap-2">
                                <Sparkles className="h-5 w-5 text-blue-500" />
                                <Label className="text-base font-bold">{t('settings.ai.gemini_principal', 'Google Gemini (Principal)')}</Label>
                            </div>
                            <Badge variant="outline">{t('common.recommended', 'RECOMMENDED')}</Badge>
                        </div>
                        <div className="flex gap-4">
                            <Input
                                type="password"
                                placeholder="Enter Google API Key..."
                                value={keys.google}
                                onChange={(e) => setKeys(prev => ({ ...prev, google: e.target.value }))}
                                className="flex-grow"
                            />
                            <Button
                                onClick={() => handleUpdateKey("google")}
                                disabled={!keys.google || loading}
                            >
                                <Save className="h-4 w-4 mr-2" />
                                {t('common.update', 'Update')}
                            </Button>
                        </div>
                    </div>

                    {/* Info Box */}
                    <div className="text-xs text-muted-foreground p-3 border-l-4 border-primary bg-muted rounded-r-md">
                        <p className="font-bold mb-1">{t('settings.ai.super_admin_note', 'Super Administrator Note:')}</p>
                        {t('settings.ai.update_warning', 'Updating these keys will take effect **immediately** on all tenant requests.')}
                    </div>
                </CardContent>
            </Card>

            <Card>
                <CardHeader className="flex flex-row items-center justify-between">
                    <div>
                        <CardTitle className="flex items-center gap-2">
                            <Activity className="h-5 w-5" />
                            {t('settings.ai.logs_title', 'Global AI Usage Logs')}
                        </CardTitle>
                        <CardDescription>
                            {t('settings.ai.logs_desc', 'Real-time monitoring of AI interactions across the entire platform.')}
                        </CardDescription>
                    </div>
                    <Button variant="outline" size="sm" onClick={fetchLogs} disabled={logsLoading}>
                        {logsLoading ? <Loader2 className="h-4 w-4 animate-spin" /> : t('common.refresh', 'Refresh')}
                    </Button>
                </CardHeader>
                <CardContent>
                    <div className="rounded-md border">
                        <Table>
                            <TableHeader>
                                <TableRow>
                                    <TableHead>{t('common.table.time', 'Time')}</TableHead>
                                    <TableHead>{t('common.table.company_id', 'Company ID')}</TableHead>
                                    <TableHead>{t('common.table.agent', 'Agent')}</TableHead>
                                    <TableHead>{t('common.table.action', 'Action')}</TableHead>
                                    <TableHead className="text-right">{t('common.table.credits', 'Credits')}</TableHead>
                                </TableRow>
                            </TableHeader>
                            <TableBody>
                                {logs.length === 0 ? (
                                    <TableRow>
                                        <TableCell colSpan={5} className="text-center py-10 text-muted-foreground">
                                            {logsLoading ? t('common.loading_logs', 'Loading logs...') : t('settings.ai.no_logs', 'No AI usage recorded yet.')}
                                        </TableCell>
                                    </TableRow>
                                ) : (
                                    logs.map((log) => (
                                        <TableRow key={log.id}>
                                            <TableCell className="text-xs">
                                                {new Date(log.created_at).toLocaleString()}
                                            </TableCell>
                                            <TableCell className="font-mono text-[10px] max-w-[100px] truncate">
                                                {log.company_id}
                                            </TableCell>
                                            <TableCell>
                                                <Badge variant="secondary" className="font-normal">
                                                    {t(`settings.ai.agents.${log.agent_name.toLowerCase()}`, log.agent_name)}
                                                </Badge>
                                            </TableCell>
                                            <TableCell className="text-xs">{t(`settings.ai.actions.${log.action.toLowerCase()}`, log.action)}</TableCell>
                                            <TableCell className="text-right font-medium text-emerald-600 dark:text-emerald-400">
                                                -${log.credits_consumed.toFixed(2)}
                                            </TableCell>
                                        </TableRow>
                                    ))
                                )}
                            </TableBody>
                        </Table>
                    </div>
                </CardContent>
            </Card>
        </div>
    )
}

function Badge({ children, variant = "default", className }: { children: React.ReactNode, variant?: "default" | "outline" | "secondary", className?: string }) {
    return (
        <span className={`px-2 py-0.5 rounded-full text-[10px] font-bold uppercase tracking-wider ${variant === "outline" ? "border text-muted-foreground" :
            variant === "secondary" ? "bg-secondary text-secondary-foreground" :
                "bg-primary text-primary-foreground"
            } ${className || ""}`}>
            {children}
        </span>
    )
}
