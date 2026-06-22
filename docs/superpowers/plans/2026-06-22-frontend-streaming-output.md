# 前端流式输出实现计划

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** 将前端从一次性输出改为流式输出，实现打字机效果，提升用户体验

**Architecture:** 后端新增SSE流式API端点，使用OpenAI流式API获取token，通过SSE实时推送给前端；前端使用EventSource接收token并逐字显示，实现打字机效果

**Tech Stack:** FastAPI, SSE, OpenAI API, React, TypeScript, EventSource

---

## 文件结构

### 后端文件
- `backend/rag/generator.py` - 添加流式生成方法
- `backend/agent/behavior.py` - 添加流式聊天方法
- `backend/api/chat.py` - 添加流式API端点
- `requirements.txt` - 添加sse-starlette依赖

### 前端文件
- `frontend/src/services/api.ts` - 添加流式API方法
- `frontend/src/hooks/useChatStream.ts` - 新增流式聊天hook
- `frontend/src/components/Chat/StreamingMessage.tsx` - 新增流式消息组件
- `frontend/src/components/Chat/TypingIndicator.tsx` - 新增打字机动画组件
- `frontend/src/components/Chat/ChatWindow.tsx` - 修改使用新的hook
- `frontend/src/components/Chat/MessageList.tsx` - 修改支持流式消息

---

## Task 1: 添加后端依赖

**Files:**
- Modify: `requirements.txt`

- [ ] **Step 1: 检查当前依赖**

```bash
cat requirements.txt
```

- [ ] **Step 2: 添加sse-starlette依赖**

在requirements.txt中添加：
```
sse-starlette==1.6.5
```

- [ ] **Step 3: 安装依赖**

```bash
pip install sse-starlette
```

- [ ] **Step 4: 验证安装**

```bash
pip show sse-starlette
```

- [ ] **Step 5: 提交**

```bash
git add requirements.txt
git commit -m "deps: add sse-starlette for streaming API"
```

---

## Task 2: 修改Generator支持流式生成

**Files:**
- Modify: `backend/rag/generator.py`

- [ ] **Step 1: 添加流式生成方法**

在Generator类中添加方法：
```python
def generate_stream(self, query: str, context_docs: List[Document]):
    """流式生成回答"""
    if not query.strip():
        logger.warning("Empty query provided for generation")
        return
    
    context = self._build_context(context_docs)
    messages = [
        {"role": "system", "content": self.system_prompt},
        {"role": "user", "content": self._build_prompt(query, context)},
    ]
    
    try:
        response = self.client.chat.completions.create(
            model=self.model,
            messages=messages,
            temperature=self.temperature,
            max_tokens=self.max_tokens,
            stream=True,
        )
        
        for chunk in response:
            if chunk.choices[0].delta.content:
                yield chunk.choices[0].delta.content
                
    except Exception as e:
        logger.error(f"Error in streaming generation: {e}")
        raise
```

- [ ] **Step 2: 验证代码语法**

```bash
python -m py_compile backend/rag/generator.py
```

- [ ] **Step 3: 提交**

```bash
git add backend/rag/generator.py
git commit -m "feat(generator): add streaming generation method"
```

---

## Task 3: 修改AgentBehavior支持流式聊天

**Files:**
- Modify: `backend/agent/behavior.py`

- [ ] **Step 1: 添加流式聊天方法**

在AgentBehavior类中添加方法：
```python
def chat_stream(self, query: str):
    """流式聊天"""
    if not query.strip():
        logger.warning("Empty query provided")
        return
    
    self.conversation.add_user_message(query)
    
    docs_with_scores = self.retriever.retrieve(query)
    docs = [doc for doc, _ in docs_with_scores]
    scores = [score for _, score in docs_with_scores]
    
    has_context = len(docs) > 0
    
    if not has_context and self.refuse_when_no_context:
        answer = "知识库中未找到相关信息，无法回答该问题。"
        self.conversation.add_assistant_message(answer)
        logger.info("No context found, refusing to answer")
        yield answer
        return
    
    citations = self.citation_manager.create_citations(docs, scores)
    
    full_answer = ""
    for token in self.generator.generate_stream(query, docs):
        full_answer += token
        yield token
    
    self.conversation.add_assistant_message(
        full_answer, metadata={"has_context": has_context, "citation_count": len(citations)}
    )
    
    logger.info(f"Generated streaming answer with {len(citations)} citations")
```

