import { useState, useEffect } from "react";
import { useChatStream } from "../../hooks/useChatStream";
import { MessageList } from "./MessageList";
import { MessageInput } from "./MessageInput";
import { TypingIndicator } from "./TypingIndicator";
import { statusApi, ServerStatus } from "../../services/api";

export function ChatWindow() {
  const { messages, streamingMessage, isStreaming, error, sendStreamMessage, clearHistory } = useChatStream();
  const [serverStatus, setServerStatus] = useState<ServerStatus>({
    status: "loading",
    is_loading: true,
    loading_message: "Server is starting...",
  });

  useEffect(() => {
    let timer: ReturnType<typeof setInterval>;

    const checkStatus = async () => {
      try {
        const status = await statusApi.getHealth();
        setServerStatus(status);
        if (!status.is_loading) {
          clearInterval(timer);
        }
      } catch {
        // Server not ready, keep current loading state
      }
    };

    timer = setInterval(checkStatus, 2000);

    return () => clearInterval(timer);
  }, []);

  return (
    <div style={{ display: "flex", flexDirection: "column", height: "100%", background: "white" }}>
      <div
        style={{
          display: "flex",
          justifyContent: "space-between",
          alignItems: "center",
          padding: "12px 16px",
          borderBottom: "1px solid #e5e7eb",
        }}
      >
        <h2 style={{ margin: 0, fontSize: 18 }}>RAG Knowledge Base</h2>
        <button
          onClick={clearHistory}
          style={{
            padding: "6px 12px",
            background: "#ef4444",
            color: "white",
            border: "none",
            borderRadius: 6,
            cursor: "pointer",
            fontSize: 13,
          }}
        >
          Clear History
        </button>
      </div>
      {serverStatus.is_loading && (
        <div
          style={{
            padding: "10px 16px",
            background: "#fef3c7",
            color: "#92400e",
            fontSize: 14,
            display: "flex",
            alignItems: "center",
            gap: 8,
          }}
        >
          <span style={{ animation: "spin 1s linear infinite" }}>⏳</span>
          {serverStatus.loading_message || "Server is loading, please wait..."}
        </div>
      )}
      {error && (
        <div style={{ padding: "8px 16px", background: "#fef2f2", color: "#dc2626", fontSize: 14 }}>{error}</div>
      )}
      <MessageList messages={messages} streamingMessage={streamingMessage} />
      {isStreaming && <TypingIndicator />}
      <MessageInput onSend={sendStreamMessage} disabled={isStreaming || serverStatus.is_loading} />
    </div>
  );
}
