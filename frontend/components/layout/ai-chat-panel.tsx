'use client';

import { useState, useRef, useCallback } from 'react';
import { cn } from '@/lib/utils';
import { Button } from '@/components/ui/button';
import { ScrollArea } from '@/components/ui/scroll-area';
import { Input } from '@/components/ui/input';
import { X, Bot, Sparkles, Send, User } from 'lucide-react';
import { useLanguage } from '@/contexts/language-context';
import { AiAPI, ChatMessage } from '@/lib/ai-api';

interface AIChatPanelProps {
    isOpen: boolean;
    onClose: () => void;
    className?: string;
}

interface Message {
    role: 'user' | 'assistant';
    content: string;
}

export function AIChatPanel({ isOpen, onClose, className }: AIChatPanelProps) {
    const { t } = useLanguage();
    const [messages, setMessages] = useState<Message[]>([]);
    const [input, setInput] = useState('');
    const [loading, setLoading] = useState(false);
    const streamingPlaceholderAdded = useRef(false);
    const cleanupRef = useRef<(() => void) | null>(null);

    if (!isOpen) return null;

    const sendMessage = useCallback(() => {
        if (!input.trim() || loading) return;

        const userMessage = input.trim();
        setInput('');
        const history: ChatMessage[] = messages.map(m => ({ role: m.role, content: m.content }));
        setMessages(prev => [...prev, { role: 'user', content: userMessage }]);
        setLoading(true);
        streamingPlaceholderAdded.current = false;

        // Clean up any previous stream
        cleanupRef.current?.();

        const cleanup = AiAPI.streamChat(
            userMessage,
            history,
            (chunk) => {
                // Append streamed token
                setMessages(prev => {
                    if (!streamingPlaceholderAdded.current) {
                        streamingPlaceholderAdded.current = true;
                        return [...prev, { role: 'assistant', content: chunk }];
                    }
                    const updated = [...prev];
                    updated[updated.length - 1] = {
                        ...updated[updated.length - 1],
                        content: updated[updated.length - 1].content + chunk,
                    };
                    return updated;
                });
            },
            (_fullText) => {
                setLoading(false);
                streamingPlaceholderAdded.current = false;
            },
            (_code) => {
                if (!streamingPlaceholderAdded.current) {
                    setMessages(prev => [...prev, {
                        role: 'assistant',
                        content: t('ai.chat.error', 'Sorry, I encountered an error. Please try again.'),
                    }]);
                }
                setLoading(false);
            },
        );
        cleanupRef.current = cleanup;
    }, [input, loading, messages, t]);

    const handleKeyDown = (e: React.KeyboardEvent) => {
        if (e.key === 'Enter' && !e.shiftKey) {
            e.preventDefault();
            sendMessage();
        }
    };

    return (
        <div
            className={cn(
                'flex h-full w-full flex-col border-r bg-background shadow-xl',
                className
            )}
        >
            <div className="flex h-14 items-center justify-between border-b px-4 py-2 bg-muted/30">
                <div className="flex items-center gap-2">
                    <Bot className="h-5 w-5 text-primary" />
                    <span className="font-semibold">AI Assistant</span>
                </div>
                <Button variant="ghost" size="icon" onClick={onClose} className="h-8 w-8">
                    <X className="h-4 w-4" />
                    <span className="sr-only">Close</span>
                </Button>
            </div>

            <ScrollArea className="flex-1 p-4">
                {messages.length === 0 ? (
                    <div className="flex flex-col items-center justify-center space-y-4 py-10 text-center text-muted-foreground">
                        <div className="flex h-12 w-12 items-center justify-center rounded-full bg-primary/10">
                            <Sparkles className="h-6 w-6 text-primary" />
                        </div>
                        <div className="space-y-2 px-4">
                            <h3 className="font-medium text-foreground">How can I help you?</h3>
                            <p className="text-sm">
                                Ask about policies, claims, quotes, or financial reports.
                            </p>
                        </div>
                    </div>
                ) : (
                    <div className="space-y-4">
                        {messages.map((msg, idx) => (
                            <div
                                key={idx}
                                className={cn(
                                    "flex w-full gap-2",
                                    msg.role === 'user' ? "justify-end" : "justify-start"
                                )}
                            >
                                {msg.role === 'assistant' && (
                                    <div className="h-8 w-8 shrink-0 rounded-full bg-primary/10 flex items-center justify-center">
                                        <Bot className="h-5 w-5 text-primary" />
                                    </div>
                                )}
                                <div
                                    className={cn(
                                        "rounded-lg px-3 py-2 text-sm max-w-[80%]",
                                        msg.role === 'user'
                                            ? "bg-primary text-primary-foreground"
                                            : "bg-muted text-foreground"
                                    )}
                                >
                                    {msg.content}
                                </div>
                                {msg.role === 'user' && (
                                    <div className="h-8 w-8 shrink-0 rounded-full bg-muted flex items-center justify-center">
                                        <User className="h-5 w-5" />
                                    </div>
                                )}
                            </div>
                        ))}
                        {loading && (
                            <div className="flex w-full gap-2 justify-start">
                                <div className="h-8 w-8 shrink-0 rounded-full bg-primary/10 flex items-center justify-center">
                                    <Bot className="h-5 w-5 text-primary" />
                                </div>
                                <div className="bg-muted rounded-lg px-3 py-2 text-sm flex items-center">
                                    <div className="flex space-x-1">
                                        <div className="w-2 h-2 bg-current rounded-full animate-bounce [animation-delay:-0.3s]"></div>
                                        <div className="w-2 h-2 bg-current rounded-full animate-bounce [animation-delay:-0.15s]"></div>
                                        <div className="w-2 h-2 bg-current rounded-full animate-bounce"></div>
                                    </div>
                                </div>
                            </div>
                        )}
                    </div>
                )}
            </ScrollArea>

            <div className="border-t p-4 bg-background">
                <div className="flex items-center gap-2">
                    <Input
                        value={input}
                        onChange={(e) => setInput(e.target.value)}
                        onKeyDown={handleKeyDown}
                        placeholder={t('placeholder.type_message', 'Type your message...')}
                        className="flex-1"
                        disabled={loading}
                    />
                    <Button onClick={sendMessage} disabled={loading || !input.trim()} size="icon">
                        <Send className="h-4 w-4" />
                    </Button>
                </div>
            </div>
        </div>
    );
}
