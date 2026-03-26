'use client';

import { useState, useRef, useEffect } from 'react';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { ScrollArea } from '@/components/ui/scroll-area';
import { Card } from '@/components/ui/card';
import {
    Bot,
    Send,
    FileText,
    Plus,
    Image as ImageIcon,
    Lightbulb,
    Search,
    ShoppingBag,
    MoreHorizontal,
    Paperclip,
    BookOpen,
    Globe,
    PenTool,
    Mic,
    Headphones,
    X,
    User,
    Play
} from 'lucide-react';
import {
    DropdownMenu,
    DropdownMenuContent,
    DropdownMenuItem,
    DropdownMenuTrigger,
    DropdownMenuSeparator,
    DropdownMenuSub,
    DropdownMenuSubTrigger,
    DropdownMenuSubContent
} from '@/components/ui/dropdown-menu';
import { AiAPI, ChatMessage } from '@/lib/ai-api';
import { toast } from '@/components/ui/use-toast';
import ReactMarkdown from 'react-markdown';
import { PreviewState } from '@/types/ai-agent';
import { useChat } from '@/context/chat-context';
import { CreditLimitModal } from './credit-limit-modal';
import { subscriptionApi, SubscriptionStatus } from '@/lib/subscription-api';
import { Badge } from '@/components/ui/badge';
import { Coins } from 'lucide-react';
import { useLanguage } from '@/contexts/language-context';

interface LeftPanelProps {
    onPreviewChange: (state: PreviewState) => void;
    pendingAction?: { action: string, data: any } | null;
    onActionProcessed?: () => void;
}

