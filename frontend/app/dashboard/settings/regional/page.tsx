"use client"

import { useState, useEffect } from "react"
import { useRouter } from "next/navigation"
import { ArrowLeft } from "lucide-react"
import Link from "next/link"

import { Button } from "@/components/ui/button"
import {
    Card,
    CardContent,
    CardDescription,
    CardHeader,
    CardTitle,
} from "@/components/ui/card"
import { Label } from "@/components/ui/label"
import {
    Select,
    SelectContent,
    SelectItem,
    SelectTrigger,
    SelectValue,
} from "@/components/ui/select"
import { getUserSettings, updateUserSettings } from "@/lib/settings-api"
import { SUPPORTED_CURRENCIES, SUPPORTED_COUNTRIES } from "@/types/settings"
import { useToast } from "@/components/ui/use-toast"
import { useLanguage } from "@/contexts/language-context"

const TIMEZONES = [
    { value: "UTC", label: "UTC (Coordinated Universal Time)" },
    { value: "America/New_York", label: "Eastern Time (ET)" },
    { value: "America/Chicago", label: "Central Time (CT)" },
    { value: "America/Denver", label: "Mountain Time (MT)" },
    { value: "America/Los_Angeles", label: "Pacific Time (PT)" },
    { value: "Europe/London", label: "London (GMT)" },
    { value: "Europe/Paris", label: "Paris (CET)" },
    { value: "Africa/Lagos", label: "Lagos (WAT)" },
    { value: "Africa/Nairobi", label: "Nairobi (EAT)" },
    { value: "Africa/Johannesburg", label: "Johannesburg (SAST)" },
]

const DATE_FORMATS = [
    { value: "MM/DD/YYYY", label: "MM/DD/YYYY (12/31/2025)" },
    { value: "DD/MM/YYYY", label: "DD/MM/YYYY (31/12/2025)" },
    { value: "YYYY-MM-DD", label: "YYYY-MM-DD (2025-12-31)" },
    { value: "DD MMM YYYY", label: "DD MMM YYYY (31 Dec 2025)" },
]

