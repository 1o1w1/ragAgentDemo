import { useEffect, useRef } from "react";
import type { ChatMessage } from "../../types";
import { StreamingMessage } from "./StreamingMessage";

interface Props {
  messages: ChatMessage[];
  streamingMessage?: string;
}

export function MessageList({ messages, streamingMessage }: Props) {
  const endRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    endRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [messages, streamingMessage]);

  if (messages.length === 0) {
    return (
      <div style={{ flex: 1, display: "flex", alignItems: "center", justifyContent: "center", color: "#9ca3af" }}>
        <p>Ask a question to get started</p>
      </div>
    );
  }

  return (
    <div style={{ flex: 1, overflowY: "auto", padding: 16 }}>
      {messages.map((msg, i) => (
        <div
          key={i}
          style={{
            display: "flex",
            justifyContent: msg.role === "user" ? "flex-end" : "flex-start",
            marginBottom: 12,
          }}
        >
          <div
            style={{
              maxWidth: "75%",
              padding: "10px 14px",
              borderRadius: 12,
              background: msg.role === "user" ? "#3b82f6" : "#f3f4f6",
              color: msg.role === "user" ? "white" : "#111827",
            }}
          >
            <div style={{ whiteSpace: "pre-wrap" }}>{msg.content}</div>
            {msg.citations && msg.citations.length > 0 && (
              <div style={{ marginTop: 8, paddingTop: 8, borderTop: "1px solid #e5e7eb", fontSize: 13 }}>
                <div style={{ fontWeight: 600, marginBottom: 4 }}>引用</div>
                {msg.citations.map((c, j) => (
                  <div key={j} style={{ marginBottom: 4, color: "#6b7280" }}>
                    <span style={{ fontWeight: 500 }}>{c.source}</span>
                    {c.score !== undefined && <span> (score: {c.score.toFixed(2)})</span>}
                    <div style={{ fontSize: 12, marginTop: 2 }}>{c.content.slice(0, 100)}...</div>
                  </div>
                ))}
              </div>
            )}
          </div>
        </div>
      ))}
      {streamingMessage && (
        <StreamingMessage content={streamingMessage} />
      )}
      <div ref={endRef} />
    </div>
  );
}
