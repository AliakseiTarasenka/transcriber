import { API_BASE } from "@/lib/config";
import type { SummarizeRequest, SummaryEvent, TranscriptResponse } from "@/types/api";

/**
 * Fetch a raw transcript by YouTube URL or 11-char id.
 */
export async function fetchTranscript(
  videoRef: string,
  lang?: string,
  signal?: AbortSignal,
): Promise<TranscriptResponse> {
  const url = new URL(`${API_BASE}/transcript/${encodeURIComponent(videoRef)}`);
  if (lang) url.searchParams.set("lang", lang);

  const response = await fetch(url.toString(), { signal });
  if (!response.ok) {
    const detail = await safeJson(response);
    throw new Error(detail?.detail ?? `Transcript request failed (${response.status})`);
  }
  return (await response.json()) as TranscriptResponse;
}

/**
 * Stream SSE events from POST /summarize.
 *
 * We use `fetch` (not EventSource) because EventSource only supports GET and
 * cannot send a JSON body. The wire format is parsed per the SSE spec
 * (https://html.spec.whatwg.org/multipage/server-sent-events.html):
 *  - Messages are separated by a blank line (`\n\n`, `\r\n\r\n`, or `\r\r`).
 *  - Lines may end with `\n`, `\r\n`, or `\r`.
 *  - Lines starting with `:` are comments (used for keep-alive pings).
 *  - Multi-line `data:` fields are joined with `\n`.
 */
export async function* streamSummary(
  request: SummarizeRequest,
  signal?: AbortSignal,
): AsyncGenerator<SummaryEvent> {
  const response = await fetch(`${API_BASE}/summarize`, {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
      Accept: "text/event-stream",
      "Cache-Control": "no-cache",
    },
    body: JSON.stringify(request),
    signal,
  });

  if (!response.ok || !response.body) {
    const detail = await safeJson(response);
    throw new Error(detail?.detail ?? `Summarize request failed (${response.status})`);
  }

  const reader = response.body.getReader();
  const decoder = new TextDecoder("utf-8");
  let buffer = "";

  try {
    while (true) {
      const { value, done } = await reader.read();
      if (done) {
        // Flush any remaining final message that wasn't terminated by a blank line.
        if (buffer.trim().length > 0) {
          const event = parseSseMessage(buffer);
          if (event) yield event;
        }
        break;
      }

      // Normalise CRLF / lone CR to LF so a single split rule works.
      buffer += decoder.decode(value, { stream: true }).replace(/\r\n|\r/g, "\n");

      // SSE messages are separated by a blank line (now uniformly `\n\n`).
      let separatorIndex: number;
      while ((separatorIndex = buffer.indexOf("\n\n")) !== -1) {
        const rawMessage = buffer.slice(0, separatorIndex);
        buffer = buffer.slice(separatorIndex + 2);
        const event = parseSseMessage(rawMessage);
        if (event) yield event;
      }
    }
  } finally {
    reader.releaseLock();
  }
}

function parseSseMessage(raw: string): SummaryEvent | null {
  const dataLines: string[] = [];

  for (const rawLine of raw.split("\n")) {
    const line = rawLine.trimEnd();
    if (line === "" || line.startsWith(":")) {
      // Empty line or comment (e.g. ": ping" keep-alive) — ignore.
      continue;
    }
    if (line.startsWith("data:")) {
      // Per spec: strip a single leading space after the colon, if present.
      const value = line.slice(5);
      dataLines.push(value.startsWith(" ") ? value.slice(1) : value);
    }
    // Other fields (event:, id:, retry:) are intentionally ignored — the
    // payload's `type` field already drives our discriminated union.
  }

  if (dataLines.length === 0) return null;

  try {
    return JSON.parse(dataLines.join("\n")) as SummaryEvent;
  } catch (err) {
    console.warn("Failed to parse SSE data payload", err, dataLines);
    return null;
  }
}

async function safeJson(response: Response): Promise<{ detail?: string } | null> {
  try {
    return (await response.json()) as { detail?: string };
  } catch {
    return null;
  }
}