export default function RegionalSettingsPage() {
    const { t } = useLanguage()
    const router = useRouter()
    const { toast } = useToast()
    const [loading, setLoading] = useState(false)
    const [initialLoading, setInitialLoading] = useState(true)
    const [currency, setCurrency] = useState("USD")
    const [timezone, setTimezone] = useState("UTC")
    const [dateFormat, setDateFormat] = useState("MM/DD/YYYY")

    useEffect(() => {
        loadSettings()
    }, [])

    const loadSettings = async () => {
        try {
            const settings = await getUserSettings()
            setCurrency(settings.currency_format || "USD")
            setTimezone(settings.timezone || "UTC")
            setDateFormat(settings.date_format || "MM/DD/YYYY")
        } catch (error) {
            console.error("Failed to load settings:", error)
            // Use defaults if API fails
            setCurrency("USD")
            setTimezone("UTC")
            setDateFormat("MM/DD/YYYY")
        } finally {
            setInitialLoading(false)
        }
    }

    const handleSave = async () => {
        setLoading(true)
        try {
            await updateUserSettings({
                currency_format: currency,
                timezone,
                date_format: dateFormat,
            })

            toast({
                title: "Settings saved",
                description: "Your regional preferences have been updated.",
            })
        } catch (error) {
            toast({
                title: "Error",
                description: "Failed to save settings. Please try again.",
                variant: "destructive",
            })
        } finally {
            setLoading(false)
        }
    }

    if (initialLoading) {
        return <div className="container mx-auto py-10">Loading...</div>
    }

    return (
        <div className="container mx-auto py-10 space-y-6">
            <div className="flex items-center space-x-4">
                <Link href="/dashboard/settings">
                    <Button variant="ghost" size="icon">
                        <ArrowLeft className="h-4 w-4" />
                    </Button>
                </Link>
                <div>
                    <h2 className="text-3xl font-bold tracking-tight">
                        {t('settings.regional.title', 'Regional Settings')}
                    </h2>
                    <p className="text-muted-foreground">
                        {t('settings.regional.desc', 'Configure your currency, timezone, and date format preferences')}
                    </p>
                </div>
            </div>

            <div className="grid gap-6 max-w-2xl">
                {/* Currency Settings */}
                <Card>
                    <CardHeader>
                        <CardTitle>{t('settings.regional.currency', 'Currency')}</CardTitle>
                        <CardDescription>
                            {t('settings.regional.currency_desc', 'Select your preferred currency for displaying amounts')}
                        </CardDescription>
                    </CardHeader>
                    <CardContent>
                        <div className="space-y-2">
                            <Label htmlFor="currency">{t('settings.regional.currency', 'Currency')}</Label>
                            <Select value={currency} onValueChange={setCurrency}>
                                <SelectTrigger id="currency">
                                    <SelectValue placeholder="Select currency" />
                                </SelectTrigger>
                                <SelectContent>
                                    {SUPPORTED_CURRENCIES.map((curr) => (
                                        <SelectItem
                                            key={curr.code}
                                            value={curr.code}
                                        >
                                            {curr.symbol} - {curr.name} ({curr.code})
                                        </SelectItem>
                                    ))}
                                </SelectContent>
                            </Select>
                        </div>
                    </CardContent>
                </Card>

                {/* Timezone Settings */}
                <Card>
                    <CardHeader>
                        <CardTitle>{t('settings.regional.timezone', 'Timezone')}</CardTitle>
                        <CardDescription>
                            {t('settings.regional.timezone_desc', 'Select your timezone for displaying dates and times')}
                        </CardDescription>
                    </CardHeader>
                    <CardContent>
                        <div className="space-y-2">
                            <Label htmlFor="timezone">{t('settings.regional.timezone', 'Timezone')}</Label>
                            <Select value={timezone} onValueChange={setTimezone}>
                                <SelectTrigger id="timezone">
                                    <SelectValue placeholder="Select timezone" />
                                </SelectTrigger>
                                <SelectContent>
                                    {TIMEZONES.map((tz) => (
                                        <SelectItem key={tz.value} value={tz.value}>
                                            {tz.label}
                                        </SelectItem>
                                    ))}
                                </SelectContent>
                            </Select>
                        </div>
                    </CardContent>
                </Card>

                {/* Date Format Settings */}
                <Card>
                    <CardHeader>
                        <CardTitle>{t('settings.regional.date_format', 'Date Format')}</CardTitle>
                        <CardDescription>
                            {t('settings.regional.date_format_desc', 'Select your preferred date format')}
                        </CardDescription>
                    </CardHeader>
                    <CardContent>
                        <div className="space-y-2">
                            <Label htmlFor="dateFormat">{t('settings.regional.date_format', 'Date Format')}</Label>
                            <Select value={dateFormat} onValueChange={setDateFormat}>
                                <SelectTrigger id="dateFormat">
                                    <SelectValue placeholder="Select date format" />
                                </SelectTrigger>
                                <SelectContent>
                                    {DATE_FORMATS.map((format) => (
                                        <SelectItem
                                            key={format.value}
                                            value={format.value}
                                        >
                                            {format.label}
                                        </SelectItem>
                                    ))}
                                </SelectContent>
                            </Select>
                        </div>
                    </CardContent>
                </Card>

                {/* Save Button */}
                <div className="flex justify-end space-x-4">
                    <Link href="/dashboard/settings">
                        <Button variant="outline">{t('common.cancel', 'Cancel')}</Button>
                    </Link>
                    <Button onClick={handleSave} disabled={loading}>
                        {loading ? t('settings.saving', 'Saving...') : t('settings.save_changes', 'Save Changes')}
                    </Button>
                </div>
            </div>
        </div>
    )
}
