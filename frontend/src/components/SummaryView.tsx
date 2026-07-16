"use client";

import { useEffect, useRef, useState } from "react";

import type { SummaryState } from "@/hooks/useSummaryStream";

interface Props {
  state: SummaryState;
}

export function SummaryView({ state }: Props) {
  const { text, meta, isStreaming, error, done } = state;
  const outputRef = useRef<HTMLElement | null>(null);
  const copyTimeoutRef = useRef<number | null>(null);
  const [copyState, setCopyState] = useState<"idle" | "copied" | "failed">(
    "idle",
  );

  // Auto-scroll the output container to the bottom as new tokens arrive.
  useEffect(() => {
    if (!isStreaming) return;
    const el = outputRef.current;
    if (!el) return;
    el.scrollTop = el.scrollHeight;
  }, [text, isStreaming]);

  useEffect(() => {
    return () => {
      if (copyTimeoutRef.current) {
        window.clearTimeout(copyTimeoutRef.current);
      }
    };
  }, []);

  const copySummary = async () => {
    const summary = text.trim();
    if (!summary) return;

    try {
      if (navigator.clipboard?.writeText) {
        await navigator.clipboard.writeText(summary);
      } else {
        const textArea = document.createElement("textarea");
        textArea.value = summary;
        textArea.setAttribute("readonly", "");
        textArea.style.position = "fixed";
        textArea.style.opacity = "0";
        document.body.appendChild(textArea);
        textArea.select();
        document.execCommand("copy");
        document.body.removeChild(textArea);
      }

      setCopyState("copied");
    } catch {
      setCopyState("failed");
    }

    if (copyTimeoutRef.current) {
      window.clearTimeout(copyTimeoutRef.current);
    }
    copyTimeoutRef.current = window.setTimeout(() => {
      setCopyState("idle");
      copyTimeoutRef.current = null;
    }, 1800);
  };

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

      {error && (
        <div className="error" role="alert" aria-live="assertive">
          ⚠️ {error}
        </div>
      )}

      {(text || isStreaming) && (
        <div className="output-panel">
          <div className="output-toolbar">
            <button
              type="button"
              className="icon-button"
              onClick={copySummary}
              disabled={!text.trim()}
              aria-label={
                copyState === "failed"
                  ? "Copy failed. Try again"
                  : copyState === "copied"
                    ? "Context summary copied"
                    : "Copy context summary"
              }
              title={
                copyState === "failed"
                  ? "Copy failed"
                  : copyState === "copied"
                    ? "Copied"
                    : "Copy context summary"
              }
            >
              {copyState === "copied" ? (
                <svg
                  viewBox="0 0 24 24"
                  aria-hidden="true"
                  focusable="false"
                  className="icon"
                >
                  <path d="m9 16.2-3.5-3.5L4 14.2l5 5 11-11-1.5-1.5z" />
                </svg>
              ) : (
                <svg
                  viewBox="0 0 24 24"
                  aria-hidden="true"
                  focusable="false"
                  className="icon"
                >
                  <path d="M8 7a3 3 0 0 1 3-3h6a3 3 0 0 1 3 3v6a3 3 0 0 1-3 3h-1v1a3 3 0 0 1-3 3H7a3 3 0 0 1-3-3v-6a3 3 0 0 1 3-3h1zm3-1a1 1 0 0 0-1 1v6a1 1 0 0 0 1 1h6a1 1 0 0 0 1-1V7a1 1 0 0 0-1-1zm-3 4H7a1 1 0 0 0-1 1v6a1 1 0 0 0 1 1h6a1 1 0 0 0 1-1v-1h-3a3 3 0 0 1-3-3z" />
                </svg>
              )}
            </button>
          </div>
          <article ref={outputRef} className="output" aria-live="polite">
            {text}
            {isStreaming && <span className="cursor" aria-hidden="true" />}
          </article>
        </div>
      )}
    </section>
  );
}
