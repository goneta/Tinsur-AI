import { useState } from 'react';
import { Dialog, DialogContent, DialogHeader, DialogTitle, DialogDescription, DialogFooter } from '@/components/ui/dialog';
import { Button } from '@/components/ui/button';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select';
import { Label } from '@/components/ui/label';
import { Alert, AlertDescription, AlertTitle } from '@/components/ui/alert';
import { Separator } from '@/components/ui/separator';
import { CheckCircle2, AlertTriangle, Calculator, FileText } from 'lucide-react';
import { formatCurrency } from '@/lib/utils';
import { Policy } from '@/types/policy';

interface CancellationWorkflowProps {
    open: boolean;
    onOpenChange: (open: boolean) => void;
    policy: Policy;
    onSuccess: () => void;
}

const CANCELLATION_REASONS = [
    { value: 'sold_vehicle', label: 'Vehicle Sold / Transfer of Ownership', notice: 'Immediate', fee: 0 },
    { value: 'found_cheaper', label: 'Found Cheaper Alternative', notice: '30 Days', fee: 50 },
    { value: 'service_dissatisfaction', label: 'Service Dissatisfaction', notice: '30 Days', fee: 0 },
    { value: 'no_longer_needed', label: 'Coverage No Longer Needed', notice: '30 Days', fee: 25 },
    { value: 'moved_abroad', label: 'Moved Abroad', notice: '14 Days', fee: 0 },
    { value: 'cooling_off', label: 'Cooling-off Period (First 14 Days)', notice: 'Immediate', fee: 0 },
];

