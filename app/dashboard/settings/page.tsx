"use client"

import { useState, useEffect } from "react"
import { Moon, Sun, Check, Plus, Trash2, Upload, Building2, Save, UserCog } from "lucide-react"

import { Button } from "@/components/ui/button"
import {
    Card,
    CardContent,
    CardDescription,
    CardHeader,
    CardTitle,
} from "@/components/ui/card"
import { ProfileUploader } from "@/components/shared/profile-uploader"
import { Input } from "@/components/ui/input"
import { Label } from "@/components/ui/label"
import { Textarea } from "@/components/ui/textarea"
import { RadioGroup, RadioGroupItem } from "@/components/ui/radio-group"
import {
    Select,
    SelectContent,
    SelectItem,
    SelectTrigger,
    SelectValue,
} from "@/components/ui/select"
import {
    Table,
    TableBody,
    TableCell,
    TableHead,
    TableHeader,
    TableRow,
} from "@/components/ui/table"
import { Badge } from "@/components/ui/badge"
import { useTheme } from "@/components/theme-provider"
import {
    getUserSettings,
    updateUserSettings,
    getCompanySettings,
    updateCompanySettings,
    uploadCompanyLogo
} from "@/lib/settings-api"
import { userApi } from "@/lib/user-api"
import { User } from "@/types/user" // Fixed import source
import {
    SUPPORTED_LANGUAGES,
    SUPPORTED_CURRENCIES,
    SUPPORTED_COUNTRIES,
    MOBILE_MONEY_PROVIDERS,
    BankDetails,
    MobileMoneyAccount
} from "@/types/settings"
import { useToast } from "@/components/ui/use-toast"
import Link from "next/link"
import Image from "next/image"
import { UserPermissionsModal } from "@/components/user-permissions-modal"
import { AiSubscriptionSettings } from "@/components/settings/ai-subscription-settings"
import { SuperAdminAISettings } from "@/components/admin/super-admin-ai-settings"
import { TwoFactorSettings } from "@/components/settings/two-factor-settings"
import { useAuth } from "@/lib/auth"
import { PermissionDeniedModal } from "@/components/shared/permission-denied-modal"
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
]

const DATE_FORMATS = [
    { value: "MM/DD/YYYY", label: "MM/DD/YYYY (12/31/2025)" },
    { value: "DD/MM/YYYY", label: "DD/MM/YYYY (31/12/2025)" },
    { value: "YYYY-MM-DD", label: "YYYY-MM-DD (2025-12-31)" },
    { value: "DD MMM YYYY", label: "DD MMM YYYY (31 Dec 2025)" },
]

