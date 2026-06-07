"use client";

import { SummarizeForm } from "@/components/SummarizeForm";
import { SummaryView } from "@/components/SummaryView";
import { useSummaryStream } from "@/hooks/useSummaryStream";

export default function HomePage() {
  const { state, start, cancel } = useSummaryStream();

  return (
    <main className="container">
      <header className="hero">
        <h1>🎬 Transcriber</h1>
        <p>YouTube transcript fetcher & AI summarizer powered by Claude.</p>
      </header>

      <section className="card">
        <SummarizeForm
          onSubmit={start}
          onCancel={cancel}
          isStreaming={state.isStreaming}
        />
      </section>

      <section className="card">
        <SummaryView state={state} />
      </section>

      <footer className="footer">
        <span>FastAPI · Next.js · Anthropic Claude · Clean Architecture</span>
      </footer>
    </main>
  );
}
