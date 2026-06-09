"use client";

import { useEffect, useRef } from "react";

import { ChatMessageComponent } from "./ChatMessage";
import type { ChatMessage } from "@/types/chat";

interface Props {
  messages: ChatMessage[];
  isStreaming: boolean;
}

export function ChatMessages({ messages, isStreaming }: Props) {
  const messagesEndRef = useRef<HTMLDivElement>(null);
  const containerRef = useRef<HTMLDivElement>(null);

  // Auto-scroll to bottom when new messages arrive
  useEffect(() => {
    if (messagesEndRef.current) {
      messagesEndRef.current.scrollIntoView({ behavior: "smooth" });
    }
  }, [messages.length, isStreaming]);

  if (messages.length === 0) {
    return (
      <div className="chat-welcome">
        <div className="welcome-icon">🎬</div>
        <h2>Welcome to Transcriber</h2>
        <p>Your AI-powered YouTube video summarizer</p>
        <div className="welcome-features">
          <div className="feature">
            <span className="feature-icon">⚡</span>
            <span>Instant summaries</span>
          </div>
          <div className="feature">
            <span className="feature-icon">🌍</span>
            <span>Multi-language support</span>
          </div>
          <div className="feature">
            <span className="feature-icon">🤖</span>
            <span>Powered by Claude AI</span>
          </div>
        </div>
        <p className="welcome-hint">
          👇 Paste a YouTube URL below and ask me to summarize it
        </p>
      </div>
    );
  }

  return (
    <div className="chat-messages" ref={containerRef} role="log" aria-live="polite" aria-atomic="false">
      {messages.map((message) => (
        <ChatMessageComponent key={message.id} message={message} />
      ))}
      <div ref={messagesEndRef} />
    </div>
  );
}
