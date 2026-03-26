'use client';

import { useState, useRef, useEffect } from 'react';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { ScrollArea } from '@/components/ui/scroll-area';
import { Card, CardContent } from '@/components/ui/card';
import { Bot, Send, User, Loader2, Sparkles, RefreshCcw } from 'lucide-react';
import { AiAPI, ChatMessage } from '@/lib/ai-api';
import { quoteApi } from '@/lib/quote-api';
import { useLanguage } from '@/contexts/language-context';
import { Badge } from '@/components/ui/badge';
import ReactMarkdown from 'react-markdown';
import { useRouter } from 'next/navigation';
import { useAuth } from '@/lib/auth';

export function SalesChatWidget() {
    const { t } = useLanguage();
    const router = useRouter();
    const [messages, setMessages] = useState<ChatMessage[]>([]);
    const [inputValue, setInputValue] = useState("");
    const [isLoading, setIsLoading] = useState(false);
    const [lastPrompt, setLastPrompt] = useState<string>('');
    const [lastError, setLastError] = useState<string>('');
    const [clientIdInput, setClientIdInput] = useState('');
    const [policyTypeIdInput, setPolicyTypeIdInput] = useState('');
    const [autoQuoteStatus, setAutoQuoteStatus] = useState('');
    const scrollRef = useRef<HTMLDivElement>(null);

    // Initial Start of Quote Conversation
    const { user } = useAuth();
    const isStaff = user?.role && ['super_admin', 'company_admin', 'manager', 'agent'].includes(user.role);

    useEffect(() => {
        if (messages.length === 0) {
            setMessages([
                {
                    role: 'assistant',
                    content: isStaff
                        ? "Hello! I'm your Tinsur.AI Sales Agent. I'll help you create a quote for a client. I can show you your recent clients or you can search for a specific one by name, email, or phone."
                        : "Hello! I'm your Tinsur.AI Sales Agent. I can help you find the best insurance policy in seconds. Let's get started!"
                }
            ]);

            // For staff, explicitly ask to list clients. For clients, use generic start.
            const initialPrompt = isStaff
                ? "I want to create a quote. List my recent clients."
                : "I want to get an insurance quote.";

            handleSendMessage(initialPrompt, true);
        }
    }, [isStaff]);

    // Auto-scroll
    useEffect(() => {
        if (scrollRef.current) {
            scrollRef.current.scrollIntoView({ behavior: 'smooth' });
        }
    }, [messages]);

    
    const createAutoQuote = async () => {
        setAutoQuoteStatus('');
        if (!clientIdInput || !policyTypeIdInput) {
            setAutoQuoteStatus('Please provide Client ID and Policy Type ID.');
            return;
        }
        try {
            const payload = {
                client_id: clientIdInput,
                policy_type_id: policyTypeIdInput,
                coverage_amount: 100000,
                premium_frequency: 'monthly' as const,
                duration_months: 12,
                discount_percent: 0,
                details: { source: 'AT-agent-auto-create', actor_role: user?.role || 'client' }
            };
            const created: any = await quoteApi.createQuote(payload as any);
            setAutoQuoteStatus(`? Quote created: ${created?.quote_number || created?.id || 'success'}`);
        } catch (e: any) {
            setAutoQuoteStatus(`? Auto-create failed: ${e?.response?.data?.detail || e?.message || 'unknown error'}`);
        }
    };

const handleSendMessage = async (textOverride?: string, isHidden: boolean = false) => {
        const content = textOverride || inputValue.trim();
        if (!content || isLoading) return;

        if (!textOverride) setInputValue("");
        setLastPrompt(content);
        setLastError('');

        // Add user message to UI (unless hidden)
        if (!isHidden) {
            setMessages(prev => [...prev, { role: 'user', content }]);
        }

        setIsLoading(true);

        try {
            // Pass full conversation history
            const response = await AiAPI.chat(content, messages);

            setMessages(prev => [...prev, {
                role: 'assistant',
                content: response.response
            }]);

        } catch (error) {
            console.error("Chat error:", error);
            const fallback = "I'm having trouble connecting to the quote engine. Please try again or use the manual form.";
            setLastError(fallback);
            setMessages(prev => [...prev, {
                role: 'assistant',
                content: `${fallback}\n\nClick Retry to resend your last message.`
            }]);
        } finally {
            setIsLoading(false);
        }
    };

    return (
        <Card className="flex flex-col h-[600px] border-slate-200 shadow-xl overflow-hidden bg-white">
            <div className="p-4 border-b bg-gradient-to-r from-violet-600 to-indigo-600 flex items-center justify-between">
                <div className="flex items-center gap-3">
                    <div className="h-10 w-10 rounded-full bg-white/20 backdrop-blur-sm flex items-center justify-center text-white shadow-lg">
                        <Sparkles className="h-5 w-5" />
                    </div>
                    <div>
                        <h3 className="font-bold text-white leading-tight">Sales Assistant</h3>
                        <div className="flex items-center gap-1.5">
                            <span className="h-2 w-2 rounded-full bg-green-400 animate-pulse" />
                            <span className="text-[11px] text-violet-100 font-medium uppercase tracking-wider">Smart Quote Active</span>
                        </div>
                    </div>
                </div>
                <Button
                    variant="ghost"
                    size="sm"
                    className="text-white hover:bg-white/10 h-8 px-2"
                    onClick={() => router.refresh()} // Or specific reset logic
                >
                    <RefreshCcw className="h-4 w-4 mr-1" />
                    Reset
                </Button>
            </div>

            <ScrollArea className="flex-1 p-4 bg-slate-50/50">
                <div className="space-y-6">
                    {messages.map((msg, idx) => (
                        <div key={idx} className={`flex gap-3 ${msg.role === 'user' ? 'flex-row-reverse' : ''}`}>
                            <div className={`h-8 w-8 rounded-lg flex items-center justify-center shrink-0 border shadow-sm ${msg.role === 'assistant' ? 'bg-white text-violet-600' : 'bg-violet-600 text-white'
                                }`}>
                                {msg.role === 'assistant' ? <Bot className="h-5 w-5" /> : <User className="h-5 w-5" />}
                            </div>
                            <div className={`max-w-[85%] p-4 rounded-2xl text-sm leading-relaxed shadow-sm ${msg.role === 'assistant'
                                ? 'bg-white border text-slate-700 rounded-tl-none'
                                : 'bg-violet-600 text-white rounded-tr-none'
                                }`}>
                                <div className="prose prose-sm max-w-none prose-slate prose-p:my-1 prose-headings:text-slate-900 prose-headings:font-bold prose-strong:text-slate-900">
                                    <ReactMarkdown
                                        components={{
                                            a: ({ node, ...props }) => {
                                                const isAction = props.href?.startsWith('select-client:') || props.href?.startsWith('select-policy:');
                                                if (isAction) {
                                                    return (
                                                        <button
                                                            onClick={(e) => {
                                                                e.preventDefault();
                                                                const parts = props.href?.split(':') || [];
                                                                if (parts[0] === 'select-client') {
                                                                    handleSendMessage(`I select ${parts[2]} (ID: ${parts[1]})`);
                                                                } else if (parts[0] === 'select-policy') {
                                                                    handleSendMessage(`I select the policy: ${parts[2]} (ID: ${parts[1]})`);
                                                                }
                                                            }}
                                                            className="inline-flex items-center px-3 py-1 my-0.5 rounded-full bg-violet-100 text-violet-700 hover:bg-violet-200 border border-violet-200 transition-colors font-semibold text-[12px] no-underline"
                                                        >
                                                            {props.children}
                                                        </button>
                                                    );
                                                }
                                                return <a {...props} className="text-violet-600 hover:underline" />;
                                            }
                                        }}
                                    >
                                        {msg.content}
                                    </ReactMarkdown>
                                </div>
                            </div>
                        </div>
                    ))}
                    {isLoading && (
                        <div className="flex gap-3">
                            <div className="h-8 w-8 rounded-lg bg-white border flex items-center justify-center shadow-sm">
                                <Bot className="h-5 w-5 text-violet-600" />
                            </div>
                            <div className="bg-white border p-3 rounded-2xl rounded-tl-none shadow-sm flex items-center gap-2">
                                <Loader2 className="h-4 w-4 animate-spin text-violet-500" />
                                <span className="text-xs text-slate-500 font-medium">Calculating best rates...</span>
                            </div>
                        </div>
                    )}
                    <div ref={scrollRef} />
                </div>
            </ScrollArea>

            <div className="p-4 border-t bg-white space-y-3">
                <div className="rounded-xl border border-indigo-200 bg-indigo-50/60 p-3">
                    <div className="text-xs font-semibold text-indigo-700 mb-2">AT Agent ? Auto-create quote (Client/Admin)</div>
                    <div className="grid grid-cols-1 md:grid-cols-3 gap-2">
                        <Input
                            placeholder="Client ID"
                            value={clientIdInput}
                            onChange={(e) => setClientIdInput(e.target.value)}
                        />
                        <Input
                            placeholder="Policy Type ID"
                            value={policyTypeIdInput}
                            onChange={(e) => setPolicyTypeIdInput(e.target.value)}
                        />
                        <Button onClick={createAutoQuote} className="bg-indigo-600 hover:bg-indigo-700">AT Auto-create Quote</Button>
                    </div>
                    {autoQuoteStatus && <div className="mt-2 text-xs text-slate-700">{autoQuoteStatus}</div>}
                </div>


                <div className="flex gap-2">
                    <div className="relative flex-1">
                        <Input
                            placeholder="e.g. I drive a 2020 Toyota Corolla, 0 accidents..."
                            className="h-12 px-4 rounded-xl border-slate-200 bg-slate-50 focus-visible:bg-white focus-visible:ring-violet-500"
                            value={inputValue}
                            onChange={(e) => setInputValue(e.target.value)}
                            onKeyDown={(e) => e.key === 'Enter' && handleSendMessage()}
                            disabled={isLoading}
                        />
                        <Button
                            size="icon"
                            className={`absolute right-1.5 top-1.5 h-9 w-9 rounded-lg transition-all ${inputValue.trim() ? 'bg-violet-600 hover:bg-violet-700' : 'bg-slate-200 text-white cursor-not-allowed'
                                }`}
                            onClick={() => handleSendMessage()}
                            disabled={isLoading || !inputValue.trim()}
                        >
                            <Send className="h-4 w-4" />
                        </Button>
                    </div>
                </div>
                {lastError && (
                    <div className="flex items-center justify-between text-[11px] text-red-500 bg-red-50 border border-red-200 rounded-lg px-3 py-2">
                        <span>{lastError}</span>
                        <Button
                            size="sm"
                            variant="outline"
                            className="h-7"
                            onClick={() => handleSendMessage(lastPrompt)}
                            disabled={isLoading || !lastPrompt}
                        >
                            Retry
                        </Button>
                    </div>
                )}

                <div className="flex justify-between items-center text-[10px] text-slate-400 font-medium">
                    <span>AI-powered estimates</span>
                    <span onClick={() => window.location.reload()} className="hover:text-violet-600 cursor-pointer">Switch to Manual Form</span>
                </div>
            </div>
        </Card>
    );
}