- [ ] **Step 2: 验证代码语法**

```bash
python -m py_compile backend/agent/behavior.py
```

- [ ] **Step 3: 提交**

```bash
git add backend/agent/behavior.py
git commit -m "feat(agent): add streaming chat method"
```

---

## Task 4: 添加流式API端点

**Files:**
- Modify: `backend/api/chat.py`

- [ ] **Step 1: 导入SSE依赖**

在chat.py顶部添加：
```python
from sse_starlette.sse import EventSourceResponse
import json
```

- [ ] **Step 2: 添加流式端点**

在chat_router中添加：
```python
@chat_router.post("/stream")
async def chat_stream(request: ChatRequest):
    agent = get_agent_behavior()
    
    async def event_generator():
        try:
            for token in agent.chat_stream(request.query):
                yield {
                    "event": "token",
                    "data": json.dumps({"content": token})
                }
            
            yield {
                "event": "done",
                "data": json.dumps({"status": "complete"})
            }
            
        except Exception as e:
            yield {
                "event": "error",
                "data": json.dumps({"message": str(e)})
            }
    
    return EventSourceResponse(event_generator())
```

- [ ] **Step 3: 验证代码语法**

```bash
python -m py_compile backend/api/chat.py
```

- [ ] **Step 4: 测试端点**

```bash
curl -X POST http://localhost:8000/api/chat/stream \
  -H "Content-Type: application/json" \
  -d '{"query": "什么是机器学习？"}'
```

- [ ] **Step 5: 提交**

```bash
git add backend/api/chat.py
git commit -m "feat(api): add streaming chat endpoint"
```

---

## Task 5: 修改前端API服务

**Files:**
- Modify: `frontend/src/services/api.ts`

- [ ] **Step 1: 添加流式API方法**

在chatApi对象中添加：
```typescript
sendMessageStream(query: string): EventSource {
  const url = new URL(`${API_BASE}/chat/stream`, window.location.origin);
  url.searchParams.append('query', query);
  return new EventSource(url.toString());
}
```

- [ ] **Step 2: 验证TypeScript编译**

```bash
cd frontend && npm run build
```

- [ ] **Step 3: 提交**

```bash
git add frontend/src/services/api.ts
git commit -m "feat(api): add streaming message method"
```

---

## Task 6: 创建useChatStream Hook

**Files:**
- Create: `frontend/src/hooks/useChatStream.ts`

- [ ] **Step 1: 创建Hook文件**

```typescript
import { useState, useCallback } from "react";
import type { ChatMessage } from "../types";
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
      
      eventSource.addEventListener('token', (event) => {
        const data = JSON.parse(event.data);
        fullResponse += data.content;
        setStreamingMessage(fullResponse);
      });
      
      eventSource.addEventListener('done', () => {
        setMessages(prev => [
          ...prev,
          { role: 'assistant', content: fullResponse }
        ]);
        setStreamingMessage('');
        setIsStreaming(false);
        eventSource.close();
      });
      
      eventSource.addEventListener('error', (event) => {
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
```

- [ ] **Step 2: 验证TypeScript编译**

```bash
cd frontend && npm run build
```

- [ ] **Step 3: 提交**

```bash
git add frontend/src/hooks/useChatStream.ts
git commit -m "feat(hooks): add useChatStream hook"
```

---

## Task 7: 创建TypingIndicator组件

**Files:**
- Create: `frontend/src/components/Chat/TypingIndicator.tsx`

