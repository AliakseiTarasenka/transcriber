"use client";

import { FormEvent, KeyboardEvent, useState, useRef, useEffect } from "react";

import { detectUserLanguage, extractYouTubeId } from "@/lib/youtube";
import type { SummaryLang, SummaryMode } from "@/types/api";

interface Props {
  onSubmit: (data: { url: string; prompt: string; mode: SummaryMode; lang: SummaryLang }) => void;
  onCancel?: () => void;
  isStreaming: boolean;
  disabled?: boolean;
}

const MODES: { value: SummaryMode; label: string; icon: string }[] = [
  { value: "summary", label: "Summary", icon: "📝" },
  { value: "bullets", label: "Bullets", icon: "•" },
  { value: "detailed", label: "Detailed", icon: "📋" },
  { value: "qa", label: "Q&A", icon: "💬" },
];

export function ChatInput({ onSubmit, onCancel, isStreaming, disabled }: Props) {
  const [input, setInput] = useState("");
  const [mode, setMode] = useState<SummaryMode>("summary");
  const [lang, setLang] = useState<SummaryLang>(() => detectUserLanguage() as SummaryLang);
  const [showSettings, setShowSettings] = useState(false);
  const textareaRef = useRef<HTMLTextAreaElement>(null);

  // Auto-focus input on mount
  useEffect(() => {
    textareaRef.current?.focus();
  }, []);

  // Auto-resize textarea
  useEffect(() => {
    if (textareaRef.current) {
      textareaRef.current.style.height = "auto";
      textareaRef.current.style.height = `${textareaRef.current.scrollHeight}px`;
    }
  }, [input]);

  const handleSubmit = (e: FormEvent) => {
    e.preventDefault();
    if (!input.trim() || disabled || isStreaming) return;

    // Extract YouTube URL from input
    const youtubeId = extractYouTubeId(input);
    if (!youtubeId) {
      alert("Please include a YouTube URL in your message");
      return;
    }

    const url = `https://www.youtube.com/watch?v=${youtubeId}`;

    // Remove URL from prompt (optional - or keep it for context)
    const promptText = input.replace(/https?:\/\/[^\s]+/g, "").trim() || "Summarize this video";

    onSubmit({ url, prompt: promptText, mode, lang });
    setInput("");

    // Reset textarea height
    if (textareaRef.current) {
      textareaRef.current.style.height = "auto";
    }
  };

  const handleKeyDown = (e: KeyboardEvent<HTMLTextAreaElement>) => {
    // Send on Enter (without Shift)
    if (e.key === "Enter" && !e.shiftKey) {
      e.preventDefault();
      handleSubmit(e as unknown as FormEvent);
    }
  };

  return (
    <div className="chat-input">
      <form onSubmit={handleSubmit} className="chat-input-form">
        {showSettings && (
          <div className="chat-settings">
            <div className="setting-group">
              <label htmlFor="chat-mode">
                Mode
                <select
                  id="chat-mode"
                  value={mode}
                  onChange={(e) => setMode(e.target.value as SummaryMode)}
                  disabled={disabled || isStreaming}
                >
                  {MODES.map((m) => (
                    <option key={m.value} value={m.value}>
                      {m.icon} {m.label}
                    </option>
                  ))}
                </select>
              </label>
            </div>
            <div className="setting-group">
              <label htmlFor="chat-lang">
                Language
                <select
                  id="chat-lang"
                  value={lang}
                  onChange={(e) => setLang(e.target.value as SummaryLang)}
                  disabled={disabled || isStreaming}
                >
                  <option value="auto">🌍 Auto</option>
                  <option value="en">🇬🇧 English</option>
                  <option value="ru">🇷🇺 Русский</option>
                  <option value="pl">🇵🇱 Polski</option>
                </select>
              </label>
            </div>
          </div>
        )}

        <div className="input-container">
          <button
            type="button"
            className="settings-button"
            onClick={() => setShowSettings(!showSettings)}
            aria-label="Toggle settings"
            disabled={disabled}
          >
            ⚙️
          </button>

          <textarea
            ref={textareaRef}
            value={input}
            onChange={(e) => setInput(e.target.value)}
            onKeyDown={handleKeyDown}
            placeholder="Paste YouTube URL and ask me anything... (Press Enter to send)"
            className="chat-textarea"
            rows={1}
            disabled={disabled || isStreaming}
            aria-label="Chat input"
          />

          {isStreaming ? (
            <button
              type="button"
              onClick={onCancel}
              className="send-button stop"
              aria-label="Stop generating"
            >
              ⏸️
            </button>
          ) : (
            <button
              type="submit"
              className="send-button"
              disabled={!input.trim() || disabled}
              aria-label="Send message"
            >
              🚀
            </button>
          )}
        </div>

        <div className="input-hint">
          <kbd>Enter</kbd> to send · <kbd>Shift + Enter</kbd> for new line ·{" "}
          {mode !== "summary" && `Mode: ${MODES.find((m) => m.value === mode)?.label} · `}
          {lang !== "auto" && `Lang: ${lang.toUpperCase()}`}
        </div>
      </form>
    </div>
  );
}