export function LeftPanel({ onPreviewChange, pendingAction, onActionProcessed }: LeftPanelProps) {
    const { t } = useLanguage();
    const { messages, setMessages, setPreviewState } = useChat();
    const fileInputRef = useRef<HTMLInputElement>(null);
    const scrollRef = useRef<HTMLDivElement>(null);
    const [inputValue, setInputValue] = useState("");
    const [selectedFile, setSelectedFile] = useState<File | null>(null);
    const [isLoading, setIsLoading] = useState(false);
    const [activeInteraction, setActiveInteraction] = useState<any | null>(null);
    const [editingField, setEditingField] = useState<string | null>(null);
    const [isCreditModalOpen, setIsCreditModalOpen] = useState(false);
    const [subStatus, setSubStatus] = useState<SubscriptionStatus | null>(null);

    // Initial Welcome Message
    useEffect(() => {
        if (messages.length === 0) {
            setMessages([
                {
                    role: 'assistant',
                    content: `${t('ai_manager.welcome_title')}
            
${t('ai_manager.welcome_desc')}

* "${t('ai_manager.sample_quote')}"
* "${t('ai_manager.sample_analyze')}"
* "${t('ai_manager.sample_user')}"

${t('ai_manager.upload_hint')}`
                }
            ]);
        }
        loadSubscription();
    }, [messages.length, setMessages, t]);

    const loadSubscription = async () => {
        try {
            const data = await subscriptionApi.getStatus();
            setSubStatus(data);
        } catch (e) {
            console.error("Failed to load subscription status for badge:", e);
        }
    };

    // Auto-scroll to bottom
    useEffect(() => {
        if (scrollRef.current) {
            scrollRef.current.scrollIntoView({ behavior: 'smooth' });
        }
    }, [messages]);

    // Handle External Actions (Validate/Modify from Right Panel)
    useEffect(() => {
        if (pendingAction) {
            if (pendingAction.action === 'validate') {
                handleValidate(pendingAction.data);
            } else if (pendingAction.action === 'modify') {
                handleSendMessage(`Modify this ${pendingAction.data.type === 'quote' ? 'quote' : pendingAction.data.type || 'document'}`);
            } else if (pendingAction.action === 'convert_to_policy') {
                handleSendMessage(`Convert quote ${pendingAction.data.quote_number || pendingAction.data.quote_id} to policy`);
            }
            onActionProcessed?.();
        }
    }, [pendingAction]);

    const handleValidate = async (data: any) => {
        setIsLoading(true);
        try {
            const result = await AiAPI.validateEntity(data.type || 'quote', data);
            toast({
                title: "Validated & Saved",
                description: `The ${data.type || 'quote'} has been persisted to the database.`,
            });
            // Add a success message to chat
            setMessages(prev => [...prev, {
                role: 'assistant',
                content: `Successfully validated and saved ${data.type || 'quote'} #${data.quote_number || data.id || ''}.`
            }]);
        } catch (error) {
            toast({
                title: "Validation Failed",
                description: "There was an error saving the record.",
                variant: "destructive"
            });
        } finally {
            setIsLoading(false);
        }
    };

    const handleFileSelect = (e: React.ChangeEvent<HTMLInputElement>) => {
        if (e.target.files && e.target.files[0]) {
            setSelectedFile(e.target.files[0]);
        }
    };

    const handleTriggerUpload = () => {
        fileInputRef.current?.click();
    };

    // Helper to extract JSON from markdown
    const parsePreviewData = (text: string) => {
        // Look for ```json blocks
        const jsonBlockRegex = /```json\s*([\s\S]*?)\s*```/g;
        let match;

        while ((match = jsonBlockRegex.exec(text)) !== null) {
            try {
                const data = JSON.parse(match[1]);
                console.log("Found structured data:", data);

                if (data.interaction) {
                    setActiveInteraction(data.interaction);
                    if (data.interaction.type === 'progress') {
                        onPreviewChange({
                            type: data.interaction.data.type || 'quote_progress',
                            data: data.interaction.data
                        });
                        toast({
                            title: "Progress Updated",
                            description: `Step: ${data.interaction.data.current_step}`,
                        });
                    }
                    return; // Stop here if it's an interaction
                }

                if (data.type === 'quote' || data.type === 'policy' || data.type === 'claim') {
                    onPreviewChange({
                        type: data.type,
                        data: data
                    });
                    toast({
                        title: "Preview Updated",
                        description: `Viewing ${data.type} details.`,
                    });
                } else if (data.type === 'quote_selection') {
                    onPreviewChange({
                        type: 'quote_selection',
                        data: data.data || data
                    });
                    toast({
                        title: "Action Required",
                        description: "Select a quote to convert to policy.",
                    });
                }
            } catch (e) {
                console.warn("Failed to parse JSON for preview:", e);
            }
        }
    };

    const handleSendMessage = async (textOverride?: string) => {
        const userMsg = textOverride || inputValue.trim();
        if ((!userMsg && !selectedFile) || isLoading) return;

        if (!textOverride) setInputValue("");

        // If we were editing a field, prepend the instruction
        let finalMsg = userMsg;
        if (editingField) {
            finalMsg = `Update ${editingField} to ${userMsg}`;
            setEditingField(null);
            setActiveInteraction(null); // Clear active interaction once we respond
        }

        // Add User Message
        const newMessages: ChatMessage[] = [
            ...messages,
            { role: 'user', content: userMsg }
        ];
        setMessages(newMessages);
        setIsLoading(true);

        try {
            console.log("Sending message...", userMsg);

            // TODO: Handle File Upload via API if selectedFile exists
            if (selectedFile) {
                console.log("File upload would happen here:", selectedFile.name);
                setSelectedFile(null);
            }

            // Call API
            const response = await AiAPI.chat(userMsg);

            // Checks for Preview Data in response
            parsePreviewData(response.response);

            // Add Assistant Response
            setMessages(prev => [
                ...prev,
                { role: 'assistant', content: response.response }
            ]);

            // Refresh status to update badge if on credit plan
            if (subStatus?.plan === 'CREDIT') {
                loadSubscription();
            }

        } catch (error: any) {
            console.error("Failed to send message:", error);

            if (error.response?.status === 402) {
                setIsCreditModalOpen(true);
                return;
            }

            toast({
                title: "Error",
                description: error.response?.data?.detail || "Failed to communicate with the AI Agent.",
                variant: "destructive"
            });
            // Optionally remove user message or add error message
        } finally {
            setIsLoading(false);
        }
    };

    const runDebugDemo = () => {
        // Debug function to force a preview
        onPreviewChange({
            type: 'quote',
            data: {
                type: 'quote',
                client_name: 'TechCorp Industries',
                quote_number: 'Q-2025-001',
                premium_amount: 12500.00,
                policy_type: 'Cyber Liability',
                status: 'draft',
                coverage_details: 'Includes data breach response, ransomware extortion, and business interruption coverage up to $5M.'
            }
        });
        toast({ title: "Debug", description: "Injected mock quote preview." });
    };

    return (
        <div className="flex h-full flex-col border-r bg-card/50">
            {/* Task Title */}
            <div className="flex items-center gap-3 border-b p-4">
                <div className="flex h-8 w-8 items-center justify-center rounded-md bg-primary/10 text-primary">
                    <Bot className="h-5 w-5" />
                </div>
                <div>
                    <h2 className="text-sm font-semibold">{t('ai_manager.title')}</h2>
                    <div className="flex items-center gap-2">
                        <p className="text-xs text-muted-foreground">{t('ai_manager.active_orchestrator')}</p>
                        {subStatus?.plan === 'CREDIT' && (
                            <Badge variant="outline" className="h-5 px-1.5 bg-primary/5 border-primary/20 text-[10px] gap-1 animate-in fade-in slide-in-from-right-2">
                                <Coins className="h-2.5 w-2.5 text-primary" />
                                <span className="font-bold">${subStatus.credits.toFixed(2)}</span>
                            </Badge>
                        )}
                    </div>
                </div>
                <div className="ml-auto flex gap-1">
                    <Button variant="ghost" size="icon" title="Test Preview" onClick={runDebugDemo}>
                        <Play className="h-4 w-4 text-orange-500" />
                    </Button>
                    <Button variant="ghost" size="icon" title="Voice Mode">
                        <Headphones className="h-5 w-5" />
                    </Button>
                </div>
            </div>

            {/* Chat/Context Area */}
            <ScrollArea className="flex-1 p-4">
                <div className="space-y-6">
                    {messages.map((msg, index) => (
                        <div key={index} className={`flex gap-3 ${msg.role === 'user' ? 'flex-row-reverse' : ''}`}>
                            {/* Avatar */}
                            <div className={`
                                flex h-8 w-8 shrink-0 items-center justify-center rounded-md border
                                ${msg.role === 'assistant' ? 'bg-primary/10 text-primary border-primary/20' : 'bg-muted text-muted-foreground'}
                            `}>
                                {msg.role === 'assistant' ? <Bot className="h-5 w-5" /> : <User className="h-5 w-5" />}
                            </div>

                            {/* Message Bubble */}
                            <div className={`
                                max-w-[85%] rounded-lg p-3 text-sm
                                ${msg.role === 'user'
                                    ? 'bg-primary text-primary-foreground'
                                    : 'bg-background border shadow-sm'}
                            `}>
                                <div className={`prose prose-sm max-w-none ${msg.role === 'user' ? 'prose-invert' : 'dark:prose-invert'}`}>
                                    <ReactMarkdown>{msg.content}</ReactMarkdown>
                                </div>

                                {/* Interactive Modification List */}
                                {msg.role === 'assistant' && activeInteraction && index === messages.length - 1 && activeInteraction.type === 'modify' && activeInteraction.fields && (
                                    <div className="mt-4 space-y-2 border-t pt-3">
                                        <p className="text-xs font-semibold text-muted-foreground uppercase tracking-wider">Modify Elements</p>
                                        {activeInteraction.fields.map((field: any) => (
                                            <div key={field.key} className="flex items-center justify-between gap-4 p-2 rounded-md bg-muted/50 border">
                                                <div className="flex flex-col">
                                                    <span className="text-[10px] text-muted-foreground uppercase font-bold">{field.label}</span>
                                                    <span className="text-sm font-medium">{field.value}</span>
                                                </div>
                                                <div className="flex gap-1">
                                                    <Button
                                                        size="sm"
                                                        variant="ghost"
                                                        className="h-7 px-2 text-[10px]"
                                                        onClick={() => {
                                                            setEditingField(field.key);
                                                            setInputValue("");
                                                            toast({ title: `Editing ${field.label}`, description: "Please enter the new value in the chat box." });
                                                        }}
                                                    >
                                                        Edit
                                                    </Button>
                                                    <Button
                                                        size="sm"
                                                        variant="ghost"
                                                        className="h-7 px-2 text-[10px] text-green-600"
                                                        onClick={() => {
                                                            handleSendMessage(`Keep ${field.label}`);
                                                        }}
                                                    >
                                                        Keep
                                                    </Button>
                                                </div>
                                            </div>
                                        ))}
                                    </div>
                                )}
                                {msg.role === 'assistant' && activeInteraction && index === messages.length - 1 && activeInteraction.type === 'progress' && (
                                    <div className="mt-4 p-2 rounded-md bg-primary/5 border border-primary/20 flex items-center justify-between">
                                        <span className="text-xs font-medium text-primary">Form synchronization active</span>
                                        <div className="flex h-2 w-2 rounded-full bg-primary animate-pulse" />
                                    </div>
                                )}
                            </div>
                        </div>
                    ))}

                    {/* Loading Indicator */}
                    {isLoading && (
                        <div className="flex gap-3">
                            <div className="flex h-8 w-8 shrink-0 items-center justify-center rounded-md border bg-primary/10 text-primary border-primary/20">
                                <Bot className="h-5 w-5" />
                            </div>
                            <div className="flex items-center gap-1 rounded-lg border bg-background p-3 shadow-sm">
                                <span className="block h-2 w-2 animate-bounce rounded-full bg-primary/50" style={{ animationDelay: '0ms' }} />
                                <span className="block h-2 w-2 animate-bounce rounded-full bg-primary/50" style={{ animationDelay: '150ms' }} />
                                <span className="block h-2 w-2 animate-bounce rounded-full bg-primary/50" style={{ animationDelay: '300ms' }} />
                            </div>
                        </div>
                    )}
                    <div ref={scrollRef} />
                </div>
            </ScrollArea>

            {/* Input Area */}
            <div className="border-t p-4 space-y-3 bg-background">
                {selectedFile && (
                    <div className="flex items-center gap-2 p-2 bg-muted/50 rounded-md max-w-fit">
                        <Paperclip className="h-3 w-3" />
                        <span className="text-xs text-muted-foreground max-w-[200px] truncate">
                            {selectedFile.name}
                        </span>
                        <Button
                            variant="ghost"
                            size="icon"
                            className="h-4 w-4 hover:bg-transparent"
                            onClick={() => setSelectedFile(null)}
                        >
                            <X className="h-3 w-3" />
                        </Button>
                    </div>
                )}

                <div className="relative flex items-center gap-2">
                    {/* Hidden File Input */}
                    <input
                        type="file"
                        ref={fileInputRef}
                        className="hidden"
                        onChange={handleFileSelect}
                        accept="video/*,.pdf,.xls,.xlsx,.doc,.docx,.csv,.png,.jpg,.jpeg,.md"
                    />

                    {/* Plus Menu */}
                    <DropdownMenu>
                        <DropdownMenuTrigger asChild>
                            <Button variant="outline" size="icon" className="h-10 w-10 shrink-0 rounded-full">
                                <Plus className="h-5 w-5" />
                            </Button>
                        </DropdownMenuTrigger>
                        <DropdownMenuContent align="start" className="w-56">
                            <DropdownMenuItem onClick={handleTriggerUpload}>
                                <Paperclip className="mr-2 h-4 w-4" />
                                Add photos & files
                            </DropdownMenuItem>
                            <DropdownMenuSeparator />
                            <DropdownMenuItem>
                                <ImageIcon className="mr-2 h-4 w-4" />
                                Create image
                            </DropdownMenuItem>
                        </DropdownMenuContent>
                    </DropdownMenu>

                    {/* Text Input */}
                    <div className="relative flex-1">
                        <Input
                            placeholder={isLoading ? "AI is thinking..." : t('ai_manager.chat_placeholder')}
                            value={inputValue}
                            onChange={(e) => setInputValue(e.target.value)}
                            onKeyDown={(e) => {
                                if (e.key === 'Enter' && !e.shiftKey) {
                                    e.preventDefault();
                                    handleSendMessage();
                                }
                            }}
                            disabled={isLoading}
                            className="pr-20 py-6 bg-muted/50 border-input/50 focus-visible:bg-background rounded-full"
                        />
                        <div className="absolute right-2 top-1/2 -translate-y-1/2 flex items-center gap-1">
                            <Button
                                size="icon"
                                variant="ghost"
                                className="h-8 w-8 hover:bg-transparent text-muted-foreground"
                            >
                                <Mic className="h-4 w-4" />
                            </Button>
                            <Button
                                size="icon"
                                onClick={() => handleSendMessage()}
                                variant={inputValue ? "default" : "ghost"}
                                disabled={isLoading || (!inputValue && !selectedFile)}
                                className={`h-8 w-8 rounded-full ${inputValue ? "" : "text-muted-foreground hover:bg-transparent"}`}
                            >
                                <Send className="h-4 w-4" />
                            </Button>
                        </div>
                    </div>
                </div>
                <div className="text-center">
                    <span className="text-[10px] text-muted-foreground">
                        {t('ai_manager.disclaimer')}
                    </span>
                </div>
            </div>
            {/* Voice UI Overlays would go here */}

            <CreditLimitModal
                isOpen={isCreditModalOpen}
                onClose={() => setIsCreditModalOpen(false)}
            />
        </div>
    );
}
