"use client";

import { useCallback, useEffect, useRef, useState } from "react";

import { streamSummary } from "@/services/transcriberApi";
import type { SummarizeRequest } from "@/types/api";

export interface SummaryMeta {
  chars: number;
  lang: string;
  originalChars: number;
  truncated: boolean;
  segments: number;
}

export interface SummaryState {
  text: string;
  meta: SummaryMeta | null;
  isStreaming: boolean;
  error: string | null;
  done: boolean;
}

const initialState: SummaryState = {
  text: "",
  meta: null,
  isStreaming: false,
  error: null,
  done: false,
};

/**
 * React hook that manages a streaming summary request lifecycle.
 *
 * Token chunks arrive at high frequency (~50/s) — calling `setState` per chunk
 * causes excessive re-renders. We batch incoming text into a ref and flush it
 * to React state once per animation frame for smooth, jank-free rendering.
 */
export function useSummaryStream() {
  const [state, setState] = useState<SummaryState>(initialState);

  const abortRef = useRef<AbortController | null>(null);
  const pendingTextRef = useRef<string>("");
  const rafRef = useRef<number | null>(null);

  const flushPendingText = useCallback(() => {
    rafRef.current = null;
    const pending = pendingTextRef.current;
    if (!pending) return;
    pendingTextRef.current = "";
    setState((prev) => ({ ...prev, text: prev.text + pending }));
  }, []);

  const scheduleFlush = useCallback(() => {
    if (rafRef.current !== null) return;
    if (typeof window === "undefined") {
      // SSR safety — should not happen because hook is client-only.
      flushPendingText();
      return;
    }
    rafRef.current = window.requestAnimationFrame(flushPendingText);
  }, [flushPendingText]);

  const cancelScheduledFlush = useCallback(() => {
    if (rafRef.current !== null && typeof window !== "undefined") {
      window.cancelAnimationFrame(rafRef.current);
      rafRef.current = null;
    }
  }, []);

  const cancel = useCallback(() => {
    abortRef.current?.abort();
    abortRef.current = null;
    cancelScheduledFlush();
    pendingTextRef.current = "";
    setState((prev) => ({ ...prev, isStreaming: false }));
  }, [cancelScheduledFlush]);

  const start = useCallback(
    async (request: SummarizeRequest) => {
      // Reset any previous run.
      abortRef.current?.abort();
      cancelScheduledFlush();
      pendingTextRef.current = "";

      const controller = new AbortController();
      abortRef.current = controller;

      setState({ ...initialState, isStreaming: true });

      try {
        for await (const event of streamSummary(request, controller.signal)) {
          switch (event.type) {
            case "meta":
              setState((prev) => ({
                ...prev,
                meta: {
                  chars: event.chars,
                  lang: event.lang,
                  originalChars: event.original_chars,
                  truncated: event.truncated,
                  segments: event.segments,
                },
              }));
              break;
            case "text":
              // Coalesce: accumulate in a ref, flush once per frame.
              pendingTextRef.current += event.text;
              scheduleFlush();
              break;
            case "done":
              cancelScheduledFlush();
              flushPendingText();
              setState((prev) => ({ ...prev, isStreaming: false, done: true }));
              break;
            case "error":
              cancelScheduledFlush();
              flushPendingText();
              setState((prev) => ({
                ...prev,
                isStreaming: false,
                error: event.text,
              }));
              break;
          }
        }
        // Stream ended without explicit `done` — flush trailing text.
        cancelScheduledFlush();
        flushPendingText();
        setState((prev) =>
          prev.isStreaming ? { ...prev, isStreaming: false, done: true } : prev,
        );
      } catch (err) {
        if ((err as Error).name === "AbortError") return;
        cancelScheduledFlush();
        flushPendingText();
        setState((prev) => ({
          ...prev,
          isStreaming: false,
          error: (err as Error).message,
        }));
      } finally {
        abortRef.current = null;
      }
    },
    [cancelScheduledFlush, flushPendingText, scheduleFlush],
  );

  const reset = useCallback(() => {
    cancelScheduledFlush();
    pendingTextRef.current = "";
    setState(initialState);
  }, [cancelScheduledFlush]);

  // Cleanup on unmount.
  useEffect(() => {
    return () => {
      abortRef.current?.abort();
      if (rafRef.current !== null && typeof window !== "undefined") {
        window.cancelAnimationFrame(rafRef.current);
      }
    };
  }, []);

  return { state, start, cancel, reset };
}
