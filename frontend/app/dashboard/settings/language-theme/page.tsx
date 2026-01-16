"use client"

import { useState, useEffect } from "react"
import { useRouter } from "next/navigation"
import { ArrowLeft, Moon, Sun, Check } from "lucide-react"
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
import { RadioGroup, RadioGroupItem } from "@/components/ui/radio-group"
import { useTheme } from "@/components/theme-provider"
import { getUserSettings, updateUserSettings } from "@/lib/settings-api"
import { SUPPORTED_LANGUAGES } from "@/types/settings"
import { useToast } from "@/components/ui/use-toast"
import { useLanguage } from "@/contexts/language-context"

export default function LanguageThemePage() {
    const router = useRouter()
    const { setTheme, theme } = useTheme()
    const { toast } = useToast()
    const { t } = useLanguage()
    const [language, setLanguage] = useState("en")
    const [loading, setLoading] = useState(false)
    const [initialLoading, setInitialLoading] = useState(true)

    useEffect(() => {
        loadSettings()
    }, [])

    const loadSettings = async () => {
        try {
            const settings = await getUserSettings()
            setLanguage(settings.language)
            setTheme(settings.theme)
        } catch (error) {
            console.error("Failed to load settings:", error)
            // Use defaults if API fails
            setLanguage("en")
            setTheme("light")
        } finally {
            setInitialLoading(false)
        }
    }

    const handleSave = async () => {
        setLoading(true)
        try {
            await updateUserSettings({
                theme,
                language: language as "en" | "fr" | "es",
            })

            toast({
                title: "Settings saved",
                description: "Your language and theme preferences have been updated.",
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
                    <h2 className="text-3xl font-bold tracking-tight">{t('settings.language_theme', 'Language & Theme')}</h2>
                    <p className="text-muted-foreground">{t('settings.customize_desc', 'Customize your display preferences and language')}</p>
                </div>
            </div>

            <div className="grid gap-6 max-w-2xl">
                {/* Theme Settings */}
                <Card>
                    <CardHeader>
                        <CardTitle>{t('settings.theme.title', 'Theme')}</CardTitle>
                        <CardDescription>
                            Choose between light and dark mode
                        </CardDescription>
                    </CardHeader>
                    <CardContent className="space-y-4">
                        <div className="grid grid-cols-2 gap-4">
                            <button
                                onClick={() => setTheme("light")}
                                className={`relative flex flex-col items-center justify-center p-6 border-2 rounded-lg cursor-pointer transition-colors ${theme === "light"
                                    ? "border-primary bg-primary/5"
                                    : "border-border hover:border-primary/50"
                                    }`}
                            >
                                <Sun className="h-8 w-8 mb-2" />
                                <span className="font-medium">{t('settings.theme.light', 'Light')}</span>
                                {theme === "light" && (
                                    <Check className="absolute top-2 right-2 h-4 w-4 text-primary" />
                                )}
                            </button>

                            <button
                                onClick={() => setTheme("dark")}
                                className={`relative flex flex-col items-center justify-center p-6 border-2 rounded-lg cursor-pointer transition-colors ${theme === "dark"
                                    ? "border-primary bg-primary/5"
                                    : "border-border hover:border-primary/50"
                                    }`}
                            >
                                <Moon className="h-8 w-8 mb-2" />
                                <span className="font-medium">{t('settings.theme.dark', 'Dark')}</span>
                                {theme === "dark" && (
                                    <Check className="absolute top-2 right-2 h-4 w-4 text-primary" />
                                )}
                            </button>
                        </div>
                    </CardContent>
                </Card>

                {/* Language Settings */}
                <Card>
                    <CardHeader>
                        <CardTitle>{t('settings.language.title', 'Language')}</CardTitle>
                        <CardDescription>
                            Select your preferred language for the interface
                        </CardDescription>
                    </CardHeader>
                    <CardContent>
                        <RadioGroup value={language} onValueChange={setLanguage}>
                            <div className="space-y-3">
                                {SUPPORTED_LANGUAGES.map((lang) => (
                                    <div
                                        key={lang.code}
                                        className="flex items-center space-x-3 p-3 border rounded-lg hover:bg-accent/50 transition-colors"
                                    >
                                        <RadioGroupItem
                                            value={lang.code}
                                            id={lang.code}
                                        />
                                        <Label
                                            htmlFor={lang.code}
                                            className="flex items-center space-x-3 flex-1 cursor-pointer"
                                        >
                                            <span className="text-2xl">
                                                {lang.flag}
                                            </span>
                                            <span className="font-medium">
                                                {lang.name}
                                            </span>
                                        </Label>
                                    </div>
                                ))}
                            </div>
                        </RadioGroup>
                    </CardContent>
                </Card>

                {/* Save Button */}
                <div className="flex justify-end space-x-4">
                    <Link href="/dashboard/settings">
                        <Button variant="outline">Cancel</Button>
                    </Link>
                    <Button onClick={handleSave} disabled={loading}>
                        {loading ? t('settings.saving', 'Saving...') : t('settings.save_changes', 'Save Changes')}
                    </Button>
                </div>
            </div>
        </div>
    )
}
