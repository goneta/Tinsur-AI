"use client"

import { useState, useEffect } from "react"
import { useRouter } from "next/navigation"
import { ArrowLeft, Plus, Trash2, Upload, Building2 } from "lucide-react"
import Link from "next/link"
import Image from "next/image"

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
import { Textarea } from "@/components/ui/textarea"
import {
    Select,
    SelectContent,
    SelectItem,
    SelectTrigger,
    SelectValue,
} from "@/components/ui/select"
import {
    getCompanySettings,
    updateCompanySettings,
    uploadCompanyLogo,
} from "@/lib/settings-api"
import {
    CompanySettings,
    BankDetails,
    MobileMoneyAccount,
    SUPPORTED_CURRENCIES,
    SUPPORTED_COUNTRIES,
    MOBILE_MONEY_PROVIDERS,
} from "@/types/settings"
import { useToast } from "@/components/ui/use-toast"
import { useLanguage } from "@/contexts/language-context"

export default function CompanySettingsPage() {
    const { t } = useLanguage()
    const router = useRouter()
    const { toast } = useToast()
    const [loading, setLoading] = useState(false)
    const [initialLoading, setInitialLoading] = useState(true)
    const [uploadingLogo, setUploadingLogo] = useState(false)

    // Company info state
    const [name, setName] = useState("")
    const [email, setEmail] = useState("")
    const [phone, setPhone] = useState("")
    const [address, setAddress] = useState("")
    const [registrationNumber, setRegistrationNumber] = useState("")
    const [logoUrl, setLogoUrl] = useState("")
    const [currency, setCurrency] = useState("USD")
    const [country, setCountry] = useState("")
    const [primaryColor, setPrimaryColor] = useState("#000000")
    const [secondaryColor, setSecondaryColor] = useState("#e6e8eb")

    // Financial Settings
    const [aprPercent, setAprPercent] = useState("")
    const [arrangementFee, setArrangementFee] = useState("")
    const [extraFee, setExtraFee] = useState("")
    const [governmentTaxPercent, setGovernmentTaxPercent] = useState("")
    const [adminFee, setAdminFee] = useState("")

    // Bank details state
    const [bankDetails, setBankDetails] = useState<BankDetails[]>([])
    const [mobileMoneyAccounts, setMobileMoneyAccounts] = useState<
        MobileMoneyAccount[]
    >([])

    useEffect(() => {
        loadSettings()
    }, [])

    const loadSettings = async () => {
        try {
            const settings = await getCompanySettings()
            setName(settings.name)
            setEmail(settings.email)
            setPhone(settings.phone || "")
            setAddress(settings.address || "")
            setRegistrationNumber(settings.registration_number || "")
            setLogoUrl(settings.logo_url || "")
            setCurrency(settings.currency)
            setCountry(settings.country || "")
            setPrimaryColor(settings.primary_color || "#000000")
            setPrimaryColor(settings.primary_color || "#000000")
            setSecondaryColor(settings.secondary_color || "#e6e8eb")
            setAprPercent(settings.apr_percent?.toString() || "0")
            setArrangementFee(settings.arrangement_fee?.toString() || "0")
            setExtraFee(settings.extra_fee?.toString() || "0")
            setGovernmentTaxPercent(settings.government_tax_percent?.toString() || "0")
            setAdminFee(settings.admin_fee?.toString() || "0")
            setBankDetails(settings.bank_details || [])
            setMobileMoneyAccounts(settings.mobile_money_accounts || [])
        } catch (error) {
            console.error("Failed to load company settings:", error)
            // Use defaults if backend is not available - don't show error toast on initial load
            // User can still interact with the form
        } finally {
            setInitialLoading(false)
        }
    }

    const handleSave = async () => {
        setLoading(true)
        try {
            await updateCompanySettings({
                name,
                email,
                phone,
                address,
                registration_number: registrationNumber,
                currency,
                country,
                bank_details: bankDetails,
                mobile_money_accounts: mobileMoneyAccounts,
                primary_color: primaryColor,
                secondary_color: secondaryColor,
                apr_percent: parseFloat(aprPercent),
                arrangement_fee: parseFloat(arrangementFee),
                extra_fee: parseFloat(extraFee),
                government_tax_percent: parseFloat(governmentTaxPercent),
                admin_fee: parseFloat(adminFee),
            })

            toast({
                title: "Settings saved",
                description: "Company information has been updated successfully.",
            })
        } catch (error) {
            toast({
                title: "Error",
                description: "Failed to save company settings. Please try again.",
                variant: "destructive",
            })
        } finally {
            setLoading(false)
        }
    }

    const handleLogoUpload = async (e: React.ChangeEvent<HTMLInputElement>) => {
        const file = e.target.files?.[0]
        if (!file) return

        setUploadingLogo(true)
        try {
            const result = await uploadCompanyLogo(file)
            setLogoUrl(result.logo_url)
            toast({
                title: "Logo uploaded",
                description: "Company logo has been updated successfully.",
            })
        } catch (error) {
            toast({
                title: "Error",
                description: "Failed to upload logo. Please try again.",
                variant: "destructive",
            })
        } finally {
            setUploadingLogo(false)
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
                        {t('settings.company.title_admin', 'Company Information (Administration Only)')}
                    </h2>
                    <p className="text-muted-foreground">
                        {t('settings.company.desc', 'Manage your company details, branding, and financial accounts')}
                    </p>
                </div>
            </div>

            <div className="grid gap-6 max-w-4xl">
                {/* Basic Information */}
                <Card>
                    <CardHeader>
                        <CardTitle>{t('settings.company.basic_info', 'Basic Information')}</CardTitle>
                        <CardDescription>
                            {t('settings.company.details_desc', 'Company details that appear on receipts, policies, and quotes')}
                        </CardDescription>
                    </CardHeader>
                    <CardContent className="space-y-4">
                        <div className="grid grid-cols-2 gap-4">
                            <div className="space-y-2">
                                <Label htmlFor="name">{t('settings.company.name_label', 'Company Name')} *</Label>
                                <Input
                                    id="name"
                                    value={name}
                                    onChange={(e) => setName(e.target.value)}
                                    placeholder="Demo Insurance Co."
                                />
                            </div>
                            <div className="space-y-2">
                                <Label htmlFor="regNumber">{t('settings.company.rccm_number', 'Company Number (N° RCCM)')}</Label>
                                <Input
                                    id="regNumber"
                                    value={registrationNumber}
                                    onChange={(e) =>
                                        setRegistrationNumber(e.target.value)
                                    }
                                    placeholder="REG-123456"
                                />
                            </div>
                        </div>

                        <div className="grid grid-cols-2 gap-4">
                            <div className="space-y-2">
                                <Label htmlFor="email">{t('settings.company.email', 'Email')} *</Label>
                                <Input
                                    id="email"
                                    type="email"
                                    value={email}
                                    onChange={(e) => setEmail(e.target.value)}
                                    placeholder="info@company.com"
                                />
                            </div>
                            <div className="space-y-2">
                                <Label htmlFor="phone">{t('settings.company.phone', 'Phone')}</Label>
                                <Input
                                    id="phone"
                                    value={phone}
                                    onChange={(e) => setPhone(e.target.value)}
                                    placeholder="+1 (555) 123-4567"
                                />
                            </div>
                        </div>

                        <div className="space-y-2">
                            <Label htmlFor="address">{t('settings.company.address', 'Address')}</Label>
                            <Textarea
                                id="address"
                                value={address}
                                onChange={(e) => setAddress(e.target.value)}
                                placeholder="123 Main Street, City, State, ZIP"
                                rows={3}
                            />
                        </div>

                        <div className="grid grid-cols-2 gap-4">
                            <div className="space-y-2">
                                <Label htmlFor="currency">{t('settings.regional.currency', 'Currency')}</Label>
                                <Select value={currency} onValueChange={setCurrency}>
                                    <SelectTrigger id="currency">
                                        <SelectValue />
                                    </SelectTrigger>
                                    <SelectContent>
                                        {SUPPORTED_CURRENCIES.map((curr) => (
                                            <SelectItem
                                                key={curr.code}
                                                value={curr.code}
                                            >
                                                {curr.symbol} - {curr.name}
                                            </SelectItem>
                                        ))}
                                    </SelectContent>
                                </Select>
                            </div>
                            <div className="space-y-2">
                                <Label htmlFor="country">{t('settings.company.country', 'Country')}</Label>
                                <Select value={country} onValueChange={setCountry}>
                                    <SelectTrigger id="country">
                                        <SelectValue placeholder="Select country" />
                                    </SelectTrigger>
                                    <SelectContent>
                                        {SUPPORTED_COUNTRIES.map((country) => (
                                            <SelectItem
                                                key={country.code}
                                                value={country.code}
                                            >
                                                {country.name}
                                            </SelectItem>
                                        ))}
                                    </SelectContent>
                                </Select>
                            </div>
                        </div>
                    </CardContent>
                </Card>



                {/* Interest & Fees */}
                <Card>
                    <CardHeader>
                        <CardTitle>{t('settings.fees.title', 'Interest & Fees')}</CardTitle>
                        <CardDescription>
                            {t('settings.fees.desc', 'Configure financial rates and fees for quotes.')}
                        </CardDescription>
                    </CardHeader>
                    <CardContent className="space-y-4">
                        <div className="grid grid-cols-3 gap-4">
                            <div className="space-y-2">
                                <Label htmlFor="aprPercent">{t('settings.fees.apr', 'APR (Gov. Tax Rate) %')}</Label>
                                <Input
                                    id="aprPercent"
                                    type="number"
                                    value={aprPercent}
                                    onChange={(e) => setAprPercent(e.target.value)}
                                    placeholder="14.0"
                                    step="0.01"
                                />
                            </div>
                            <div className="space-y-2">
                                <Label htmlFor="arrangementFee">{t('settings.fees.arrangement', 'Arrangement Fee (Interest)')}</Label>
                                <Input
                                    id="arrangementFee"
                                    type="number"
                                    value={arrangementFee}
                                    onChange={(e) => setArrangementFee(e.target.value)}
                                    placeholder="5000"
                                    step="100"
                                />
                            </div>
                            <div className="space-y-2">
                                <Label htmlFor="extraFee">{t('settings.fees.extra', 'Extra Fee')}</Label>
                                <Input
                                    id="extraFee"
                                    type="number"
                                    value={extraFee}
                                    onChange={(e) => setExtraFee(e.target.value)}
                                    placeholder="2000"
                                    step="100"
                                />
                            </div>
                            <div className="space-y-2">
                                <Label htmlFor="adminFee">{t('settings.fees.admin', 'Company Admin Fee')}</Label>
                                <Input
                                    id="adminFee"
                                    type="number"
                                    value={adminFee}
                                    onChange={(e) => setAdminFee(e.target.value)}
                                    placeholder="5000"
                                    step="100"
                                />
                            </div>
                            <div className="space-y-2">
                                <Label htmlFor="govTax">{t('settings.fees.tax', 'Government Tax (TVA) %')}</Label>
                                <Input
                                    id="govTax"
                                    type="number"
                                    value={governmentTaxPercent}
                                    onChange={(e) => setGovernmentTaxPercent(e.target.value)}
                                    placeholder="18.0"
                                    step="0.01"
                                />
                            </div>
                        </div>
                    </CardContent>
                </Card>

                {/* Branding (Logo & Colors) */}
                <Card>
                    <CardHeader>
                        <CardTitle>{t('settings.branding.title', 'Branding')}</CardTitle>
                        <CardDescription>
                            {t('settings.branding.desc', "Customize your platform's appearance with your logo and brand colors")}
                        </CardDescription>
                    </CardHeader>
                    <CardContent className="space-y-6">
                        <div className="flex items-center space-x-6">
                            {logoUrl ? (
                                <div className="relative w-32 h-32 border rounded-lg overflow-hidden bg-white shadow-sm">
                                    <Image
                                        src={logoUrl}
                                        alt="Company logo"
                                        fill
                                        className="object-contain p-2"
                                    />
                                </div>
                            ) : (
                                <div className="w-32 h-32 border-2 border-dashed rounded-lg flex items-center justify-center bg-muted/30">
                                    <Building2 className="h-12 w-12 text-muted-foreground" />
                                </div>
                            )}
                            <div className="flex-1 space-y-3">
                                <Label
                                    htmlFor="logo"
                                    className="cursor-pointer inline-block"
                                >
                                    <div className="flex items-center space-x-2 px-4 py-2 border rounded-lg hover:bg-accent transition-all duration-200">
                                        <Upload className="h-4 w-4" />
                                        <span className="font-medium">
                                            {uploadingLogo
                                                ? t('settings.uploading', 'Uploading...')
                                                : t('settings.branding.change_logo', 'Change Logo')}
                                        </span>
                                    </div>
                                </Label>
                                <Input
                                    id="logo"
                                    type="file"
                                    accept="image/*"
                                    onChange={handleLogoUpload}
                                    disabled={uploadingLogo}
                                    className="hidden"
                                />
                                <p className="text-xs text-muted-foreground">
                                    {t('settings.branding.upload_text', 'Upload a high-resolution logo. PNG, JPG, or SVG. Max 5MB.')}
                                </p>
                            </div>
                        </div>

                        <div className="grid grid-cols-2 gap-6 pt-4 border-t">
                            <div className="space-y-3">
                                <Label htmlFor="primaryColor" className="text-sm font-semibold">{t('settings.branding.primary_color', 'Primary Brand Color')}</Label>
                                <div className="flex items-center space-x-3">
                                    <Input
                                        id="primaryColor"
                                        type="color"
                                        value={primaryColor}
                                        onChange={(e) => setPrimaryColor(e.target.value)}
                                        className="w-16 h-10 p-1 cursor-pointer"
                                    />
                                    <Input
                                        type="text"
                                        value={primaryColor}
                                        onChange={(e) => setPrimaryColor(e.target.value)}
                                        className="flex-1 font-mono text-sm"
                                        placeholder="#000000"
                                    />
                                </div>
                                <p className="text-[10px] text-muted-foreground uppercase tracking-wider font-bold">Main buttons, sidebar headers, active states</p>
                            </div>
                            <div className="space-y-3">
                                <Label htmlFor="secondaryColor" className="text-sm font-semibold">{t('settings.branding.secondary_color', 'Secondary Brand Color')}</Label>
                                <div className="flex items-center space-x-3">
                                    <Input
                                        id="secondaryColor"
                                        type="color"
                                        value={secondaryColor}
                                        onChange={(e) => setSecondaryColor(e.target.value)}
                                        className="w-16 h-10 p-1 cursor-pointer"
                                    />
                                    <Input
                                        type="text"
                                        value={secondaryColor}
                                        onChange={(e) => setSecondaryColor(e.target.value)}
                                        className="flex-1 font-mono text-sm"
                                        placeholder="#E6E8EB"
                                    />
                                </div>
                                <p className="text-[10px] text-muted-foreground uppercase tracking-wider font-bold">Secondary buttons, background accents, muted states</p>
                            </div>
                        </div>
                    </CardContent>
                </Card>

                {/* Bank Details */}
                <Card>
                    <CardHeader>
                        <div className="flex items-center justify-between">
                            <div>
                                <CardTitle>{t('settings.bank_accounts_title', 'Bank Accounts')}</CardTitle>
                                <CardDescription>
                                    Add your bank account details for payments
                                </CardDescription>
                            </div>
                            <Button onClick={addBankAccount} variant="outline" size="sm">
                                <Plus className="h-4 w-4 mr-2" />
                                {t('settings.add_bank_account', 'Add Account')}
                            </Button>
                        </div>
                    </CardHeader>
                    <CardContent className="space-y-4">
                        {bankDetails.length === 0 ? (
                            <p className="text-sm text-muted-foreground text-center py-8">
                                {t('settings.no_bank_accounts', 'No bank accounts added yet')}
                            </p>
                        ) : (
                            bankDetails.map((bank, index) => (
                                <div
                                    key={index}
                                    className="p-4 border rounded-lg space-y-3"
                                >
                                    <div className="flex justify-between items-start">
                                        <h4 className="font-medium">
                                            {t('settings.bank_account_number', 'Bank Account {{number}}').replace('{{number}}', (index + 1).toString())}
                                        </h4>
                                        <Button
                                            onClick={() => removeBankAccount(index)}
                                            variant="ghost"
                                            size="sm"
                                        >
                                            <Trash2 className="h-4 w-4 text-destructive" />
                                        </Button>
                                    </div>
                                    <div className="grid grid-cols-2 gap-3">
                                        <div className="space-y-2">
                                            <Label>{t('settings.bank_name', 'Bank Name')}</Label>
                                            <Input
                                                value={bank.bank_name}
                                                onChange={(e) =>
                                                    updateBankAccount(
                                                        index,
                                                        "bank_name",
                                                        e.target.value
                                                    )
                                                }
                                                placeholder="Bank of Example"
                                            />
                                        </div>
                                        <div className="space-y-2">
                                            <Label>{t('settings.account_number', 'Account Number')}</Label>
                                            <Input
                                                value={bank.account_number}
                                                onChange={(e) =>
                                                    updateBankAccount(
                                                        index,
                                                        "account_number",
                                                        e.target.value
                                                    )
                                                }
                                                placeholder="123456789"
                                            />
                                        </div>
                                        <div className="space-y-2">
                                            <Label>{t('settings.account_name', 'Account Name')}</Label>
                                            <Input
                                                value={bank.account_name}
                                                onChange={(e) =>
                                                    updateBankAccount(
                                                        index,
                                                        "account_name",
                                                        e.target.value
                                                    )
                                                }
                                                placeholder="Demo Insurance Co."
                                            />
                                        </div>
                                        <div className="space-y-2">
                                            <Label>{t('settings.swift_bic_code', 'SWIFT/BIC Code')}</Label>
                                            <Input
                                                value={bank.swift_code || ""}
                                                onChange={(e) =>
                                                    updateBankAccount(
                                                        index,
                                                        "swift_code",
                                                        e.target.value
                                                    )
                                                }
                                                placeholder="ABCDUS33"
                                            />
                                        </div>
                                        <div className="space-y-2 col-span-2">
                                            <Label>{t('settings.branch', 'Branch')}</Label>
                                            <Input
                                                value={bank.branch || ""}
                                                onChange={(e) =>
                                                    updateBankAccount(
                                                        index,
                                                        "branch",
                                                        e.target.value
                                                    )
                                                }
                                                placeholder="Main Branch"
                                            />
                                        </div>
                                    </div>
                                </div>
                            ))
                        )}
                    </CardContent>
                </Card>

                {/* Mobile Money Accounts */}
                <Card>
                    <CardHeader>
                        <div className="flex items-center justify-between">
                            <div>
                                <CardTitle>{t('settings.mobile_money_title', 'Mobile Money Accounts')}</CardTitle>
                                <CardDescription>
                                    {t('settings.mobile_money_desc', 'Add your mobile money accounts for payments')}
                                </CardDescription>
                            </div>
                            <Button
                                onClick={addMobileMoneyAccount}
                                variant="outline"
                                size="sm"
                            >
                                <Plus className="h-4 w-4 mr-2" />
                                {t('settings.add_mobile_money', 'Add Account')}
                            </Button>
                        </div>
                    </CardHeader>
                    <CardContent className="space-y-4">
                        {mobileMoneyAccounts.length === 0 ? (
                            <p className="text-sm text-muted-foreground text-center py-8">
                                {t('settings.no_mobile_money', 'No mobile money accounts added yet')}
                            </p>
                        ) : (
                            mobileMoneyAccounts.map((account, index) => (
                                <div
                                    key={index}
                                    className="p-4 border rounded-lg space-y-3"
                                >
                                    <div className="flex justify-between items-start">
                                        <h4 className="font-medium">
                                            {t('settings.mobile_money_account_number', 'Mobile Money Account {{number}}').replace('{{number}}', (index + 1).toString())}
                                        </h4>
                                        <Button
                                            onClick={() =>
                                                removeMobileMoneyAccount(index)
                                            }
                                            variant="ghost"
                                            size="sm"
                                        >
                                            <Trash2 className="h-4 w-4 text-destructive" />
                                        </Button>
                                    </div>
                                    <div className="grid grid-cols-2 gap-3">
                                        <div className="space-y-2">
                                            <Label>Provider</Label>
                                            <Select
                                                value={account.provider}
                                                onValueChange={(value) =>
                                                    updateMobileMoneyAccount(
                                                        index,
                                                        "provider",
                                                        value
                                                    )
                                                }
                                            >
                                                <SelectTrigger>
                                                    <SelectValue placeholder="Select provider" />
                                                </SelectTrigger>
                                                <SelectContent>
                                                    {MOBILE_MONEY_PROVIDERS.map(
                                                        (provider) => (
                                                            <SelectItem
                                                                key={provider}
                                                                value={provider}
                                                            >
                                                                {provider}
                                                            </SelectItem>
                                                        )
                                                    )}
                                                </SelectContent>
                                            </Select>
                                        </div>
                                        <div className="space-y-2">
                                            <Label>Account Number</Label>
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
                                        <div className="space-y-2 col-span-2">
                                            <Label>Account Name</Label>
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
                            ))
                        )}
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
            </div >
        </div >
    )
}