export function CancellationWorkflow({ open, onOpenChange, policy, onSuccess }: CancellationWorkflowProps) {
    const [step, setStep] = useState<'reason' | 'refund' | 'confirm' | 'success'>('reason');
    const [reason, setReason] = useState<string>('');
    const [isSubmitting, setIsSubmitting] = useState(false);

    const selectedReason = CANCELLATION_REASONS.find(r => r.value === reason);

    // Mock Refund Calculation logic based on policy details
    const calculateRefund = () => {
        if (!policy) return 0;
        // Simple mock: 40% of premium for demo purposes if active
        // In real app, this would be a backend calculation
        return policy.premium_amount * 0.4;
    };

    const estimatedRefund = calculateRefund();
    const cancellationFee = selectedReason?.fee || 0;
    const finalRefund = Math.max(0, estimatedRefund - cancellationFee);

    const handleNext = () => {
        if (step === 'reason') setStep('refund');
        else if (step === 'refund') setStep('confirm');
    };

    const handleBack = () => {
        if (step === 'refund') setStep('reason');
        else if (step === 'confirm') setStep('refund');
    };

    const handleConfirm = async () => {
        setIsSubmitting(true);
        // Simulate API call
        await new Promise(resolve => setTimeout(resolve, 1500));

        // Call parent success handler (which would ideally reload policy to show 'canceled')
        // Here we just transition to success state locally first
        setIsSubmitting(false);
        setStep('success');
    };

    const handleClose = () => {
        onOpenChange(false);
        // Reset state after close animation
        setTimeout(() => {
            setStep('reason');
            setReason('');
        }, 300);
        if (step === 'success') {
            onSuccess();
        }
    };

    return (
        <Dialog open={open} onOpenChange={handleClose}>
            <DialogContent className="max-w-md">
                <DialogHeader>
                    <DialogTitle>Cancel Policy {policy?.policy_number}</DialogTitle>
                    <DialogDescription>
                        Follow the steps below to proceed with the cancellation of your insurance policy.
                    </DialogDescription>
                </DialogHeader>

                {step === 'reason' && (
                    <div className="space-y-4 py-4 animate-in fade-in slide-in-from-right-4 duration-300">
                        <div className="space-y-2">
                            <Label htmlFor="reason">Reason for Cancellation</Label>
                            <Select value={reason} onValueChange={setReason}>
                                <SelectTrigger>
                                    <SelectValue placeholder="Select a reason..." />
                                </SelectTrigger>
                                <SelectContent>
                                    {CANCELLATION_REASONS.map((r) => (
                                        <SelectItem key={r.value} value={r.value}>
                                            {r.label}
                                        </SelectItem>
                                    ))}
                                </SelectContent>
                            </Select>
                        </div>

                        {selectedReason && (
                            <Alert className="bg-blue-50 border-blue-100">
                                <AlertTriangle className="h-4 w-4 text-blue-600" />
                                <AlertTitle className="text-blue-800">Notice Period: {selectedReason.notice}</AlertTitle>
                                <AlertDescription className="text-blue-700 text-xs">
                                    Standard administrative fees may apply based on the selected reason as per the Terms & Conditions.
                                </AlertDescription>
                            </Alert>
                        )}
                    </div>
                )}

                {step === 'refund' && (
                    <div className="space-y-6 py-4 animate-in fade-in slide-in-from-right-4 duration-300">
                        <div className="bg-slate-50 p-4 rounded-lg border border-slate-100 space-y-3">
                            <h4 className="font-semibold text-sm flex items-center gap-2">
                                <Calculator className="h-4 w-4 text-slate-500" />
                                Estimated Refund Calculation
                            </h4>
                            <Separator />
                            <div className="space-y-2 text-sm">
                                <div className="flex justify-between">
                                    <span className="text-slate-600">Pro-rata Unused Premium</span>
                                    <span className="font-medium text-green-600">+{formatCurrency(estimatedRefund)}</span>
                                </div>
                                <div className="flex justify-between">
                                    <span className="text-slate-600">Administration Fee</span>
                                    <span className="font-medium text-red-600">-{formatCurrency(cancellationFee)}</span>
                                </div>
                                <Separator className="my-2" />
                                <div className="flex justify-between items-center pt-1">
                                    <span className="font-bold text-slate-900">Total Refund Amount</span>
                                    <span className="font-bold text-xl text-slate-900">{formatCurrency(finalRefund)}</span>
                                </div>
                            </div>
                        </div>
                        <p className="text-xs text-slate-500 italic text-center">
                            * This is an estimate. Final amount will be confirmed by our underwriting team within 48 hours.
                        </p>
                    </div>
                )}

                {step === 'confirm' && (
                    <div className="space-y-4 py-4 animate-in fade-in slide-in-from-right-4 duration-300">
                        <Alert variant="destructive">
                            <AlertTriangle className="h-4 w-4" />
                            <AlertTitle>Warning: Irreversible Action</AlertTitle>
                            <AlertDescription>
                                Once confirmed, your coverage for <strong>{policy?.policy_number}</strong> will stop effective immediately (or after the notice period). You will no longer be protected.
                            </AlertDescription>
                        </Alert>

                        <div className="rounded-md border p-4 space-y-2 text-sm">
                            <div className="grid grid-cols-2 gap-2">
                                <span className="text-slate-500">Policy:</span>
                                <span className="font-medium">{policy?.policy_number}</span>

                                <span className="text-slate-500">Reason:</span>
                                <span className="font-medium capitalize">{selectedReason?.label}</span>

                                <span className="text-slate-500">Est. Refund:</span>
                                <span className="font-medium">{formatCurrency(finalRefund)}</span>
                            </div>
                        </div>
                    </div>
                )}

                {step === 'success' && (
                    <div className="py-8 flex flex-col items-center text-center space-y-4 animate-in zoom-in duration-300">
                        <div className="h-16 w-16 bg-green-100 text-green-600 rounded-full flex items-center justify-center mb-2">
                            <CheckCircle2 className="h-8 w-8" />
                        </div>
                        <h3 className="text-2xl font-bold text-slate-900">Cancellation Submitted</h3>
                        <p className="text-slate-500 max-w-[280px]">
                            Your request to cancel policy <strong>{policy?.policy_number}</strong> has been received. You will receive a confirmation email shortly.
                        </p>
                        <div className="flex gap-2 mt-4">
                            <Button variant="outline" className="gap-2">
                                <FileText className="h-4 w-4" /> Download Receipt
                            </Button>
                        </div>
                    </div>
                )}

                <DialogFooter className="flex-col sm:flex-row gap-2">
                    {step === 'success' ? (
                        <Button onClick={handleClose} className="w-full sm:w-auto bg-slate-900 text-white hover:bg-slate-800">
                            Close
                        </Button>
                    ) : (
                        <>
                            {step !== 'reason' && (
                                <Button variant="outline" onClick={handleBack} disabled={isSubmitting}>
                                    Back
                                </Button>
                            )}
                            <div className="flex-1" />
                            {step === 'reason' && (
                                <Button onClick={handleNext} disabled={!reason}>
                                    Next: Review Refund
                                </Button>
                            )}
                            {step === 'refund' && (
                                <Button onClick={handleNext}>
                                    Next: Final Confirm
                                </Button>
                            )}
                            {step === 'confirm' && (
                                <Button onClick={handleConfirm} disabled={isSubmitting} variant="destructive">
                                    {isSubmitting ? 'Processing...' : 'Confirm Cancellation'}
                                </Button>
                            )}
                        </>
                    )}
                </DialogFooter>
            </DialogContent>
        </Dialog>
    );
}
