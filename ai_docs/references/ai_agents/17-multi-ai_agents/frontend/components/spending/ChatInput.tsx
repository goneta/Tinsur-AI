import { useState, useRef, KeyboardEvent } from "react";
import { Button } from "@/components/ui/button";
import { Send, Loader2 } from "lucide-react";
import { cn } from "@/lib/utils";

interface ChatInputProps {
  onSendMessage: (message: string) => void;
  disabled?: boolean;
  isLoading?: boolean;
}

export function ChatInput({
  onSendMessage,
  disabled = false,
  isLoading = false,
}: ChatInputProps) {
  const [message, setMessage] = useState("");
  const textareaRef = useRef<HTMLTextAreaElement>(null);

  const handleSend = () => {
    if (!message.trim() || disabled || isLoading) {
      return;
    }

    onSendMessage(message.trim());
    setMessage("");

    // Reset textarea height
    if (textareaRef.current) {
      textareaRef.current.style.height = "auto";
    }
  };

  const handleKeyDown = (e: KeyboardEvent<HTMLTextAreaElement>) => {
    if (e.key === "Enter") {
      if (e.shiftKey) {
        // Allow shift+enter for new lines
        return;
      } else {
        // Send message on Enter
        e.preventDefault();
        handleSend();
      }
    }
  };

  // Auto-resize textarea
  const handleInputChange = (e: React.ChangeEvent<HTMLTextAreaElement>) => {
    setMessage(e.target.value);

    // Auto-resize textarea
    const textarea = e.target;
    textarea.style.height = "auto";
    const scrollHeight = textarea.scrollHeight;
    const maxHeight = 120; // Max 5 lines approximately
    textarea.style.height = `${Math.min(scrollHeight, maxHeight)}px`;
  };

  return (
    <div className="p-4">
      <div className="flex items-end gap-2">
        <div className="flex-1 relative">
          <textarea
            ref={textareaRef}
            value={message}
            onChange={handleInputChange}
            onKeyDown={handleKeyDown}
            placeholder={
              isLoading
                ? "Waiting for response..."
                : "Ask me about your spending habits, financial insights, or recommendations..."
            }
            disabled={disabled || isLoading}
            className={cn(
              "w-full resize-none rounded-md border border-input bg-background",
              "px-3 py-2 text-sm ring-offset-background",
              "placeholder:text-muted-foreground",
              "focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring focus-visible:ring-offset-2",
              "disabled:cursor-not-allowed disabled:opacity-50",
              "min-h-[40px] max-h-[120px]"
            )}
            rows={1}
          />

          {/* Character counter for very long messages */}
          {message.length > 500 && (
            <div className="absolute right-2 bottom-1 text-xs text-muted-foreground">
              {message.length}/1000
            </div>
          )}
        </div>

        <Button
          onClick={handleSend}
          disabled={!message.trim() || disabled || isLoading}
          size="sm"
          className="h-[40px] min-w-[40px]"
        >
          {isLoading ? (
            <Loader2 className="h-4 w-4 animate-spin" />
          ) : (
            <Send className="h-4 w-4" />
          )}
        </Button>
      </div>

      {/* Help text */}
      <p className="text-xs text-muted-foreground mt-2">
        Press Enter to send, Shift+Enter for a new line
      </p>
    </div>
  );
}
