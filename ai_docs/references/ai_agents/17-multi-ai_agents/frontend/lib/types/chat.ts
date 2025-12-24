export interface ChatMessage {
  id: string;
  type: "user" | "agent";
  content: string;
  timestamp: Date;
}

export interface ChatState {
  messages: ChatMessage[];
  isLoading: boolean;
  error: string | null;
  sessionId: string | null;
}

export interface SSEEvent {
  type: "session" | "content" | "complete" | "error";
  sessionId?: string;
  text?: string;
  timestamp?: number;
  error?: string;
}
