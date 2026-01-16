'use client';

import { useState, useRef, useEffect } from 'react';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { ScrollArea } from '@/components/ui/scroll-area';
import { Card, CardContent } from '@/components/ui/card';
import { Bot, Send, Paperclip, X, User, Loader2, Image as ImageIcon, Sparkles } from 'lucide-react';
import { AiAPI, ChatMessage } from '@/lib/ai-api';
import { api } from '@/lib/api';
import { toast } from '@/components/ui/use-toast';
import ReactMarkdown from 'react-markdown';
import { useLanguage } from '@/contexts/language-context';
import { Badge } from '@/components/ui/badge';

export function SupportChatWidget() {
    const { t } = useLanguage();
    const [messages, setMessages] = useState<ChatMessage[]>([]);
    const [inputValue, setInputValue] = useState("");
    const [isLoading, setIsLoading] = useState(false);
    const [selectedFile, setSelectedFile] = useState<File | null>(null);
    const [uploading, setUploading] = useState(false);
    const scrollRef = useRef<HTMLDivElement>(null);
    const fileInputRef = useRef<HTMLInputElement>(null);

    // Initial Welcome and Proactive Trigger
    useEffect(() => {
        if (messages.length === 0) {
            setMessages([
                {
                    role: 'assistant',
                    content: "Hello! I'm your Tinsur.AI Personal Assistant. I'm checking your account status right now..."
                }
            ]);
            // Trigger proactive check by sending a hidden greeting
            handleSendMessage("Hello, checking in.", true);
        }
    }, []);

    // Auto-scroll
    useEffect(() => {
        if (scrollRef.current) {
            scrollRef.current.scrollIntoView({ behavior: 'smooth' });
        }
    }, [messages]);

    const handleSendMessage = async (textOverride?: string, isProactive: boolean = false) => {
        const content = textOverride || inputValue.trim();
        if ((!content && !selectedFile) || isLoading) return;

        if (!textOverride) setInputValue("");

        // Add user message to UI (unless it's a silent proactive trigger)
        if (!isProactive) {
            setMessages(prev => [...prev, { role: 'user', content }]);
        }

        setIsLoading(true);

        try {
            let imagePath = undefined;

            // Handle file upload if present
            if (selectedFile) {
                setUploading(true);
                const formData = new FormData();
                formData.append('file', selectedFile);
                formData.append('label', 'Incident Photo');

                try {
                    const uploadRes = await api.post('/documents/upload', formData, {
                        headers: { 'Content-Type': 'multipart/form-data' }
                    });
                    imagePath = uploadRes.data.url;
                    setSelectedFile(null);
                } catch (err) {
                    toast({
                        title: "Upload Failed",
                        description: "Could not upload photo. Sending message without it.",
                        variant: "destructive"
                    });
                } finally {
                    setUploading(false);
                }
            }

            const response = await AiAPI.chat(content, messages, undefined, imagePath);

            setMessages(prev => [...prev, {
                role: 'assistant',
                content: response.response
            }]);

        } catch (error) {
            console.error("Chat error:", error);
            toast({
                title: "Error",
                description: "Failed to connect to assistant.",
                variant: "destructive"
            });
        } finally {
            setIsLoading(false);
        }
    };

    const triggerFileUpload = () => {
        fileInputRef.current?.click();
    };

    return (
        <Card className="flex flex-col h-[600px] border-slate-200 shadow-xl overflow-hidden bg-white">
            <div className="p-4 border-b bg-primary/5 flex items-center justify-between">
                <div className="flex items-center gap-3">
                    <div className="h-10 w-10 rounded-full bg-blue-600 flex items-center justify-center text-white shadow-lg shadow-blue-200">
                        <Bot className="h-6 w-6" />
                    </div>
                    <div>
                        <h3 className="font-bold text-slate-900 leading-tight">AI Assistant</h3>
                        <div className="flex items-center gap-1.5">
                            <span className="h-2 w-2 rounded-full bg-green-500 animate-pulse" />
                            <span className="text-[11px] text-slate-500 font-medium uppercase tracking-wider">Online • Intelligent Care</span>
                        </div>
                    </div>
                </div>
                <Badge variant="outline" className="bg-white border-blue-100 text-blue-700 gap-1 px-2 py-1">
                    <Sparkles className="h-3 w-3" />
                    Smart Support
                </Badge>
            </div>

            <ScrollArea className="flex-1 p-4 bg-slate-50/50">
                <div className="space-y-4">
                    {messages.map((msg, idx) => (
                        <div key={idx} className={`flex gap-3 ${msg.role === 'user' ? 'flex-row-reverse' : ''}`}>
                            <div className={`h-8 w-8 rounded-lg flex items-center justify-center shrink-0 border shadow-sm ${msg.role === 'assistant' ? 'bg-white text-blue-600' : 'bg-blue-600 text-white'
                                }`}>
                                {msg.role === 'assistant' ? <Bot className="h-5 w-5" /> : <User className="h-5 w-5" />}
                            </div>
                            <div className={`max-w-[85%] p-3.5 rounded-2xl text-sm leading-relaxed shadow-sm ${msg.role === 'assistant'
                                ? 'bg-white border text-slate-700 rounded-tl-none'
                                : 'bg-blue-600 text-white rounded-tr-none'
                                }`}>
                                <div className="prose prose-sm max-w-none prose-slate">
                                    <ReactMarkdown>{msg.content}</ReactMarkdown>
                                </div>
                                {msg.role === 'assistant' && msg.content.includes('Found in:') && (
                                    <div className="mt-2 pt-2 border-t border-slate-100 flex items-center gap-1.5 text-[10px] text-slate-400 font-mono">
                                        <Paperclip className="h-3 w-3" />
                                        Verified Source
                                    </div>
                                )}
                            </div>
                        </div>
                    ))}
                    {isLoading && (
                        <div className="flex gap-3">
                            <div className="h-8 w-8 rounded-lg bg-white border flex items-center justify-center shadow-sm">
                                <Bot className="h-5 w-5 text-blue-600" />
                            </div>
                            <div className="bg-white border p-3 rounded-2xl rounded-tl-none shadow-sm flex items-center gap-2">
                                <Loader2 className="h-4 w-4 animate-spin text-blue-500" />
                                <span className="text-xs text-slate-500 font-medium">Assistant is thinking...</span>
                            </div>
                        </div>
                    )}
                    <div ref={scrollRef} />
                </div>
            </ScrollArea>

            <div className="p-4 border-t bg-white space-y-3">
                {selectedFile && (
                    <div className="flex items-center gap-2 p-2 bg-blue-50 border border-blue-100 rounded-lg max-w-fit animate-in fade-in slide-in-from-bottom-2">
                        <ImageIcon className="h-4 w-4 text-blue-600" />
                        <span className="text-xs font-medium text-blue-700 truncate max-w-[150px]">{selectedFile.name}</span>
                        <Button variant="ghost" size="icon" className="h-5 w-5 hover:bg-transparent" onClick={() => setSelectedFile(null)}>
                            <X className="h-3 w-3 text-blue-400" />
                        </Button>
                    </div>
                )}

                <div className="flex gap-2">
                    <input
                        type="file"
                        ref={fileInputRef}
                        className="hidden"
                        onChange={(e) => e.target.files && setSelectedFile(e.target.files[0])}
                        accept="image/*,.pdf"
                    />
                    <Button
                        variant="outline"
                        size="icon"
                        className="h-12 w-12 rounded-xl shrink-0 border-slate-200 hover:bg-slate-50"
                        onClick={triggerFileUpload}
                        disabled={isLoading}
                    >
                        <Paperclip className="h-5 w-5 text-slate-500" />
                    </Button>
                    <div className="relative flex-1">
                        <Input
                            placeholder="Type your message..."
                            className="h-12 px-4 rounded-xl border-slate-200 bg-slate-50 focus-visible:bg-white focus-visible:ring-blue-500"
                            value={inputValue}
                            onChange={(e) => setInputValue(e.target.value)}
                            onKeyDown={(e) => e.key === 'Enter' && handleSendMessage()}
                            disabled={isLoading}
                        />
                        <Button
                            size="icon"
                            className={`absolute right-1.5 top-1.5 h-9 w-9 rounded-lg transition-all ${inputValue.trim() || selectedFile ? 'bg-blue-600 hover:bg-blue-700' : 'bg-slate-200 text-white cursor-not-allowed'
                                }`}
                            onClick={() => handleSendMessage()}
                            disabled={isLoading || (!inputValue.trim() && !selectedFile)}
                        >
                            <Send className="h-4 w-4" />
                        </Button>
                    </div>
                </div>
                <p className="text-[10px] text-center text-slate-400 font-medium">
                    AI can make mistakes. Check important info.
                </p>
            </div>
        </Card>
    );
}
