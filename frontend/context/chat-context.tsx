'use client';

import React, { createContext, useContext, useState, ReactNode } from 'react';
import { PreviewState } from '@/types/ai-agent';
import { ChatMessage } from '@/lib/ai-api';

interface ChatContextType {
    messages: ChatMessage[];
    setMessages: React.Dispatch<React.SetStateAction<ChatMessage[]>>;
    previewState: PreviewState;
    setPreviewState: React.Dispatch<React.SetStateAction<PreviewState>>;
    isAiOpen: boolean;
    setIsAiOpen: (open: boolean) => void;
    pendingAction: { action: string; data: any } | null;
    setPendingAction: (action: { action: string; data: any } | null) => void;
}

const ChatContext = createContext<ChatContextType | undefined>(undefined);

export function ChatProvider({ children }: { children: ReactNode }) {
    const [messages, setMessages] = useState<ChatMessage[]>([]);
    const [previewState, setPreviewState] = useState<PreviewState>({
        type: 'empty',
        data: null
    });
    const [isAiOpen, setIsAiOpen] = useState(false);
    const [pendingAction, setPendingAction] = useState<{ action: string; data: any } | null>(null);

    return (
        <ChatContext.Provider
            value={{
                messages,
                setMessages,
                previewState,
                setPreviewState,
                isAiOpen,
                setIsAiOpen,
                pendingAction,
                setPendingAction,
            }}
        >
            {children}
        </ChatContext.Provider>
    );
}

export function useChat() {
    const context = useContext(ChatContext);
    if (context === undefined) {
        throw new Error('useChat must be used within a ChatProvider');
    }
    return context;
}
