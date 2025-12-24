import { ChatMessage } from "@/lib/types/chat";
import { Card, CardContent } from "@/components/ui/card";
import { Loader2, Brain, DollarSign, Sparkles } from "lucide-react";
import { cn } from "@/lib/utils";
import ReactMarkdown from "react-markdown";

interface AgentMessageProps {
  message: ChatMessage;
}

export function AgentMessage({ message }: AgentMessageProps) {
  return (
    <div className="flex justify-start mb-1 animate-in slide-in-from-left-2 duration-500">
      <div className="flex items-start gap-2 max-w-[85%]">
        {/* Enhanced FI Logo Avatar */}
        <div className="flex-shrink-0 relative group">
          {/* Main avatar container with glass effect */}
          <div
            className={cn(
              "relative w-8 h-8 rounded-xl flex items-center justify-center shadow-md transition-all duration-300",
              "bg-card/90 backdrop-blur-md border border-border/50",
              message.streaming
                ? "animate-pulse bg-gradient-to-br from-orange-500/10 to-orange-600/20"
                : "bg-gradient-to-br from-primary/10 to-cyan-500/20 group-hover:scale-105"
            )}
          >
            {/* Glass effect overlay */}
            <div className="absolute inset-0 bg-gradient-to-br from-white/10 via-transparent to-white/5 rounded-xl pointer-events-none" />

            {/* FI Logo - Brain + DollarSign */}
            <div className="relative flex items-center justify-center">
              {message.streaming ? (
                <div className="flex items-center gap-1">
                  <Brain className="h-3 w-3 text-orange-500" />
                  <Loader2 className="h-2.5 w-2.5 animate-spin text-orange-400" />
                </div>
              ) : (
                <div className="flex items-center gap-0.5">
                  <Brain className="h-3 w-3 text-primary" />
                  <DollarSign className="h-2.5 w-2.5 text-cyan-500" />
                </div>
              )}
            </div>

            {/* Floating sparkle for completed messages */}
            {!message.streaming && (
              <div className="absolute -top-1 -right-1">
                <Sparkles className="h-3 w-3 text-cyan-400 animate-pulse" />
              </div>
            )}
          </div>

          {/* Status indicator */}
          <div
            className={cn(
              "absolute -bottom-1 -right-1 w-4 h-4 rounded-full border-2 border-background shadow-sm",
              message.streaming
                ? "bg-gradient-to-r from-orange-400 to-orange-500 animate-pulse"
                : "bg-gradient-to-r from-green-400 to-emerald-500"
            )}
          />

          {/* AI consciousness indicator */}
          {message.streaming && (
            <div className="absolute -top-1 -left-1 w-4 h-4 bg-orange-400/20 rounded-full animate-ping" />
          )}
        </div>

        {/* Enhanced Glass Message Card */}
        <Card
          className={cn(
            "relative bg-card/90 backdrop-blur-md border border-border/50 shadow-xl",
            "transition-all duration-300 hover:shadow-2xl hover:border-primary/30",
            "overflow-hidden group"
          )}
        >
          {/* Glass effect overlays */}
          <div className="absolute inset-0 bg-gradient-to-br from-white/5 via-transparent to-white/5 pointer-events-none" />
          <div className="absolute top-0 right-0 w-32 h-32 bg-gradient-to-bl from-primary/10 via-cyan-500/5 to-transparent rounded-full blur-3xl" />

          <CardContent className="px-4 py-3 relative">
            {/* AI Header */}
            <div className="flex items-center gap-2 mb-2 pb-2 border-b border-border/30">
              <div className="flex items-center gap-2">
                <div className="w-2 h-2 rounded-full bg-gradient-to-r from-primary to-cyan-500" />
                <span className="text-sm font-medium bg-gradient-to-r from-primary via-primary/90 to-cyan-600 bg-clip-text text-transparent">
                  FI Assistant
                </span>
              </div>

              {message.streaming && (
                <div className="flex items-center gap-1 ml-auto">
                  <div className="flex gap-1">
                    <div className="w-1 h-1 bg-orange-400 rounded-full animate-bounce" />
                    <div
                      className="w-1 h-1 bg-orange-400 rounded-full animate-bounce"
                      style={{ animationDelay: "0.1s" }}
                    />
                    <div
                      className="w-1 h-1 bg-orange-400 rounded-full animate-bounce"
                      style={{ animationDelay: "0.2s" }}
                    />
                  </div>
                  <span className="text-xs text-orange-500 font-medium ml-2">
                    Thinking...
                  </span>
                </div>
              )}
            </div>

            {/* Enhanced Content */}
            <div className="prose prose-sm dark:prose-invert max-w-none">
              <ReactMarkdown
                components={{
                  // Enhanced paragraph styling
                  p: ({ children }) => (
                    <p className="text-sm leading-relaxed mb-4 last:mb-0 text-foreground/95">
                      {children}
                    </p>
                  ),
                  // Enhanced list styling with better spacing
                  ul: ({ children }) => (
                    <ul className="text-sm space-y-2 mb-4 ml-5 list-none text-foreground/95">
                      {children}
                    </ul>
                  ),
                  ol: ({ children }) => (
                    <ol className="text-sm space-y-2 mb-4 ml-5 list-decimal text-foreground/95">
                      {children}
                    </ol>
                  ),
                  li: ({ children }) => (
                    <li className="text-foreground/95 relative">
                      <div className="absolute -left-4 top-2 w-1.5 h-1.5 bg-gradient-to-r from-primary to-cyan-500 rounded-full" />
                      {children}
                    </li>
                  ),
                  // Enhanced emphasis with gradients
                  strong: ({ children }) => (
                    <strong className="font-semibold bg-gradient-to-r from-primary via-primary/90 to-cyan-600 bg-clip-text text-transparent">
                      {children}
                    </strong>
                  ),
                  em: ({ children }) => (
                    <em className="italic text-primary/80 font-medium">
                      {children}
                    </em>
                  ),
                  // Enhanced code styling with glass effect
                  code: ({ children, className }) => {
                    // Inline code
                    if (!className) {
                      return (
                        <code className="bg-background/80 backdrop-blur-sm px-2 py-1 rounded-md text-xs font-mono border border-border/50 shadow-sm">
                          {children}
                        </code>
                      );
                    }
                    // Code blocks
                    return (
                      <code className="block bg-background/80 backdrop-blur-sm p-4 rounded-xl border border-border/50 text-xs font-mono overflow-x-auto shadow-sm">
                        {children}
                      </code>
                    );
                  },
                  // Enhanced headings
                  h1: ({ children }) => (
                    <h1 className="text-lg font-semibold mb-3 bg-gradient-to-r from-primary to-cyan-600 bg-clip-text text-transparent">
                      {children}
                    </h1>
                  ),
                  h2: ({ children }) => (
                    <h2 className="text-base font-semibold mb-3 bg-gradient-to-r from-primary to-cyan-600 bg-clip-text text-transparent">
                      {children}
                    </h2>
                  ),
                  h3: ({ children }) => (
                    <h3 className="text-sm font-semibold mb-2 text-primary">
                      {children}
                    </h3>
                  ),
                  // Enhanced blockquotes with glass effect
                  blockquote: ({ children }) => (
                    <blockquote className="border-l-4 border-gradient-to-b from-primary to-cyan-500 pl-4 italic text-muted-foreground bg-background/30 backdrop-blur-sm rounded-r-lg py-2 my-4">
                      {children}
                    </blockquote>
                  ),
                }}
              >
                {message.content}
              </ReactMarkdown>
            </div>

            {/* Enhanced Footer */}
            {!message.streaming && (
              <div className="flex items-center justify-between mt-3 pt-2 border-t border-gradient-to-r from-transparent via-border/50 to-transparent">
                <div className="flex items-center gap-3">
                  <div className="w-2 h-2 bg-gradient-to-r from-green-400 to-emerald-500 rounded-full shadow-sm" />
                  <span className="text-xs text-muted-foreground font-medium">
                    {message.timestamp.toLocaleTimeString([], {
                      hour: "2-digit",
                      minute: "2-digit",
                    })}
                  </span>
                  <div className="h-3 w-px bg-border/50" />
                  <span className="text-xs bg-gradient-to-r from-primary/70 to-cyan-600/70 bg-clip-text text-transparent font-medium">
                    AI Analysis Complete
                  </span>
                </div>

                {/* Confidence indicator */}
                <div className="flex items-center gap-2">
                  <div className="flex gap-0.5">
                    <div className="w-1 h-3 bg-gradient-to-t from-green-400 to-emerald-500 rounded-full" />
                    <div className="w-1 h-3 bg-gradient-to-t from-green-400 to-emerald-500 rounded-full" />
                    <div className="w-1 h-2 bg-gradient-to-t from-green-400/70 to-emerald-500/70 rounded-full" />
                  </div>
                  <span className="text-xs text-muted-foreground/60">
                    High Confidence
                  </span>
                </div>
              </div>
            )}
          </CardContent>
        </Card>
      </div>
    </div>
  );
}
