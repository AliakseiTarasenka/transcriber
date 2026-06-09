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
      <label htmlFor="youtube-url" className="field">
        <span>YouTube URL</span>
        <input
          id="youtube-url"
          type="url"
          required
          placeholder="https://www.youtube.com/watch?v=..."
          value={url}
          onChange={(e) => setUrl(e.target.value)}
          disabled={disabled}
          aria-describedby="url-help"
        />
      </label>

      <fieldset className="field-group">
        <legend className="sr-only">Summary options</legend>
        <div className="row">
          <label htmlFor="summary-mode" className="field">
            <span>Mode</span>
            <select
              id="summary-mode"
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

          <label htmlFor="summary-lang" className="field">
            <span>Language</span>
            <select
              id="summary-lang"
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
      </fieldset>

      <label htmlFor="custom-prompt" className="field">
        <span>Custom prompt (optional)</span>
        <textarea
          id="custom-prompt"
          rows={3}
          placeholder="e.g. Focus on technical details, list mentioned tools..."
          value={prompt}
          onChange={(e) => setPrompt(e.target.value)}
          disabled={disabled}
          maxLength={2000}
          aria-describedby="prompt-help"
        />
      </label>

      <div className="actions">
        <button
          type="submit"
          disabled={disabled || isStreaming}
          aria-busy={isStreaming}
          aria-label={isStreaming ? "Streaming summary in progress" : "Start summarizing video"}
        >
          {isStreaming ? "Streaming..." : "Summarize"}
        </button>
        {isStreaming && onCancel && (
          <button
            type="button"
            className="secondary"
            onClick={onCancel}
            aria-label="Cancel summary streaming"
          >
            Cancel
          </button>
        )}
      </div>
    </form>
  );
}
