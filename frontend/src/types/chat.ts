/**
 * Chat-specific types for the conversation interface.
 */

export type MessageRole = "user" | "assistant" | "system";
export type MessageStatus = "sending" | "streaming" | "done" | "error";

export interface MessageMeta {
  videoId?: string;
  transcriptChars?: number;
  originalChars?: number;
  language?: string;
  segments?: number;
  truncated?: boolean;
}

export interface ChatMessage {
  id: string;
  role: MessageRole;
  content: string;
  timestamp: Date;
  status?: MessageStatus;
  meta?: MessageMeta;
  error?: string;
}

export interface ChatSession {
  messages: ChatMessage[];
  isStreaming: boolean;
  currentMessageId: string | null;
}
