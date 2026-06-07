import type { Metadata } from "next";

import "./globals.css";

export const metadata: Metadata = {
  title: "Transcriber — YouTube AI Summarizer",
  description: "Get AI-generated summaries of YouTube videos via Claude.",
};

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html lang="en">
      <body>{children}</body>
    </html>
  );
}
