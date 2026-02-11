"use client";

import { useEffect, useState } from "react";
import { useRouter } from "next/navigation";
import { SalesChatWidget } from "@/components/quote/sales-chat-widget";
import { QuoteWizard } from "@/components/quotes/quote-wizard";
import { Card, CardHeader, CardTitle, CardDescription, CardContent } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { FileText, Sparkles, ArrowLeft, Loader2 } from "lucide-react";
import { clientApi } from "@/lib/client-api";
import { useToast } from "@/components/ui/use-toast";

export default function PortalCreateQuotePage() {
    const router = useRouter();
    const { toast } = useToast();
    const [mode, setMode] = useState<'select' | 'chat' | 'manual'>('select');
    const [clientId, setClientId] = useState<string | null>(null);
    const [clientLoading, setClientLoading] = useState(true);

    useEffect(() => {
        let isMounted = true;
        const loadClient = async () => {
            try {
                const client = await clientApi.getMyClient();
                if (isMounted) {
                    setClientId(client.id);
                }
            } catch (error: any) {
                console.error("Failed to load client for quote creation:", error);
                toast({
                    title: "Unable to load profile",
                    description: "We could not confirm your client profile. Refresh the page and try again.",
                    variant: "destructive"
                });
            } finally {
                if (isMounted) {
                    setClientLoading(false);
                }
            }
        };
        loadClient();
        return () => {
            isMounted = false;
        };
    }, [toast]);

    if (mode === 'select') {
        return (
            <div className="flex-1 p-4 md:p-8 pt-6 h-full flex flex-col items-center justify-center min-h-[600px]">
                <div className="text-center mb-10 space-y-2">
                    <h1 className="text-3xl font-bold tracking-tight">Get a Quote</h1>
                    <p className="text-muted-foreground text-lg">How would you like to create your quote?</p>
                </div>

                <div className="grid grid-cols-1 md:grid-cols-2 gap-8 w-full max-w-4xl">
                    {/* AI Option */}
                    <Card
                        className="group relative overflow-hidden border-2 hover:border-violet-500 transition-all cursor-pointer hover:shadow-xl bg-gradient-to-br from-white to-violet-50/20"
                        onClick={() => setMode('chat')}
                    >
                        <div className="absolute top-0 right-0 p-3">
                            <span className="px-2 py-1 bg-violet-100 text-violet-700 text-xs font-bold rounded-full uppercase tracking-wider">Recommended</span>
                        </div>
                        <CardHeader className="space-y-4">
                            <div className="h-14 w-14 rounded-2xl bg-violet-100 flex items-center justify-center group-hover:scale-110 transition-transform duration-300">
                                <Sparkles className="h-7 w-7 text-violet-600" />
                            </div>
                            <div>
                                <CardTitle className="text-2xl">Ask AI Assistant</CardTitle>
                                <CardDescription className="text-base mt-2">
                                    Chat with our intelligent agent. It will help you find the best coverage in seconds.
                                </CardDescription>
                            </div>
                        </CardHeader>
                        <CardContent>
                            <Button className="w-full bg-violet-600 hover:bg-violet-700">Start Chat</Button>
                        </CardContent>
                    </Card>

                    {/* Manual Option */}
                    <Card
                        className="group border-2 hover:border-slate-400 transition-all cursor-pointer hover:shadow-lg"
                        onClick={() => setMode('manual')}
                    >
                        <CardHeader className="space-y-4">
                            <div className="h-14 w-14 rounded-2xl bg-slate-100 flex items-center justify-center group-hover:scale-110 transition-transform duration-300">
                                <FileText className="h-7 w-7 text-slate-600" />
                            </div>
                            <div>
                                <CardTitle className="text-2xl">Manual Form</CardTitle>
                                <CardDescription className="text-base mt-2">
                                    Fill out the form yourself. Control every detail of your policy.
                                </CardDescription>
                            </div>
                        </CardHeader>
                        <CardContent>
                            <Button variant="outline" className="w-full">Open Form</Button>
                        </CardContent>
                    </Card>
                </div>
            </div>
        );
    }

    if (mode === 'chat') {
        return (
            <div className="flex-1 space-y-4 p-4 md:p-8 pt-6">
                <div className="flex items-center mb-6">
                    <Button variant="ghost" className="gap-2 pl-0 hover:bg-transparent hover:text-primary" onClick={() => setMode('select')}>
                        <ArrowLeft className="h-4 w-4" />
                        Back to Selection
                    </Button>
                </div>

                <div className="max-w-4xl mx-auto">
                    <SalesChatWidget />
                </div>
            </div>
        );
    }

    return (
        <div className="flex-1 p-4 md:p-8 pt-6 space-y-6">
            <div className="flex items-center mb-4">
                <Button variant="ghost" className="gap-2 pl-0 hover:bg-transparent hover:text-primary" onClick={() => setMode('select')}>
                    <ArrowLeft className="h-4 w-4" />
                    Back to Selection
                </Button>
            </div>

            {clientLoading ? (
                <div className="flex items-center justify-center py-20">
                    <Loader2 className="h-10 w-10 animate-spin text-[#00539F]" />
                </div>
            ) : clientId ? (
                <QuoteWizard
                    initialClientId={clientId}
                    onQuoteCreated={() => {
                        toast({ title: "Quote Created", description: "We redirected you to the portal dashboard." });
                        router.push('/portal');
                    }}
                    onExit={() => setMode('select')}
                />
            ) : (
                <div className="p-8 rounded-[30px] border border-dashed border-gray-200 bg-gray-50 text-center text-gray-500 font-bold uppercase tracking-widest">
                    Unable to load your client profile. Please refresh the page and try again.
                </div>
            )}
        </div>
    );
}
