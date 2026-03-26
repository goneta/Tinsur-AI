"use client"

import {
    Dialog,
    DialogContent,
    DialogDescription,
    DialogFooter,
    DialogHeader,
    DialogTitle,
} from "@/components/ui/dialog"
import { Button } from "@/components/ui/button"
import { CreditCard, Zap, ShieldCheck } from "lucide-react"

interface CreditLimitModalProps {
    isOpen: boolean
    onClose: () => void
}

export function CreditLimitModal({ isOpen, onClose }: CreditLimitModalProps) {
    return (
        <Dialog open={isOpen} onOpenChange={onClose}>
            <DialogContent className="sm:max-w-[425px]">
                <DialogHeader>
                    <div className="mx-auto w-12 h-12 bg-yellow-100 rounded-full flex items-center justify-center mb-4">
                        <Zap className="h-6 w-6 text-yellow-600" fill="currentColor" />
                    </div>
                    <DialogTitle className="text-center text-xl">AI Credits Exhausted</DialogTitle>
                    <DialogDescription className="text-center pt-2">
                        You've reached your AI usage limit for the current billing period.
                        Top up your credits to continue using the AI Agent Manager.
                    </DialogDescription>
                </DialogHeader>

                <div className="grid gap-4 py-4">
                    <div className="flex flex-col gap-3">
                        <div className="p-3 border rounded-lg flex items-center gap-3 bg-primary/5">
                            <CreditCard className="h-5 w-5 text-primary" />
                            <div className="text-sm">
                                <p className="font-bold">Managed Credit Plan</p>
                                <p className="text-muted-foreground">$0.05 per AI interaction</p>
                            </div>
                        </div>
                        <div className="p-3 border rounded-lg flex items-center gap-3">
                            <ShieldCheck className="h-5 w-5 text-green-600" />
                            <div className="text-sm">
                                <p className="font-bold">Unlimited Plan (BYOK)</p>
                                <p className="text-muted-foreground">Switch to your own API key</p>
                            </div>
                        </div>
                    </div>
                </div>

                <DialogFooter className="sm:justify-center gap-2">
                    <Button variant="outline" onClick={onClose} className="flex-1">
                        Maybe Later
                    </Button>
                    <Button onClick={() => window.location.href = "/dashboard/settings"} className="flex-1">
                        Get More Credits
                    </Button>
                </DialogFooter>
            </DialogContent>
        </Dialog>
    )
}
