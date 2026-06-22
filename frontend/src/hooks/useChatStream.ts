import { useState, useCallback } from "react";
import type { ChatMessage, Citation } from "../types";
import { chatApi } from "../services/api";

export function useChatStream() {
  const [messages, setMessages] = useState<ChatMessage[]>([]);
  const [streamingMessage, setStreamingMessage] = useState<string>('');
  const [isStreaming, setIsStreaming] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const sendStreamMessage = useCallback(async (query: string) => {
    setIsStreaming(true);
    setError(null);
    setStreamingMessage('');
    
    setMessages(prev => [...prev, { role: 'user', content: query }]);
    
    try {
      const eventSource = chatApi.sendMessageStream(query);
      let fullResponse = '';
      let citations: Citation[] = [];
      let hasContext = false;
      
      eventSource.addEventListener('token', (event: MessageEvent) => {
        const data = JSON.parse(event.data);
        fullResponse += data.content;
        setStreamingMessage(fullResponse);
      });

      eventSource.addEventListener('reasoning', () => {});
      
      eventSource.addEventListener('citations', (event: MessageEvent) => {
        const data = JSON.parse(event.data);
        citations = data.citations;
        hasContext = data.has_context;
      });
      
      eventSource.addEventListener('done', () => {
        setMessages(prev => [
          ...prev,
          { 
            role: 'assistant', 
            content: fullResponse,
            citations: citations.length > 0 ? citations : undefined,
            has_context: hasContext,
          }
        ]);
        setStreamingMessage('');
        setIsStreaming(false);
        eventSource.close();
      });
      
      eventSource.addEventListener('error', (event: MessageEvent) => {
        const data = JSON.parse(event.data);
        setError(data.message);
        setIsStreaming(false);
        eventSource.close();
      });
      
      eventSource.onerror = () => {
        setError('连接中断，请重试');
        setIsStreaming(false);
        eventSource.close();
      };
    } catch (err) {
      setError(err instanceof Error ? err.message : '发送消息失败');
      setIsStreaming(false);
    }
  }, []);

  const clearHistory = useCallback(async () => {
    try {
      await chatApi.clearHistory();
      setMessages([]);
      setError(null);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to clear history');
    }
  }, []);

  return { messages, streamingMessage, isStreaming, error, sendStreamMessage, clearHistory };
}
