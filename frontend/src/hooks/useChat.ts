import { useState, useCallback } from "react";
import type { ChatMessage } from "../types";
import { chatApi } from "../services/api";

export function useChat() {
  const [messages, setMessages] = useState<ChatMessage[]>([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const sendMessage = useCallback(async (query: string) => {
    setError(null);
    setMessages((prev) => [...prev, { role: "user", content: query }]);
    setLoading(true);

    try {
      const response = await chatApi.sendMessage(query);
      setMessages((prev) => [
        ...prev,
        {
          role: "assistant",
          content: response.answer,
          citations: response.citations,
          has_context: response.has_context,
        },
      ]);
    } catch (err) {
      setError(err instanceof Error ? err.message : "Failed to send message");
    } finally {
      setLoading(false);
    }
  }, []);

  const clearHistory = useCallback(async () => {
    try {
      await chatApi.clearHistory();
      setMessages([]);
      setError(null);
    } catch (err) {
      setError(err instanceof Error ? err.message : "Failed to clear history");
    }
  }, []);

  return { messages, loading, error, sendMessage, clearHistory };
}