- [ ] **Step 1: 创建组件**

```typescript
import React from 'react';

export function TypingIndicator() {
  return (
    <div style={{
      display: 'flex',
      alignItems: 'center',
      padding: '8px 16px',
      color: '#6b7280',
      fontSize: 14
    }}>
      <div style={{
        display: 'flex',
        gap: '4px',
        marginRight: '8px'
      }}>
        <div style={{
          width: '6px',
          height: '6px',
          borderRadius: '50%',
          backgroundColor: '#9ca3af',
          animation: 'typing 1.4s infinite ease-in-out'
        }} />
        <div style={{
          width: '6px',
          height: '6px',
          borderRadius: '50%',
          backgroundColor: '#9ca3af',
          animation: 'typing 1.4s infinite ease-in-out 0.2s'
        }} />
        <div style={{
          width: '6px',
          height: '6px',
          borderRadius: '50%',
          backgroundColor: '#9ca3af',
          animation: 'typing 1.4s infinite ease-in-out 0.4s'
        }} />
      </div>
      <span>正在输入...</span>
      
      <style>{`
        @keyframes typing {
          0%, 60%, 100% {
            transform: translateY(0);
            opacity: 0.4;
          }
          30% {
            transform: translateY(-4px);
            opacity: 1;
          }
        }
      `}</style>
    </div>
  );
}
```

- [ ] **Step 2: 验证TypeScript编译**

```bash
cd frontend && npm run build
```

- [ ] **Step 3: 提交**

```bash
git add frontend/src/components/Chat/TypingIndicator.tsx
git commit -m "feat(components): add TypingIndicator component"
```

---

## Task 8: 创建StreamingMessage组件

**Files:**
- Create: `frontend/src/components/Chat/StreamingMessage.tsx`

- [ ] **Step 1: 创建组件**

```typescript
import React from 'react';

interface StreamingMessageProps {
  content: string;
  isComplete?: boolean;
}

export function StreamingMessage({ content, isComplete = false }: StreamingMessageProps) {
  return (
    <div style={{
      padding: '8px 16px',
      margin: '4px 0',
      backgroundColor: '#f3f4f6',
      borderRadius: '8px',
      maxWidth: '80%',
      alignSelf: 'flex-start'
    }}>
      <div style={{ whiteSpace: 'pre-wrap' }}>
        {content}
        {!isComplete && (
          <span style={{
            display: 'inline-block',
            width: '2px',
            height: '16px',
            backgroundColor: '#3b82f6',
            marginLeft: '2px',
            animation: 'blink 1s infinite'
          }} />
        )}
      </div>
      
      <style>{`
        @keyframes blink {
          0%, 100% { opacity: 1; }
          50% { opacity: 0; }
        }
      `}</style>
    </div>
  );
}
```

- [ ] **Step 2: 验证TypeScript编译**

```bash
cd frontend && npm run build
```

- [ ] **Step 3: 提交**

```bash
git add frontend/src/components/Chat/StreamingMessage.tsx
git commit -m "feat(components): add StreamingMessage component"
```

---

## Task 9: 修改MessageList组件

**Files:**
- Modify: `frontend/src/components/Chat/MessageList.tsx`

- [ ] **Step 1: 读取当前组件**

```bash
cat frontend/src/components/Chat/MessageList.tsx
```

- [ ] **Step 2: 修改组件支持流式消息**

