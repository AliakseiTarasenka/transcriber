"use client";

import { useEffect, useRef } from "react";

import type { SummaryState } from "@/hooks/useSummaryStream";

interface Props {
  state: SummaryState;
}

export function SummaryView({ state }: Props) {
  const { text, meta, isStreaming, error, done } = state;
  const outputRef = useRef<HTMLElement | null>(null);

  // Auto-scroll the output container to the bottom as new tokens arrive.
  useEffect(() => {
    if (!isStreaming) return;
    const el = outputRef.current;
    if (!el) return;
    el.scrollTop = el.scrollHeight;
  }, [text, isStreaming]);

  if (!text && !meta && !error && !isStreaming) {
    return (
      <div className="placeholder">
        <p>Submit a YouTube URL to get an AI-generated summary streamed live.</p>
      </div>
    );
  }

  return (
    <section className="summary">
      {meta && (
        <div className="meta">
          <span>Language: {meta.lang}</span>
          <span>Segments: {meta.segments.toLocaleString()}</span>
          <span>
            Sent to LLM: {meta.chars.toLocaleString()} /{" "}
            {meta.originalChars.toLocaleString()} chars
          </span>
          {isStreaming && <span className="badge">streaming…</span>}
          {done && <span className="badge done">done</span>}
        </div>
      )}

      {meta?.truncated && (
        <div className="warning">
          ℹ️ Transcript was truncated from{" "}
          <strong>{meta.originalChars.toLocaleString()}</strong> to{" "}
          <strong>{meta.chars.toLocaleString()}</strong> characters to fit the
          model context. Increase <code>MAX_TRANSCRIPT_CHARS</code> in the
          backend <code>.env</code> if you need the full transcript.
        </div>
      )}

      {error && <div className="error">⚠️ {error}</div>}

      {(text || isStreaming) && (
        <article ref={outputRef} className="output" aria-live="polite">
          {text}
          {isStreaming && <span className="cursor" aria-hidden="true" />}
        </article>
      )}
    </section>
  );
}
