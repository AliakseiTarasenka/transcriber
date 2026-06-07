"use client";

import { FormEvent, useState } from "react";

import type { SummarizeRequest, SummaryLang, SummaryMode } from "@/types/api";

interface Props {
  disabled?: boolean;
  onSubmit: (request: SummarizeRequest) => void;
  onCancel?: () => void;
  isStreaming?: boolean;
}

const MODES: { value: SummaryMode; label: string }[] = [
  { value: "summary", label: "Summary" },
  { value: "bullets", label: "Bullets" },
  { value: "detailed", label: "Detailed" },
  { value: "qa", label: "Q&A" },
];

const LANGS: { value: SummaryLang; label: string }[] = [
  { value: "ru", label: "Русский" },
  { value: "en", label: "English" },
  { value: "pl", label: "Polski" },
  { value: "auto", label: "Auto" },
];

export function SummarizeForm({ disabled, onSubmit, onCancel, isStreaming }: Props) {
  const [url, setUrl] = useState("");
  const [mode, setMode] = useState<SummaryMode>("summary");
  const [lang, setLang] = useState<SummaryLang>("ru");
  const [prompt, setPrompt] = useState("");

  const handleSubmit = (event: FormEvent<HTMLFormElement>) => {
    event.preventDefault();
    if (!url.trim()) return;
    onSubmit({
      url: url.trim(),
      mode,
      lang,
      prompt: prompt.trim() ? prompt.trim() : null,
    });
  };

  return (
    <form className="form" onSubmit={handleSubmit}>
      <label className="field">
        <span>YouTube URL</span>
        <input
          type="url"
          required
          placeholder="https://www.youtube.com/watch?v=..."
          value={url}
          onChange={(e) => setUrl(e.target.value)}
          disabled={disabled}
        />
      </label>

      <div className="row">
        <label className="field">
          <span>Mode</span>
          <select
            value={mode}
            onChange={(e) => setMode(e.target.value as SummaryMode)}
            disabled={disabled}
          >
            {MODES.map((m) => (
              <option key={m.value} value={m.value}>
                {m.label}
              </option>
            ))}
          </select>
        </label>

        <label className="field">
          <span>Language</span>
          <select
            value={lang}
            onChange={(e) => setLang(e.target.value as SummaryLang)}
            disabled={disabled}
          >
            {LANGS.map((l) => (
              <option key={l.value} value={l.value}>
                {l.label}
              </option>
            ))}
          </select>
        </label>
      </div>

      <label className="field">
        <span>Custom prompt (optional)</span>
        <textarea
          rows={3}
          placeholder="e.g. Focus on technical details, list mentioned tools..."
          value={prompt}
          onChange={(e) => setPrompt(e.target.value)}
          disabled={disabled}
          maxLength={2000}
        />
      </label>

      <div className="actions">
        <button type="submit" disabled={disabled || isStreaming}>
          {isStreaming ? "Streaming..." : "Summarize"}
        </button>
        {isStreaming && onCancel && (
          <button type="button" className="secondary" onClick={onCancel}>
            Cancel
          </button>
        )}
      </div>
    </form>
  );
}