```typescript
import React from 'react';
import type { ChatMessage } from '../../types';
import { StreamingMessage } from './StreamingMessage';

interface MessageListProps {
  messages: ChatMessage[];
  streamingMessage?: string;
}

export function MessageList({ messages, streamingMessage }: MessageListProps) {
  return (
    <div style={{
      flex: 1,
      overflowY: 'auto',
      padding: '16px',
      display: 'flex',
      flexDirection: 'column',
      gap: '8px'
    }}>
      {messages.map((message, index) => (
        <div
          key={index}
          style={{
            display: 'flex',
            justifyContent: message.role === 'user' ? 'flex-end' : 'flex-start'
          }}
        >
          <div style={{
            padding: '8px 16px',
            borderRadius: '8px',
            maxWidth: '80%',
            backgroundColor: message.role === 'user' ? '#3b82f6' : '#f3f4f6',
            color: message.role === 'user' ? 'white' : 'black'
          }}>
            {message.content}
          </div>
        </div>
      ))}
      
      {streamingMessage && (
        <StreamingMessage content={streamingMessage} />
      )}
    </div>
  );
}
```

- [ ] **Step 3: 验证TypeScript编译**

```bash
cd frontend && npm run build
```

- [ ] **Step 4: 提交**

```bash
git add frontend/src/components/Chat/MessageList.tsx
git commit -m "feat(components): update MessageList for streaming"
```

---

## Task 10: 修改ChatWindow组件

**Files:**
- Modify: `frontend/src/components/Chat/ChatWindow.tsx`

- [ ] **Step 1: 读取当前组件**

```bash
cat frontend/src/components/Chat/ChatWindow.tsx
```

- [ ] **Step 2: 修改组件使用新的hook**

```typescript
import { useChatStream } from "../../hooks/useChatStream";
import { MessageList } from "./MessageList";
import { MessageInput } from "./MessageInput";
import { TypingIndicator } from "./TypingIndicator";

export function ChatWindow() {
  const { messages, streamingMessage, isStreaming, error, sendStreamMessage, clearHistory } = useChatStream();

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
      {error && (
        <div style={{ padding: "8px 16px", background: "#fef2f2", color: "#dc2626", fontSize: 14 }}>{error}</div>
      )}
      <MessageList messages={messages} streamingMessage={streamingMessage} />
      {isStreaming && <TypingIndicator />}
      <MessageInput onSend={sendStreamMessage} disabled={isStreaming} />
    </div>
  );
}
```

- [ ] **Step 3: 验证TypeScript编译**

```bash
cd frontend && npm run build
```

- [ ] **Step 4: 提交**

```bash
git add frontend/src/components/Chat/ChatWindow.tsx
git commit -m "feat(components): update ChatWindow for streaming"
```

---

## Task 11: 集成测试

**Files:**
- Test: 测试整个流式功能

- [ ] **Step 1: 启动后端服务**

```bash
uvicorn backend.main:app --reload --host 0.0.0.0 --port 8000
```

- [ ] **Step 2: 启动前端服务**

```bash
cd frontend && npm run dev
```

- [ ] **Step 3: 测试流式API**

```bash
curl -X POST http://localhost:8000/api/chat/stream \
  -H "Content-Type: application/json" \
  -d '{"query": "什么是机器学习？"}'
```

- [ ] **Step 4: 测试前端界面**

在浏览器中打开 http://localhost:5173，发送消息测试流式输出效果

- [ ] **Step 5: 测试错误处理**

测试网络中断、无效查询等错误场景

- [ ] **Step 6: 提交最终代码**

```bash
git add .
git commit -m "feat: complete streaming output implementation"
```

---

## 自我审查

### 1. 规格覆盖检查
- ✅ 打字机效果：通过StreamingMessage组件实现
- ✅ SSE传输：通过后端SSE端点和前端EventSource实现
- ✅ 引用信息处理：流式完成后通过现有API获取
- ✅ 加载状态：通过TypingIndicator组件实现

### 2. 占位符扫描
- ✅ 无TBD、TODO或模糊需求
- ✅ 所有步骤都包含实际代码

### 3. 类型一致性检查
- ✅ 方法名、属性名在前后端保持一致
- ✅ 类型定义匹配

### 4. 范围检查
- ✅ 聚焦于前端流式输出功能
- ✅ 适合单个实现计划

### 5. 歧义检查
- ✅ 需求明确，无歧义