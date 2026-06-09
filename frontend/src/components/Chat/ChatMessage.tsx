"use client";

import type { ChatMessage } from "@/types/chat";

interface Props {
  message: ChatMessage;
}

export function ChatMessageComponent({ message }: Props) {
  const isUser = message.role === "user";
  const isStreaming = message.status === "streaming";
  const hasError = message.status === "error";

  return (
    <div className={`chat-message ${isUser ? "user" : "assistant"}`}>
      <div className="message-avatar">{isUser ? "👤" : "🤖"}</div>
      <div className="message-content">
        <div className="message-header">
          <span className="message-author">{isUser ? "You" : "Assistant"}</span>
          <span className="message-time">
            {message.timestamp.toLocaleTimeString("en-US", {
              hour: "2-digit",
              minute: "2-digit",
            })}
          </span>
        </div>

        {message.meta && (
          <div className="message-meta">
            📊 {message.meta.transcriptChars?.toLocaleString()} chars · {message.meta.language} ·{" "}
            {message.meta.segments} segments
            {message.meta.truncated && " · ⚠️ truncated"}
          </div>
        )}

        <div className={`message-bubble ${isStreaming ? "streaming" : ""} ${hasError ? "error" : ""}`}>
          {hasError ? (
            <span className="error-text">⚠️ {message.error || message.content}</span>
          ) : (
            <MessageContent content={message.content} isUser={isUser} />
          )}
        </div>
      </div>
    </div>
  );
}

function MessageContent({ content, isUser }: { content: string; isUser: boolean }) {
  if (!content) return <span className="placeholder">...</span>;

  // For user messages, detect YouTube URLs and make them clickable
  if (isUser) {
    const youtubePattern = /(https?:\/\/(?:www\.)?(?:youtube\.com\/watch\?v=|youtu\.be\/)([a-zA-Z0-9_-]{11}))/g;
    const parts = content.split(youtubePattern);

    return (
      <>
        {parts.map((part, i) => {
          if (part && part.match(/^https?:\/\//)) {
            return (
              <a
                key={i}
                href={part}
                target="_blank"
                rel="noopener noreferrer"
                className="youtube-link"
              >
                🎬 {part}
              </a>
            );
          }
          return <span key={i}>{part}</span>;
        })}
      </>
    );
  }

  // For assistant messages, preserve markdown-like formatting
  return (
    <div className="message-text" style={{ whiteSpace: "pre-wrap" }}>
      {content}
    </div>
  );
}
