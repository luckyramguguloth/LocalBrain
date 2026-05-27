import type { Metadata } from "next";
import "./globals.css";

export const metadata: Metadata = {
  title: "Local Brain — Private AI Knowledge Engine",
  description:
    "Local Brain is a self-hosted, on-premise AI platform that turns your documents into a private, searchable knowledge base powered by a local LLM. No cloud. No subscriptions. 100% private.",
  keywords: ["on-premise AI", "private LLM", "knowledge base", "RAG", "Ollama", "document search"],
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html lang="en">
      <body>{children}</body>
    </html>
  );
}