export default function SettingsPage() {
    const { t, currency, setCurrency, setLanguage: setContextLanguage } = useLanguage()
    const { user } = useAuth()
    const { theme, setTheme } = useTheme()
    const { toast } = useToast()
    const [loading, setLoading] = useState(false)
    const [uploadingLogo, setUploadingLogo] = useState(false)
    const [isMounted, setIsMounted] = useState(false)

    // User Settings
    const [language, setLanguage] = useState("en")
    // Currency is now managed by LanguageContext
    const [timezone, setTimezone] = useState("UTC")
    const [dateFormat, setDateFormat] = useState("MM/DD/YYYY")

    // User Management
    const [users, setUsers] = useState<User[]>([])

    // Company Settings
    const [companyName, setCompanyName] = useState("")
    const [companyEmail, setCompanyEmail] = useState("")
    const [companyPhone, setCompanyPhone] = useState("")
    const [companyAddress, setCompanyAddress] = useState("")
    const [registrationNumber, setRegistrationNumber] = useState("")
    const [logoUrl, setLogoUrl] = useState("")
    const [companyCountry, setCompanyCountry] = useState("")
    const [bankDetails, setBankDetails] = useState<BankDetails[]>([])
    const [mobileMoneyAccounts, setMobileMoneyAccounts] = useState<MobileMoneyAccount[]>([])
    const [governmentTaxPercent, setGovernmentTaxPercent] = useState(0)
    const [adminFee, setAdminFee] = useState(0)

    // Permissions Modal
    const [permissionsModalOpen, setPermissionsModalOpen] = useState(false)
    const [showAccessDenied, setShowAccessDenied] = useState(false)

    useEffect(() => {
        setIsMounted(true)
        loadSettings()
    }, [])

    const loadSettings = async () => {
        try {
            // Load user settings
            const userSettings = await getUserSettings()
            setLanguage(userSettings.language)
            setTheme(userSettings.theme)
            // Currency sync logic: if backend has it, use it, else keep context default (XOF)
            if (userSettings.currency_format) {
                setCurrency(userSettings.currency_format);
            }
            setTimezone(userSettings.timezone || "UTC")
            setDateFormat(userSettings.date_format || "MM/DD/YYYY")


            // Load users list (if admin)
            try {
                const usersList = await userApi.list()
                setUsers(usersList)
            } catch (err) {
                // Not an admin or users list not available
            }

            // Load company settings (if admin)
            try {
                const companySettings = await getCompanySettings()
                setCompanyName(companySettings.name)
                setCompanyEmail(companySettings.email)
                setCompanyPhone(companySettings.phone || "")
                setCompanyAddress(companySettings.address || "")
                setRegistrationNumber(companySettings.registration_number || "")
                setLogoUrl(companySettings.logo_url || "")
                setCompanyCountry(companySettings.country || "")
                setBankDetails(companySettings.bank_details || [])
                setMobileMoneyAccounts(companySettings.mobile_money_accounts || [])
                setGovernmentTaxPercent(companySettings.government_tax_percent || 0.0)
                setAdminFee(companySettings.admin_fee || 0.0)
            } catch (err) {
                // Not an admin or company settings not available
            }
        } catch (error) {
            console.error("Failed to load settings:", error)
            // Use defaults
            setLanguage("en")
            setTheme("light")
            setCurrency("XOF")
            setTimezone("UTC")
            setDateFormat("MM/DD/YYYY")
        }
    }

    const handleSaveUserSettings = async () => {
        setLoading(true)
        try {
            await updateUserSettings({
                theme,
                language: language as "en" | "fr" | "es",
                currency_format: currency,
                timezone,
                date_format: dateFormat,
            })

            toast({
                title: t('Settings saved'),
                description: t('Your preferences have been updated successfully.'),
            })
        } catch (error) {
            toast({
                title: t('Error'),
                description: t('Failed to save settings. Please try again.'),
                variant: "destructive",
            })
        } finally {
            setLoading(false)
        }
    }

    const handleSaveCompanySettings = async () => {
        setLoading(true)
        try {
            await updateCompanySettings({
                name: companyName,
                email: companyEmail,
                phone: companyPhone,
                address: companyAddress,
                registration_number: registrationNumber,
                country: companyCountry,
                bank_details: bankDetails,
                mobile_money_accounts: mobileMoneyAccounts,
                government_tax_percent: governmentTaxPercent,
                admin_fee: adminFee,
            })

            toast({
                title: t('Company settings saved'),
                description: t('Company information has been updated successfully.'),
            })
        } catch (error: any) {
            if (error.response?.status === 403) {
                setShowAccessDenied(true)
            } else {
                toast({
                    title: t('Error'),
                    description: t('Failed to save company settings. You may not have admin access.'),
                    variant: "destructive",
                })
            }
        } finally {
            setLoading(false)
        }
    }

    const handleRoleChange = async (userId: string, newRole: string) => {
        try {
            await userApi.update(userId, { role: newRole })
            // Update local state
            setUsers(users.map(user =>
                user.id === userId ? { ...user, role: newRole as User['role'] } : user
            ))
            toast({
                title: t('Role updated'),
                description: t('User role has been updated successfully.'),
            })
        } catch (error: any) {
            if (error.response?.status === 403) {
                setShowAccessDenied(true)
            } else {
                toast({
                    title: t('Error'),
                    description: t('Failed to update user role. You may not have admin access.'),
                    variant: "destructive",
                })
            }
        }
    }

    const handleToggleUserStatus = async (userId: string) => {
        const user = users.find(u => u.id === userId);
        if (!user) return;

        try {
            const updatedUser = await userApi.update(userId, { is_active: !user.is_active })
            // Update local state
            setUsers(users.map(u =>
                u.id === userId ? updatedUser : u
            ))
            toast({
                title: t('Status updated'),
                description: t('User has been activated/deactivated'),
            })
        } catch (error) {
            toast({
                title: t('Error'),
                description: t('Failed to update user status.'),
                variant: "destructive",
            })
        }
    }

    const addBankAccount = () => {
        setBankDetails([
            ...bankDetails,
            {
                bank_name: "",
                account_number: "",
                account_name: "",
                swift_code: "",
                branch: "",
            },
        ])
    }

    const removeBankAccount = (index: number) => {
        setBankDetails(bankDetails.filter((_, i) => i !== index))
    }

    const updateBankAccount = (index: number, field: keyof BankDetails, value: string) => {
        const updated = [...bankDetails]
        updated[index] = { ...updated[index], [field]: value }
        setBankDetails(updated)
    }

    const addMobileMoneyAccount = () => {
        setMobileMoneyAccounts([
            ...mobileMoneyAccounts,
            {
                provider: "",
                account_number: "",
                account_name: "",
            },
        ])
    }

    const removeMobileMoneyAccount = (index: number) => {
        setMobileMoneyAccounts(mobileMoneyAccounts.filter((_, i) => i !== index))
    }

    const updateMobileMoneyAccount = (
        index: number,
        field: keyof MobileMoneyAccount,
        value: string
    ) => {
        const updated = [...mobileMoneyAccounts]
        updated[index] = { ...updated[index], [field]: value }
        setMobileMoneyAccounts(updated)
    }

    if (!isMounted) return null

    return (
        <div className="container mx-auto py-10 space-y-8">
            <div className="flex justify-between items-center">
                <div>
                    <h2 className="text-3xl font-bold tracking-tight">{t('nav.settings', 'Settings')}</h2>
                    <p className="text-muted-foreground">
                        {t('settings.header_desc', 'Manage all your application settings in one place')}
                    </p>
                </div>
                <div className="flex gap-2">
                    <Button variant="outline" onClick={() => setPermissionsModalOpen(true)}>
                        <UserCog className="mr-2 h-4 w-4" />
                        {t('settings.permissions.title', 'User Permissions')}
                    </Button>
                    <Button variant="outline" asChild>
                        <Link href="/dashboard/settings/keys">API Keys →</Link>
                    </Button>
                </div>
            </div>

            {/* Two-Factor Authentication */}
            <TwoFactorSettings />

            {/* Theme & Language */}
            <Card>
                <CardHeader>
                    <CardTitle>{t('settings.language.title', 'Language')} & {t('settings.theme.title', 'Theme')}</CardTitle>
                    <CardDescription>
                        {t('settings.theme.customize', 'Customize your display preferences and language')}
                    </CardDescription>
                </CardHeader>
                <CardContent className="space-y-6">
                    <div className="space-y-3">
                        <Label>{t('settings.theme.title', 'Theme')}</Label>
                        <div className="grid grid-cols-2 gap-4 max-w-md">
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
                    </div>

                    <div className="space-y-3">
                        <Label>{t('settings.language.title', 'Language')}</Label>
                        <RadioGroup
                            value={language}
                            onValueChange={(val) => {
                                setLanguage(val);
                                setContextLanguage(val as "en" | "fr");
                            }}
                            className="max-w-md"
                        >
                            <div className="space-y-2">
                                {SUPPORTED_LANGUAGES.map((lang) => (
                                    <div
                                        key={lang.code}
                                        className="flex items-center space-x-3 p-3 border rounded-lg hover:bg-accent/50 transition-colors"
                                    >
                                        <RadioGroupItem value={lang.code} id={lang.code} />
                                        <Label
                                            htmlFor={lang.code}
                                            className="flex items-center space-x-3 flex-1 cursor-pointer"
                                        >
                                            <span className="text-2xl">{lang.flag}</span>
                                            <span className="font-medium">{lang.name}</span>
                                        </Label>
                                    </div>
                                ))}
                            </div>
                        </RadioGroup>
                    </div>
                </CardContent>
            </Card>

            {/* Regional Settings */}
            <Card>
                <CardHeader>
                    <CardTitle>{t('settings.regional_title', 'Regional Settings')}</CardTitle>
                    <CardDescription>
                        {t('settings.regional_desc', 'Configure currency, timezone, and date format')}
                    </CardDescription>
                </CardHeader>
                <CardContent className="space-y-4">
                    <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                        <div className="space-y-2">
                            <Label htmlFor="currency">{t('settings.currency_label', 'Currency')}</Label>
                            <Select value={currency} onValueChange={setCurrency}>
                                <SelectTrigger id="currency">
                                    <SelectValue placeholder={t('common.select_currency', 'Select currency')} />
                                </SelectTrigger>
                                <SelectContent>
                                    {SUPPORTED_CURRENCIES.map((curr) => (
                                        <SelectItem key={curr.code} value={curr.code}>
                                            {curr.symbol} - {curr.name}
                                        </SelectItem>
                                    ))}
                                </SelectContent>
                            </Select>
                        </div>

                        <div className="space-y-2">
                            <Label htmlFor="timezone">{t('settings.timezone_label', 'Timezone')}</Label>
                            <Select value={timezone} onValueChange={setTimezone}>
                                <SelectTrigger id="timezone">
                                    <SelectValue placeholder={t('common.select_timezone', 'Select timezone')} />
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

                        <div className="space-y-2">
                            <Label htmlFor="dateFormat">{t('settings.date_format_label', 'Date Format')}</Label>
                            <Select value={dateFormat} onValueChange={setDateFormat}>
                                <SelectTrigger id="dateFormat">
                                    <SelectValue placeholder={t('common.select_date_format', 'Select date format')} />
                                </SelectTrigger>
                                <SelectContent>
                                    {DATE_FORMATS.map((format) => (
                                        <SelectItem key={format.value} value={format.value}>
                                            {format.label}
                                        </SelectItem>
                                    ))}
                                </SelectContent>
                            </Select>
                        </div>
                    </div>

                    <Button onClick={handleSaveUserSettings} disabled={loading}>
                        <Save className="mr-2 h-4 w-4" />
                        {loading ? t('settings.saving', 'Saving...') : t('settings.save_changes', 'Save Changes')}
                    </Button>
                </CardContent>
            </Card>

            {/* AI Subscription & Quotas */}
            <AiSubscriptionSettings />

            {/* Super Admin AI Controls */}
            {user?.role === "super_admin" && (
                <SuperAdminAISettings />
            )}

            {/* User Permissions */}
            {users.length > 0 && (
                <Card>
                    <CardHeader>
                        <div className="flex justify-between items-center">
                            <div>
                                <CardTitle>{t('settings.permissions.title', 'User Permissions')}{t('common.admin_only', ' (Admin Only)')}</CardTitle>
                                <CardDescription>
                                    {t('settings.permissions.desc', 'Manage user roles and access levels')}
                                </CardDescription>
                            </div>
                            <UserCog className="h-5 w-5 text-muted-foreground" />
                        </div>
                    </CardHeader>
                    <CardContent>
                        <div className="rounded-md border">
                            <Table>
                                <TableHeader>
                                    <TableRow>
                                        <TableHead>{t('settings.permissions.table.name', 'Name')}</TableHead>
                                        <TableHead>{t('settings.permissions.table.email', 'Email')}</TableHead>
                                        <TableHead>{t('settings.permissions.table.role', 'Current Role')}</TableHead>
                                        <TableHead>{t('settings.permissions.table.action', 'Change Role')}</TableHead>
                                        <TableHead>{t('settings.permissions.table.status', 'Status')}</TableHead>
                                    </TableRow>
                                </TableHeader>
                                <TableBody>
                                    {users.map((user) => (
                                        <TableRow key={user.id}>
                                            <TableCell className="font-medium">
                                                {user.first_name} {user.last_name}
                                            </TableCell>
                                            <TableCell>{user.email}</TableCell>
                                            <TableCell>
                                                <Badge variant={(user.role === 'company_admin' || user.role === 'super_admin') ? 'default' : 'secondary'}>
                                                    {user.role}
                                                </Badge>
                                            </TableCell>
                                            <TableCell>
                                                <Select
                                                    value={user.role}
                                                    onValueChange={(value) => handleRoleChange(user.id, value)}
                                                >
                                                    <SelectTrigger className="w-[140px]">
                                                        <SelectValue />
                                                    </SelectTrigger>
                                                    <SelectContent>
                                                        <SelectItem value="company_admin">{t('roles.admin', 'Admin')}</SelectItem>
                                                        <SelectItem value="manager">{t('roles.manager', 'Manager')}</SelectItem>
                                                        <SelectItem value="agent">{t('roles.agent', 'Agent')}</SelectItem>
                                                        <SelectItem value="client">{t('roles.client', 'Client')}</SelectItem>
                                                    </SelectContent>
                                                </Select>
                                            </TableCell>
                                            <TableCell>
                                                <Badge variant={user.is_active ? 'default' : 'destructive'}>
                                                    {user.is_active ? t('Active') : t('Inactive')}
                                                </Badge>
                                            </TableCell>
                                        </TableRow>
                                    ))}
                                </TableBody>
                            </Table>
                        </div>
                        <p className="text-sm text-muted-foreground mt-4">
                            {t('settings.permissions.tip', '💡 Tip: Change user roles to control their access to different parts of the system. Clients can only access the client portal, while employees and accountants have dashboard access.')}
                        </p>
                    </CardContent>
                </Card>
            )}

            {/* Company Information */}
            <Card>
                <CardHeader>
                    <CardTitle>{t('settings.company.title_admin', 'Company Information')}{t('common.admin_only', ' (Admin Only)')}</CardTitle>
                    <CardDescription>
                        {t('settings.company.details_desc', 'Manage company details, branding, and financial accounts')}
                    </CardDescription>
                </CardHeader>
                <CardContent className="space-y-6">
                    {/* Basic Company Info */}
                    <div className="space-y-4">
                        <h3 className="font-semibold text-lg">{t('settings.company.basic_info', 'Basic Information')}</h3>
                        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                            <div className="space-y-2">
                                <Label htmlFor="companyName">{t('settings.company.name_label', 'Company Name')}</Label>
                                <Input
                                    id="companyName"
                                    value={companyName}
                                    onChange={(e) => setCompanyName(e.target.value)}
                                    placeholder="Demo Insurance Co."
                                />
                            </div>
                            <div className="space-y-2">
                                <Label htmlFor="regNumber">{t('settings.company.reg_number', 'Registration Number')}</Label>
                                <Input
                                    id="regNumber"
                                    value={registrationNumber}
                                    onChange={(e) => setRegistrationNumber(e.target.value)}
                                    placeholder="REG-123456"
                                />
                            </div>
                            <div className="space-y-2">
                                <Label htmlFor="companyEmail">{t('settings.company.email', 'Email')}</Label>
                                <Input
                                    id="companyEmail"
                                    type="email"
                                    value={companyEmail}
                                    onChange={(e) => setCompanyEmail(e.target.value)}
                                    placeholder="info@company.com"
                                />
                            </div>
                            <div className="space-y-2">
                                <Label htmlFor="companyPhone">{t('settings.company.phone', 'Phone')}</Label>
                                <Input
                                    id="companyPhone"
                                    value={companyPhone}
                                    onChange={(e) => setCompanyPhone(e.target.value)}
                                    placeholder="+1 (555) 123-4567"
                                />
                            </div>
                            <div className="space-y-2 md:col-span-2">
                                <Label htmlFor="companyAddress">{t('settings.company.address', 'Address')}</Label>
                                <Textarea
                                    id="companyAddress"
                                    value={companyAddress}
                                    onChange={(e) => setCompanyAddress(e.target.value)}
                                    placeholder="123 Main Street, City, State, ZIP"
                                    rows={2}
                                />
                            </div>
                            <div className="space-y-2">
                                <Label htmlFor="companyCountry">{t('settings.company.country', 'Country')}</Label>
                                <Select value={companyCountry} onValueChange={setCompanyCountry}>
                                    <SelectTrigger id="companyCountry">
                                        <SelectValue placeholder={t('common.select_country', 'Select country')} />
                                    </SelectTrigger>
                                    <SelectContent>
                                        {SUPPORTED_COUNTRIES.map((country) => (
                                            <SelectItem key={country.code} value={country.code}>
                                                {country.name}
                                            </SelectItem>
                                        ))}
                                    </SelectContent>
                                </Select>
                            </div>
                        </div>
                    </div>


                    {/* Mandatory Fees Configuration */}
                    <div className="space-y-4">
                        <h3 className="font-semibold text-lg">{t('settings.fees.title', 'Mandatory Fees')}</h3>
                        <p className="text-sm text-muted-foreground">
                            {t('settings.fees.desc', 'These fees will be automatically applied to all new quotes generated.')}
                        </p>
                        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                            <div className="space-y-2">
                                <Label htmlFor="govtTax">{t('settings.fees.govt_tax', 'Government Tax (TVA) %')}</Label>
                                <div className="relative">
                                    <Input
                                        id="govtTax"
                                        type="number"
                                        min="0"
                                        step="0.1"
                                        value={governmentTaxPercent}
                                        onChange={(e) => setGovernmentTaxPercent(parseFloat(e.target.value) || 0)}
                                        placeholder="0.0"
                                    />
                                    <div className="absolute inset-y-0 right-0 pr-3 flex items-center pointer-events-none">
                                        <span className="text-gray-500">%</span>
                                    </div>
                                </div>
                                <p className="text-xs text-muted-foreground">{t('settings.fees.govt_tax_help', 'Applied as a percentage of the subtotal.')}</p>
                            </div>
                            <div className="space-y-2">
                                <Label htmlFor="adminFee">{t('settings.fees.admin_fee', 'Company Admin Fee (Fixed)')}</Label>
                                <div className="relative">
                                    <div className="absolute inset-y-0 left-0 pl-3 flex items-center pointer-events-none">
                                        <span className="text-gray-500">{currency}</span>
                                    </div>
                                    <Input
                                        id="adminFee"
                                        type="number"
                                        min="0"
                                        step="1"
                                        className="pl-12"
                                        value={adminFee}
                                        onChange={(e) => setAdminFee(parseFloat(e.target.value) || 0)}
                                        placeholder="0.00"
                                    />
                                </div>
                                <p className="text-xs text-muted-foreground">{t('settings.fees.admin_fee_help', 'Fixed amount added to every quote.')}</p>
                            </div>
                        </div>
                    </div>

                    {/* Company Logo */}
                    <div className="space-y-4">
                        <h3 className="font-semibold text-lg">{t('settings.branding.title', 'Branding')}</h3>
                        <div className="flex items-center space-x-4">
                            <ProfileUploader
                                entityId={user?.company_id || 'company'}
                                entityType="user"
                                name={companyName || "Company Logo"}
                                currentImageUrl={logoUrl}
                                onUploadSuccess={loadSettings}
                                customEndpoint="/settings/company/logo"
                                size="lg"
                            />
                            <div className="text-sm text-muted-foreground">
                                <p>{t('settings.branding.upload_text', 'Upload your company logo here (PNG, JPG, SVG up to 5MB).')}</p>
                            </div>
                        </div>
                    </div>

                    {/* Bank Details */}
                    <div className="space-y-4">
                        <div className="flex justify-between items-center">
                            <h3 className="font-semibold text-lg">{t('settings.bank_accounts_title', 'Bank Accounts')}</h3>
                            <Button onClick={addBankAccount} variant="outline" size="sm">
                                <Plus className="h-4 w-4 mr-2" />
                                {t('settings.add_bank_account', 'Add Bank Account')}
                            </Button>
                        </div>
                        {bankDetails.length === 0 ? (
                            <p className="text-sm text-muted-foreground text-center py-4 border rounded-lg">
                                {t('settings.no_bank_accounts', 'No bank accounts added yet')}
                            </p>
                        ) : (
                            <div className="space-y-3">
                                {bankDetails.map((bank, index) => (
                                    <div key={index} className="p-4 border rounded-lg space-y-3">
                                        <div className="flex justify-between items-center">
                                            <h4 className="font-medium">{t('settings.bank_account_item', 'Bank Account')} {index + 1}</h4>
                                            <Button
                                                onClick={() => removeBankAccount(index)}
                                                variant="ghost"
                                                size="sm"
                                            >
                                                <Trash2 className="h-4 w-4 text-destructive" />
                                            </Button>
                                        </div>
                                        <div className="grid grid-cols-1 md:grid-cols-2 gap-3">
                                            <div className="space-y-2">
                                                <Label>{t('settings.bank_name', 'Bank Name')}</Label>
                                                <Input
                                                    value={bank.bank_name}
                                                    onChange={(e) =>
                                                        updateBankAccount(index, "bank_name", e.target.value)
                                                    }
                                                    placeholder="Bank of Example"
                                                />
                                            </div>
                                            <div className="space-y-2">
                                                <Label>{t('settings.account_number', 'Account Number')}</Label>
                                                <Input
                                                    value={bank.account_number}
                                                    onChange={(e) =>
                                                        updateBankAccount(index, "account_number", e.target.value)
                                                    }
                                                    placeholder="123456789"
                                                />
                                            </div>
                                            <div className="space-y-2">
                                                <Label>{t('settings.account_name', 'Account Name')}</Label>
                                                <Input
                                                    value={bank.account_name}
                                                    onChange={(e) =>
                                                        updateBankAccount(index, "account_name", e.target.value)
                                                    }
                                                    placeholder="Demo Insurance Co."
                                                />
                                            </div>
                                            <div className="space-y-2">
                                                <Label>{t('settings.swift_code', 'SWIFT/BIC Code')}</Label>
                                                <Input
                                                    value={bank.swift_code || ""}
                                                    onChange={(e) =>
                                                        updateBankAccount(index, "swift_code", e.target.value)
                                                    }
                                                    placeholder="ABCDUS33"
                                                />
                                            </div>
                                        </div>
                                    </div>
                                ))}
                            </div>
                        )}
                    </div>

                    {/* Mobile Money Accounts */}
                    <div className="space-y-4">
                        <div className="flex justify-between items-center">
                            <h3 className="font-semibold text-lg">{t('settings.mobile_money_title', 'Mobile Money Accounts')}</h3>
                            <Button onClick={addMobileMoneyAccount} variant="outline" size="sm">
                                <Plus className="h-4 w-4 mr-2" />
                                {t('settings.add_mobile_money', 'Add Mobile Money')}
                            </Button>
                        </div>
                        {mobileMoneyAccounts.length === 0 ? (
                            <p className="text-sm text-muted-foreground text-center py-4 border rounded-lg">
                                {t('settings.no_mobile_money', 'No mobile money accounts added yet')}
                            </p>
                        ) : (
                            <div className="space-y-3">
                                {mobileMoneyAccounts.map((account, index) => (
                                    <div key={index} className="p-4 border rounded-lg space-y-3">
                                        <div className="flex justify-between items-center">
                                            <h4 className="font-medium">{t('settings.mobile_money_item', 'Mobile Money Account')} {index + 1}</h4>
                                            <Button
                                                onClick={() => removeMobileMoneyAccount(index)}
                                                variant="ghost"
                                                size="sm"
                                            >
                                                <Trash2 className="h-4 w-4 text-destructive" />
                                            </Button>
                                        </div>
                                        <div className="grid grid-cols-1 md:grid-cols-2 gap-3">
                                            <div className="space-y-2">
                                                <Label>{t('settings.provider', 'Provider')}</Label>
                                                <Select
                                                    value={account.provider}
                                                    onValueChange={(value) =>
                                                        updateMobileMoneyAccount(index, "provider", value)
                                                    }
                                                >
                                                    <SelectTrigger>
                                                        <SelectValue placeholder={t('common.select_provider', 'Select provider')} />
                                                    </SelectTrigger>
                                                    <SelectContent>
                                                        {MOBILE_MONEY_PROVIDERS.map((provider) => (
                                                            <SelectItem key={provider} value={provider}>
                                                                {provider}
                                                            </SelectItem>
                                                        ))}
                                                    </SelectContent>
                                                </Select>
                                            </div>
                                            <div className="space-y-2">
                                                <Label>{t('settings.account_number', 'Account Number')}</Label>
                                                <Input
                                                    value={account.account_number}
                                                    onChange={(e) =>
                                                        updateMobileMoneyAccount(
                                                            index,
                                                            "account_number",
                                                            e.target.value
                                                        )
                                                    }
                                                    placeholder="0241234567"
                                                />
                                            </div>
                                            <div className="space-y-2 md:col-span-2">
                                                <Label>{t('settings.account_name', 'Account Name')}</Label>
                                                <Input
                                                    value={account.account_name}
                                                    onChange={(e) =>
                                                        updateMobileMoneyAccount(
                                                            index,
                                                            "account_name",
                                                            e.target.value
                                                        )
                                                    }
                                                    placeholder="Demo Insurance Co."
                                                />
                                            </div>
                                        </div>
                                    </div>
                                ))}
                            </div>
                        )}
                    </div>

                    <Button onClick={handleSaveCompanySettings} disabled={loading}>
                        <Save className="mr-2 h-4 w-4" />
                        {loading ? t('settings.saving', 'Saving...') : t('settings.save_changes', 'Save Changes')}
                    </Button>
                </CardContent>
            </Card>

            {/* User Permissions Modal */}
            <UserPermissionsModal
                open={permissionsModalOpen}
                onOpenChange={setPermissionsModalOpen}
            />

            {/* Access Denied Modal */}
            <PermissionDeniedModal
                isOpen={showAccessDenied}
                onClose={() => setShowAccessDenied(false)}
            />
        </div>
    )
}
