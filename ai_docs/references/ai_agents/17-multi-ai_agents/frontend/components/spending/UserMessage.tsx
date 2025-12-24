import { ChatMessage } from "@/lib/types/chat";
import { Card, CardContent } from "@/components/ui/card";
import { User, CheckCircle } from "lucide-react";
import { cn } from "@/lib/utils";

interface UserMessageProps {
  message: ChatMessage;
}

export function UserMessage({ message }: UserMessageProps) {
  return (
    <div className="flex justify-end mb-1 animate-in slide-in-from-right-2 duration-500">
      <div className="flex items-end gap-2 max-w-[75%]">
        {/* Ultra-Compact Message Card */}
        <Card
          className={cn(
            "relative bg-gradient-to-br from-primary/95 to-primary/90 backdrop-blur-md order-2",
            "text-primary-foreground shadow-md border border-primary/30",
            "transition-all duration-200 overflow-hidden"
          )}
        >
          {/* Minimal glass effect */}
          <div className="absolute inset-0 bg-gradient-to-br from-white/8 to-transparent pointer-events-none" />

          <CardContent className="px-3 py-2 relative">
            {/* Tight message content */}
            <p className="text-sm leading-snug whitespace-pre-wrap font-medium text-primary-foreground">
              {message.content}
            </p>

            {/* Inline timestamp */}
            <div className="flex items-center justify-end gap-1 mt-1">
              <CheckCircle className="h-2.5 w-2.5 text-white/60" />
              <span className="text-xs text-white/50">
                {message.timestamp.toLocaleTimeString([], {
                  hour: "2-digit",
                  minute: "2-digit",
                })}
              </span>
            </div>
          </CardContent>
        </Card>

        {/* Tiny User Avatar */}
        <div className="flex-shrink-0 relative order-1 mb-0.5">
          <div
            className={cn(
              "relative w-7 h-7 rounded-lg flex items-center justify-center shadow-sm transition-all duration-200",
              "bg-gradient-to-br from-primary/90 to-primary/80",
              "border border-primary/30"
            )}
          >
            {/* User icon */}
            <User className="h-3.5 w-3.5 text-primary-foreground" />
          </div>

          {/* Tiny status indicator */}
          <div className="absolute -bottom-0.5 -right-0.5 w-2.5 h-2.5 bg-green-400 rounded-full border border-background" />
        </div>
      </div>
    </div>
  );
}
