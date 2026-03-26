"use client"

import { Bot, CreditCard, X } from "lucide-react"
import { useRouter } from "next/navigation"

import {
    Dialog,
    DialogContent,
    DialogDescription,
    DialogFooter,
    DialogHeader,
    DialogTitle,
} from "@/components/ui/dialog"
import { Button } from "@/components/ui/button"

interface CreditLimitModalProps {
    isOpen: boolean
    onClose: () => void
}

export function CreditLimitModal({ isOpen, onClose }: CreditLimitModalProps) {
    const router = useRouter()

    const handleUpgrade = () => {
        onClose()
        router.push("/dashboard/settings?tab=ai")
    }

    return (
        <Dialog open={isOpen} onOpenChange={(open) => !open && onClose()}>
            <DialogContent className="sm:max-w-[425px]">
                <DialogHeader>
                    <div className="mx-auto w-12 h-12 bg-amber-100 dark:bg-amber-900/30 rounded-full flex items-center justify-center mb-4">
                        <CreditCard className="h-6 w-6 text-amber-600 dark:text-amber-400" />
                    </div>
                    <DialogTitle className="text-center text-xl">Insufficient AI Credits</DialogTitle>
                    <DialogDescription className="text-center pt-2">
                        Your company has exhausted its allocated AI interaction credits or your current plan does not include AI access.
                    </DialogDescription>
                </DialogHeader>
                <div className="py-6 flex flex-col items-center gap-4">
                    <div className="p-4 bg-muted rounded-lg text-sm flex items-start gap-3">
                        <Bot className="h-5 w-5 text-primary shrink-0 mt-0.5" />
                        <p>
                            To continue enjoying automated claims processing, smart quotes, and agent assistance, please top up your balance or upgrade your plan.
                        </p>
                    </div>
                </div>
                <DialogFooter className="flex flex-col sm:flex-row gap-2">
                    <Button variant="outline" onClick={onClose} className="flex-1">
                        Maybe Later
                    </Button>
                    <Button onClick={handleUpgrade} className="flex-1">
                        Go to Settings
                    </Button>
                </DialogFooter>
            </DialogContent>
        </Dialog>
    )
}
