/**
 * Shared types between frontend and backend API.
 * Mirrors `backend/app/api/schemas` and `backend/app/application/dto`.
 */

export type SummaryMode = "summary" | "bullets" | "detailed" | "qa";

export type SummaryLang = "ru" | "en" | "pl" | "auto";

export interface SummarizeRequest {
  url: string;
  mode: SummaryMode;
  lang: SummaryLang;
  prompt?: string | null;
}

export interface TranscriptSegment {
  text: string;
  start: number;
  duration: number;
}

export interface TranscriptResponse {
  video_id: string;
  language: string;
  is_generated: boolean;
  char_count: number;
  segments: TranscriptSegment[];
}

/* ---------- SSE event payloads ---------- */

export interface MetaEvent {
  type: "meta";
  chars: number;
  lang: string;
  original_chars: number;
  truncated: boolean;
  segments: number;
}

export interface TextEvent {
  type: "text";
  text: string;
}

export interface DoneEvent {
  type: "done";
}

export interface ErrorEvent {
  type: "error";
  text: string;
}

export type SummaryEvent = MetaEvent | TextEvent | DoneEvent | ErrorEvent;
