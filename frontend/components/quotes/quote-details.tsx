"use client";

import { useEffect, useState } from "react";
import { useRouter } from "next/navigation";
import { QuoteAPI } from "@/lib/api/quotes";
import { Quote, PolicyType } from "@/types/quote";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardHeader, CardTitle, CardFooter } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { useToast } from "@/components/ui/use-toast";
import { formatCurrency, formatDate } from "@/lib/utils";
import { ArrowLeft, Check, Send, FileText, Loader2 } from "lucide-react";
import {
    Dialog,
    DialogContent,
    DialogDescription,
    DialogFooter,
    DialogHeader,
    DialogTitle,
    DialogTrigger,
} from "@/components/ui/dialog";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select";

export function QuoteDetails({ id }: { id: string }) {
    const router = useRouter();
    const { toast } = useToast();
    const [quote, setQuote] = useState<Quote | null>(null);
    const [loading, setLoading] = useState(true);
    const [policyType, setPolicyType] = useState<string>("");
    const [converting, setConverting] = useState(false);
    const [startDate, setStartDate] = useState("");

    useEffect(() => {
        async function fetchQuote() {
            try {
                const data = await QuoteAPI.get(id);
                setQuote(data);

                // Fetch types to display name
                const types = await QuoteAPI.listPolicyTypes();
                const type = types.find(t => t.id === data.policy_type_id);
                if (type) setPolicyType(type.name);

            } catch (e: any) {
                console.error("Failed to load quote:", e);
                toast({
                    title: "Error",
                    description: `Failed to load quote: ${e.message || "Unknown error"}`,
                    variant: "destructive"
                });
            } finally {
                setLoading(false);
            }
        }
        fetchQuote();
    }, [id]);

    const onConvert = async () => {
        if (!startDate) {
            toast({ title: "Error", description: "Start Date is required", variant: "destructive" });
            return;
        }
        setConverting(true);
        try {
            const result = await QuoteAPI.convertToPolicy(id, {
                start_date: startDate,
                payment_method: 'cash', // Default for now, could be form input
            });
            toast({ title: "Success", description: "Policy created: " + result.policy_number });
            // Redirect to policy list or detail (if implemented)
            router.push("/dashboard/policies");
        } catch (e) {
            toast({ title: "Error", description: "Failed to convert quote", variant: "destructive" });
        } finally {
            setConverting(false);
        }
    };

    const onSend = async () => {
        try {
            await QuoteAPI.send(id);
            toast({ title: "Success", description: "Quote sent to client" });
            // Refresh
            const updated = await QuoteAPI.get(id);
            setQuote(updated);
        } catch (e) {
            toast({ title: "Error", description: "Failed to send quote", variant: "destructive" });
        }
    };

    if (loading) return <Loader2 className="h-8 w-8 animate-spin mx-auto mt-10" />;
    if (!quote) return <div>Quote not found</div>;

    return (
        <div className="space-y-6">
            <div className="flex items-center justify-between">
                <Button variant="ghost" onClick={() => router.back()}>
                    <ArrowLeft className="mr-2 h-4 w-4" /> Back to List
                </Button>
                <div className="flex gap-2">
                    {quote.status === 'draft' && (
                        <Button onClick={onSend}>
                            <Send className="mr-2 h-4 w-4" /> Send to Client
                        </Button>
                    )}
                    {(['sent', 'draft_from_client', 'accepted', 'approved'].includes(quote.status)) && (
                        <Dialog>
                            <DialogTrigger asChild>
                                <Button variant="default" className="w-full sm:w-auto">
                                    <Check className="mr-2 h-4 w-4" /> Select Quote
                                </Button>
                            </DialogTrigger>
                            <DialogContent>
                                <DialogHeader>
                                    <DialogTitle>Convert to Policy</DialogTitle>
                                    <DialogDescription>
                                        Create a new active policy from this quote.
                                    </DialogDescription>
                                </DialogHeader>
                                <div className="grid gap-4 py-4">
                                    <div className="grid grid-cols-4 items-center gap-4">
                                        <Label htmlFor="start_date" className="text-right">Start Date</Label>
                                        <Input
                                            id="start_date"
                                            type="date"
                                            className="col-span-3"
                                            value={startDate}
                                            onChange={(e) => setStartDate(e.target.value)}
                                        />
                                    </div>
                                </div>
                                <DialogFooter>
                                    <Button disabled={converting} onClick={onConvert}>
                                        {converting && <Loader2 className="mr-2 h-4 w-4 animate-spin" />}
                                        Confirm Conversion
                                    </Button>
                                </DialogFooter>
                            </DialogContent>
                        </Dialog>
                    )}
                </div>
            </div>

            <div className="grid gap-6 md:grid-cols-2">
                <Card>
                    <CardHeader>
                        <CardTitle>Quote Details</CardTitle>
                    </CardHeader>
                    <CardContent className="space-y-4">
                        <div className="grid grid-cols-2 gap-2 text-sm">
                            <span className="text-muted-foreground">Quote Number:</span>
                            <span className="font-medium">{quote.quote_number}</span>

                            <span className="text-muted-foreground">Status:</span>
                            <Badge>{quote.status.toUpperCase()}</Badge>

                            <span className="text-muted-foreground">Policy Type:</span>
                            <span>{policyType}</span>

                            <span className="text-muted-foreground">Values Valid Until:</span>
                            <span>{formatDate(quote.valid_until)}</span>
                        </div>
                    </CardContent>
                </Card>

                <Card className="border-2 border-primary/20 shadow-lg">
                    <CardHeader className="bg-slate-50 dark:bg-slate-900 border-b">
                        <div className="flex justify-between items-center">
                            <CardTitle>Premium Breakdown</CardTitle>
                            <div className="flex items-center space-x-1 bg-yellow-100 text-yellow-800 px-2 py-1 rounded text-xs font-bold border border-yellow-200">
                                <span>★★★★★</span>
                                <span>5 Star Defaqto</span>
                            </div>
                        </div>
                    </CardHeader>
                    <CardContent className="space-y-4 pt-6">
                        <div className="flex justify-between items-center text-sm">
                            <span className="text-muted-foreground">Base Policy Price</span>
                            <span className="font-medium">{formatCurrency(quote.premium_amount || quote.final_premium)}</span>
                        </div>

                        {/* Excess Display */}
                        {(quote.excess || 0) > 0 && (
                            <div className="flex justify-between items-center text-sm">
                                <span className="text-muted-foreground">Excess (Deductible)</span>
                                <span>{formatCurrency(quote.excess!)}</span>
                            </div>
                        )}

                        {/* Included Services Display */}
                        {quote.included_services && quote.included_services.length > 0 && (
                            <div className="pt-2 pb-2">
                                <span className="text-xs font-semibold text-muted-foreground uppercase tracking-wider">Included Services</span>
                                <div className="flex flex-wrap gap-2 mt-2">
                                    {quote.included_services.map((service: any, index: number) => (
                                        <Badge key={index} variant="secondary" className="text-xs">
                                            {typeof service === 'object' ? service.name_en || service.name : service}
                                        </Badge>
                                    ))}
                                </div>
                            </div>
                        )}

                        {(quote.arrangement_fee || 0) > 0 && (
                            <div className="flex justify-between items-center text-sm">
                                <span className="text-muted-foreground">Arrangement Fee</span>
                                <span>{formatCurrency(quote.arrangement_fee!)}</span>
                            </div>
                        )}

                        {(quote.extra_fee || 0) > 0 && (
                            <div className="flex justify-between items-center text-sm">
                                <span className="text-muted-foreground">Extra Fee</span>
                                <span className="text-muted-foreground">{formatCurrency(quote.extra_fee!)}</span>
                            </div>
                        )}

                        {/* Admin Fee */}
                        {(quote.admin_fee || 0) > 0 && (
                            <div className="flex justify-between items-center text-sm">
                                <span className="text-muted-foreground">Company Admin Fee</span>
                                <span>{formatCurrency(quote.admin_fee!)}</span>
                            </div>
                        )}

                        <div className="border-t my-2 border-dashed"></div>

                        {/* Subtotal implied or explicit? User asked for fees "before the total amount". */}

                        {/* Government Tax */}
                        {(quote.tax_amount || 0) > 0 && (
                            <div className="flex justify-between items-center text-sm">
                                <span className="text-muted-foreground">Government Tax (TVA) {parseFloat(quote.tax_percent as any) > 0 ? `(${quote.tax_percent}%)` : ''}</span>
                                <span>{formatCurrency(quote.tax_amount!)}</span>
                            </div>
                        )}

                        <div className="border-t my-2"></div>

                        <div className="flex justify-between items-center text-sm font-semibold">
                            <span>Total Financed Amount</span>
                            <span>{formatCurrency(quote.total_financed_amount || quote.final_premium)}</span>
                        </div>

                        {(quote.apr_percent || 0) > 0 && (
                            <div className="flex justify-between items-center text-xs text-muted-foreground mt-1">
                                <span>APR (Gov. Tax Rate)</span>
                                <span>{quote.apr_percent}%</span>
                            </div>
                        )}

                        <div className="bg-primary/5 p-4 rounded-lg mt-4 space-y-2">
                            <div className="flex justify-between items-center">
                                <span className="text-sm font-medium">Monthly Installment</span>
                                <span className="text-lg font-bold text-primary">
                                    {formatCurrency(quote.monthly_installment || 0)}
                                </span>
                            </div>
                            <div className="flex justify-between items-center text-xs text-muted-foreground">
                                <span>Over {quote.duration_months} months</span>
                            </div>
                        </div>

                        <div className="flex justify-between items-center text-sm pt-2">
                            <span className="font-medium">Total Installment Price</span>
                            <span className="font-bold">{formatCurrency(quote.total_installment_price || 0)}</span>
                        </div>
                    </CardContent>
                </Card>

                {quote.details && Object.keys(quote.details).length > 0 && (
                    <Card className="md:col-span-2">
                        <CardHeader>
                            <CardTitle>Risk Factors</CardTitle>
                        </CardHeader>
                        <CardContent>
                            <div className="grid grid-cols-2 md:grid-cols-3 gap-4">
                                {Object.entries(quote.details).map(([key, value]) => (
                                    <div key={key} className="space-y-1">
                                        <span className="text-xs text-muted-foreground uppercase">{key.replace(/_/g, " ")}</span>
                                        <p className="font-medium text-sm">{String(value)}</p>
                                    </div>
                                ))}
                            </div>
                        </CardContent>
                    </Card>
                )}
            </div>
        </div>
    );
}
