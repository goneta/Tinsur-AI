"use client"

import { useState } from "react"
import {
    Dialog,
    DialogContent,
    DialogDescription,
    DialogHeader,
    DialogTitle,
    DialogTrigger,
    DialogFooter
} from "@/components/ui/dialog"
import { Button } from "@/components/ui/button"
import { Label } from "@/components/ui/label"
import { Input } from "@/components/ui/input"
import { RadioGroup, RadioGroupItem } from "@/components/ui/radio-group"
import {
    CreditCard,
    Smartphone,
    Plus,
    ChevronRight,
    CheckCircle2,
    Loader2
} from "lucide-react"
import { subscriptionApi } from "@/lib/subscription-api"
import { useToast } from "@/components/ui/use-toast"
import { Badge } from "@/components/ui/badge"

interface TopupDialogProps {
    onSuccess: () => void
}

import { useLanguage } from "@/contexts/language-context"

const PRESET_AMOUNTS = [10, 20, 50, 100]

export function TopupDialog({ onSuccess }: TopupDialogProps) {
    const { t, formatPrice } = useLanguage()
    const { toast } = useToast()
    const [open, setOpen] = useState(false)
    const [step, setStep] = useState(1)
    const [loading, setLoading] = useState(false)
    const [amount, setAmount] = useState<number>(20)
    const [customAmount, setCustomAmount] = useState("")
    const [method, setMethod] = useState<"stripe" | "mobile_money">("stripe")
    const [provider, setProvider] = useState<"orange_money" | "mtn_money" | "wave" | "moov_money" | "djamo">("wave")
    const [phoneNumber, setPhoneNumber] = useState("")
    const [paymentResult, setPaymentResult] = useState<any>(null)

    const finalAmount = amount === 0 ? parseFloat(customAmount) || 0 : amount

    const handleInitiate = async () => {
        if (finalAmount <= 0) {
            toast({ title: "Invalid amount", variant: "destructive" })
            return
        }

        if (method === "mobile_money" && !phoneNumber) {
            toast({ title: "Phone number required", variant: "destructive" })
            return
        }

        setLoading(true)
        try {
            const result = await subscriptionApi.initiateTopup({
                amount: finalAmount,
                payment_method: method,
                payment_gateway: method === "mobile_money" ? provider : "stripe",
                phone_number: phoneNumber,
                success_url: window.location.href,
                cancel_url: window.location.href
            })

            setPaymentResult(result)

            if (method === "stripe" && result.gateway_response?.checkout_url) {
                // Redirect to Stripe
                window.location.href = result.gateway_response.checkout_url
            } else {
                // Show instructions for Mobile Money
                setStep(3)
            }
        } catch (error) {
            toast({
                title: "Top-up failed",
                description: "There was an error initiating your payment.",
                variant: "destructive"
            })
        } finally {
            setLoading(false)
        }
    }

    const reset = () => {
        setOpen(false)
        setStep(1)
        setPaymentResult(null)
        setPhoneNumber("")
    }

    return (
        <Dialog open={open} onOpenChange={setOpen}>
            <DialogTrigger asChild>
                <Button variant="outline" size="sm" className="gap-2">
                    <Plus className="h-4 w-4" />
                    <Plus className="h-4 w-4" />
                    {t('settings.topup.top_up_btn', 'Top up Credits')}
                </Button>
            </DialogTrigger>
            <DialogContent className="sm:max-w-[450px]">
                <DialogHeader>
                    <DialogTitle>{t('settings.topup.title', 'Top up AI Credits')}</DialogTitle>
                    <DialogDescription>
                        {t('settings.topup.desc', 'Purchase credits to keep your AI agents running.')}
                    </DialogDescription>
                </DialogHeader>

                {step === 1 && (
                    <div className="space-y-6 py-4">
                        <div className="space-y-3">
                            <Label>{t('settings.topup.select_amount', 'Select Amount')}</Label>
                            <div className="grid grid-cols-2 gap-3">
                                {PRESET_AMOUNTS.map((a) => (
                                    <Button
                                        key={a}
                                        variant={amount === a ? "default" : "outline"}
                                        className="py-6 text-lg font-bold"
                                        onClick={() => {
                                            setAmount(a)
                                            setCustomAmount("")
                                        }}
                                    >
                                        {formatPrice(a)}
                                    </Button>
                                ))}
                                <div className="col-span-2 relative">
                                    <Input
                                        placeholder={t('settings.topup.custom_amount', 'Custom amount')}
                                        className="pl-8 text-lg"
                                        type="number"
                                        value={customAmount}
                                        onChange={(e) => {
                                            setAmount(0)
                                            setCustomAmount(e.target.value)
                                        }}
                                    />
                                    {/* Removed absolute dollar sign as formatPrice handles symbol, but input is raw number */}
                                </div>
                            </div>
                        </div>

                        <Button className="w-full" onClick={() => setStep(2)}>
                            {t('settings.topup.next_payment', 'Next: Payment Method')} <ChevronRight className="ml-2 h-4 w-4" />
                        </Button>
                    </div>
                )}

                {step === 2 && (
                    <div className="space-y-6 py-4">
                        <RadioGroup
                            value={method}
                            onValueChange={(v: any) => setMethod(v)}
                            className="space-y-3"
                        >
                            <div className={`border rounded-xl p-4 cursor-pointer transition-all ${method === "stripe" ? "border-primary bg-primary/5" : "hover:bg-accent"}`}>
                                <RadioGroupItem value="stripe" id="stripe" className="sr-only" />
                                <Label htmlFor="stripe" className="flex items-center gap-4 cursor-pointer">
                                    <div className="p-2 bg-blue-100 text-blue-600 rounded-lg">
                                        <CreditCard className="h-6 w-6" />
                                    </div>
                                    <div className="flex-grow">
                                        <p className="font-bold">Stripe / Credit Card</p>
                                        <p className="text-xs text-muted-foreground">Visa, Mastercard, AMEX</p>
                                    </div>
                                    <div className={`w-4 h-4 rounded-full border-2 ${method === "stripe" ? "border-primary bg-primary" : "border-muted"}`} />
                                </Label>
                            </div>

                            <div className={`border rounded-xl p-4 cursor-pointer transition-all ${method === "mobile_money" ? "border-primary bg-primary/5" : "hover:bg-accent"}`}>
                                <RadioGroupItem value="mobile_money" id="mm" className="sr-only" />
                                <Label htmlFor="mm" className="flex items-center gap-4 cursor-pointer">
                                    <div className="p-2 bg-orange-100 text-orange-600 rounded-lg">
                                        <Smartphone className="h-6 w-6" />
                                    </div>
                                    <div className="flex-grow">
                                        <p className="font-bold">Mobile Money</p>
                                        <p className="text-xs text-muted-foreground">Orange, MTN, Wave</p>
                                    </div>
                                    <div className={`w-4 h-4 rounded-full border-2 ${method === "mobile_money" ? "border-primary bg-primary" : "border-muted"}`} />
                                </Label>
                            </div>
                        </RadioGroup>

                        {method === "mobile_money" && (
                            <div className="space-y-4 animate-in fade-in slide-in-from-top-2 duration-300">
                                <div className="grid grid-cols-2 gap-2">
                                    {(["orange_money", "mtn_money", "wave", "moov_money", "djamo"] as const).map((p) => (
                                        <Button
                                            key={p}
                                            variant={provider === p ? "default" : "outline"}
                                            size="sm"
                                            className="capitalize"
                                            onClick={() => setProvider(p)}
                                        >
                                            {p.replace("_money", "")}
                                        </Button>
                                    ))}
                                </div>
                                <div className="space-y-2">
                                    <Label>Phone Number</Label>
                                    <Input
                                        placeholder="0123456789"
                                        value={phoneNumber}
                                        onChange={(e) => setPhoneNumber(e.target.value)}
                                    />
                                </div>
                            </div>
                        )}

                        <div className="flex gap-3">
                            <Button variant="outline" className="flex-grow" onClick={() => setStep(1)}>Back</Button>
                            <Button className="flex-grow gap-2" onClick={handleInitiate} disabled={loading}>
                                {loading ? <Loader2 className="h-4 w-4 animate-spin" /> : `${t('settings.topup.pay', 'Pay')} ${formatPrice(finalAmount)}`}
                            </Button>
                        </div>
                    </div>
                )}

                {step === 3 && (
                    <div className="py-8 flex flex-col items-center text-center space-y-4 animate-in zoom-in-95 duration-300">
                        <div className="w-16 h-16 bg-green-100 text-green-600 rounded-full flex items-center justify-center">
                            <CheckCircle2 className="h-10 w-10" />
                        </div>
                        <div className="space-y-2">
                            <h3 className="text-xl font-bold">{t('settings.topup.initiated_title', 'Payment Initiated!')}</h3>
                            <p className="text-sm text-muted-foreground px-4">
                                {paymentResult?.gateway_response?.instructions || t('settings.topup.initiated_desc', 'Please check your phone to confirm the transaction.')}
                            </p>
                            {paymentResult?.payment_id && (
                                <Badge variant="secondary" className="font-mono mt-2">
                                    ID: {paymentResult.payment_id.split('-')[0]}...
                                </Badge>
                            )}
                        </div>
                        <Button className="w-full mt-4" onClick={reset}>
                            {t('settings.topup.got_it', 'Got it')}
                        </Button>
                    </div>
                )}
            </DialogContent>
        </Dialog>
    )
}
