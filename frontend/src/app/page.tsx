"use client";

import { SummarizeForm } from "@/components/SummarizeForm";
import { SummaryView } from "@/components/SummaryView";
import { useSummaryStream } from "@/hooks/useSummaryStream";

export default function HomePage() {
  const { state, start, cancel } = useSummaryStream();

  return (
    <main id="main-content" className="container">
      <header className="hero">
        <h1>🎬 Transcriber</h1>
      </header>

      <section className="card" aria-labelledby="form-heading">
        <h2 id="form-heading" className="sr-only">Enter video details</h2>
        <SummarizeForm
          onSubmit={start}
          onCancel={cancel}
          isStreaming={state.isStreaming}
        />
      </section>

      <section className="card" aria-labelledby="output-heading">
        <h2 id="output-heading" className="sr-only">Summary output</h2>
        <SummaryView state={state} />
      </section>

      <footer className="footer">
        <span>@2026</span>
      </footer>
    </main>
  );
}
