"use client";

import { useState, useCallback, useEffect, useRef } from "react";
import { ChatMessage, ChatState } from "@/lib/types/chat";
import { SpendingSnapshotData } from "@/lib/types/spending";

import { Loader2, MessageSquare, AlertCircle, Brain } from "lucide-react";
import { Alert, AlertDescription } from "@/components/ui/alert";
import { UserMessage } from "./UserMessage";
import { AgentMessage } from "./AgentMessage";
import { ChatInput } from "./ChatInput";

interface SpendingChatProps {
  userId: string;
  isEnabled: boolean; // Chat appears after snapshot loads
  spendingData: SpendingSnapshotData | null;
}

export function SpendingChat({
  userId,
  isEnabled,
  spendingData,
}: SpendingChatProps) {
  const [chatState, setChatState] = useState<ChatState>({
    messages: [],
    isLoading: false,
    error: null,
    sessionId: null,
  });

  const messagesEndRef = useRef<HTMLDivElement>(null);

  // Auto-scroll to bottom when new messages arrive
  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
  };

  useEffect(() => {
    scrollToBottom();
  }, [chatState.messages]);

  const sendMessage = useCallback(
    async (message: string) => {
      if (!message.trim() || chatState.isLoading) {
        return;
      }

      console.log("[CHAT] 🚀 Sending message:", message);

      // Prepare message with context for first message only
      let messageToSend = message.trim();

      // If this is the first message (no sessionId), include spending context
      if (!chatState.sessionId && spendingData) {
        console.log("[CHAT] 🎯 First message - adding spending context");

        // Format spending data as context
        const contextData = {
          income: spendingData.income,
          expenses: spendingData.expenses,
          activities: spendingData.activities,
          insights: spendingData.insights,
        };

        messageToSend = `${message.trim()}

<SPENDING_CONTEXT>
${JSON.stringify(contextData, null, 2)}
</SPENDING_CONTEXT>`;

        console.log("[CHAT] 📊 Added spending context:", contextData);
      }

      // Add user message to chat (display original message without context)
      const userMessage: ChatMessage = {
        id: `user-${Date.now()}`,
        type: "user",
        content: message.trim(), // Display original message
        timestamp: new Date(),
      };

      setChatState((prev) => ({
        ...prev,
        messages: [...prev.messages, userMessage],
        isLoading: true,
        error: null,
      }));

      try {
        // Create request body for the API proxy
        const requestBody = {
          userId,
          message: messageToSend, // Send contextual message to API
          ...(chatState.sessionId && { sessionId: chatState.sessionId }),
        };

        console.log("[CHAT] 📤 Request body:", requestBody);

        // Use our API proxy (not direct agent call)
        const response = await fetch("/api/cymbal/chat", {
          method: "POST",
          headers: {
            "Content-Type": "application/json",
            Accept: "application/json", // Request JSON response instead of SSE
          },
          body: JSON.stringify(requestBody),
        });

        if (!response.ok) {
          throw new Error(`HTTP error! status: ${response.status}`);
        }

        const data = await response.json();
        console.log("[CHAT] 📥 Received response:", data);

        // Create agent message from response
        const agentMessage: ChatMessage = {
          id: `agent-${Date.now()}`,
          type: "agent",
          content: data.response || "No response received",
          timestamp: new Date(),
        };

        console.log(
          "[CHAT] ✅ Agent message created:",
          agentMessage.content.substring(0, 100)
        );

        // Always update sessionId to ensure persistence across messages
        if (data.session_id) {
          if (data.session_id !== chatState.sessionId) {
            console.log("[CHAT] 📋 Session ID updated:", data.session_id);
          } else {
            console.log("[CHAT] 🔄 Session ID maintained:", data.session_id);
          }
        }

        // Update state with both message and session ID
        setChatState((prev) => ({
          ...prev,
          messages: [...prev.messages, agentMessage],
          isLoading: false,
          sessionId: data.session_id || prev.sessionId, // Always use session_id from response
        }));
      } catch (error) {
        console.error("[CHAT] ❌ Chat error:", error);

        setChatState((prev) => ({
          ...prev,
          isLoading: false,
          error:
            error instanceof Error ? error.message : "Failed to send message",
        }));
      }
    },
    [userId, chatState.sessionId, chatState.isLoading, spendingData]
  );

  // Don't render chat until snapshot is loaded
  if (!isEnabled) {
    return (
      <div className="h-full flex items-center justify-center bg-gradient-to-b from-transparent via-primary/[0.02] to-transparent relative">
        {/* Glass loading card */}
        <div className="bg-card/90 backdrop-blur-md border border-border/50 rounded-2xl p-8 shadow-lg relative overflow-hidden">
          <div className="absolute inset-0 bg-gradient-to-br from-white/5 via-transparent to-white/5 pointer-events-none" />

          <div className="relative flex flex-col items-center space-y-6">
            {/* Animated AI Brain logo */}
            <div className="relative">
              <div className="w-16 h-16 bg-gradient-to-br from-primary to-cyan-500 rounded-2xl flex items-center justify-center shadow-lg animate-pulse">
                <Brain className="h-8 w-8 text-white" />
              </div>
              <div className="absolute -bottom-1 -right-1">
                <MessageSquare className="h-5 w-5 text-cyan-400 animate-pulse" />
              </div>
            </div>

            {/* Loading spinner */}
            <Loader2 className="h-8 w-8 animate-spin text-primary" />

            <div className="text-center space-y-2">
              <p className="text-foreground font-semibold">
                Waiting for Snapshot
              </p>
              <p className="text-muted-foreground text-sm">
                Chat will be available after data analysis...
              </p>
            </div>

            {/* Progress dots */}
            <div className="flex items-center gap-2">
              <div className="w-2 h-2 bg-primary rounded-full animate-pulse" />
              <div
                className="w-2 h-2 bg-primary rounded-full animate-pulse"
                style={{ animationDelay: "0.3s" }}
              />
              <div
                className="w-2 h-2 bg-primary rounded-full animate-pulse"
                style={{ animationDelay: "0.6s" }}
              />
            </div>
          </div>
        </div>
      </div>
    );
  }

  // Error state
  if (chatState.error) {
    return (
      <div className="h-full p-6 flex items-center justify-center">
        <div className="w-full max-w-md">
          <Alert variant="destructive">
            <AlertCircle className="h-4 w-4" />
            <AlertDescription>
              {chatState.error}
              <button
                onClick={() =>
                  setChatState((prev) => ({ ...prev, error: null }))
                }
                className="ml-2 underline hover:no-underline"
              >
                Dismiss
              </button>
            </AlertDescription>
          </Alert>
        </div>
      </div>
    );
  }

  return (
    <div className="h-full flex flex-col bg-gradient-to-b from-background to-muted/20">
      {/* Scrollable Messages Area */}
      <div className="flex-1 overflow-hidden">
        <div className="h-full overflow-y-auto">
          {chatState.messages.length === 0 && !chatState.isLoading ? (
            <div className="h-full flex items-center justify-center p-6">
              <div className="text-center max-w-md">
                <div className="relative mb-6">
                  <div className="w-20 h-20 bg-gradient-to-br from-primary/20 to-primary/10 rounded-2xl flex items-center justify-center mx-auto mb-4 shadow-lg">
                    <MessageSquare className="h-8 w-8 text-primary" />
                  </div>
                  <div className="absolute top-0 right-8 w-3 h-3 bg-blue-400 rounded-full animate-bounce delay-75" />
                  <div className="absolute top-4 right-4 w-2 h-2 bg-green-400 rounded-full animate-bounce delay-150" />
                  <div className="absolute top-2 right-12 w-2 h-2 bg-purple-400 rounded-full animate-bounce" />
                </div>

                <h3 className="text-2xl font-bold bg-gradient-to-r from-foreground via-foreground/90 to-foreground/70 bg-clip-text text-transparent mb-3">
                  Let&rsquo;s talk about your money
                </h3>
                <p className="text-muted-foreground mb-8 leading-relaxed">
                  I&rsquo;m here to help you understand your spending patterns,
                  find savings opportunities, and make smarter financial
                  decisions.
                </p>

                {/* Quick Start Suggestions */}
                <div className="space-y-3">
                  <p className="text-sm font-medium text-foreground/80 mb-4">
                    Try asking me:
                  </p>
                  <div className="grid gap-2">
                    {[
                      "💳 What did I spend the most on this month?",
                      "📊 Show me my spending trends",
                      "💡 Where can I save money?",
                      "🎯 Help me set a budget goal",
                    ].map((suggestion, index) => (
                      <button
                        key={index}
                        onClick={() => sendMessage(suggestion.slice(2).trim())}
                        className="text-left p-3 rounded-lg bg-card hover:bg-accent/50 border border-border/50 hover:border-border transition-all duration-200 text-sm group hover:shadow-sm"
                      >
                        <span className="group-hover:text-primary transition-colors">
                          {suggestion}
                        </span>
                      </button>
                    ))}
                  </div>
                </div>
              </div>
            </div>
          ) : (
            <div className="p-3 space-y-2 pb-24">
              {chatState.messages.map((message) =>
                message.type === "user" ? (
                  <UserMessage key={message.id} message={message} />
                ) : (
                  <AgentMessage key={message.id} message={message} />
                )
              )}

              {/* Show loading spinner while waiting for response */}
              {chatState.isLoading && (
                <div className="flex items-center justify-center space-x-2 py-8">
                  <div className="animate-spin rounded-full h-6 w-6 border-2 border-primary border-t-transparent"></div>
                  <span className="text-muted-foreground">
                    AI is thinking...
                  </span>
                </div>
              )}

              <div ref={messagesEndRef} />
            </div>
          )}
        </div>
      </div>

      {/* Fixed Chat Input at Bottom */}
      <div className="flex-shrink-0 bg-background/90 backdrop-blur-md border-t border-border/50 shadow-lg relative z-10">
        <ChatInput
          onSendMessage={sendMessage}
          disabled={chatState.isLoading}
          isLoading={chatState.isLoading}
        />
      </div>
    </div>
  );
}
