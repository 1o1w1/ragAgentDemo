# Streaming Output Fix Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Fix the streaming output issue where all content appears at once instead of incrementally

**Architecture:** Modify httpx client configuration in the Generator class to disable buffering and optimize for Ollama's streaming API

**Tech Stack:** Python, httpx, OpenAI Python client, Ollama

---

## File Structure

**Files to modify:**
- `backend/rag/generator.py` - Update httpx client configuration in `__init__` and `update_config` methods

---

### Task 1: Update httpx client configuration in Generator.__init__

**Files:**
- Modify: `backend/rag/generator.py:30-36`

- [ ] **Step 1: Read current implementation**

Read `backend/rag/generator.py` to understand the current httpx client configuration.

- [ ] **Step 2: Update httpx transport configuration**

Modify the `__init__` method to add `verify=False` to the HTTPTransport:

```python
transport = httpx.HTTPTransport(
    http1=True, 
    http2=False,
    verify=False,  # Support HTTP connections for local Ollama
)
```

- [ ] **Step 3: Update httpx client configuration**

Modify the httpx.Client initialization to add connect timeout and Accept header:

```python
http_client = httpx.Client(
    transport=transport, 
    timeout=httpx.Timeout(60.0, connect=10.0),
    headers={"Accept": "text/event-stream"}
)
```

- [ ] **Step 4: Verify the changes**

Run a quick test to ensure the code is syntactically correct:
```bash
cd /Users/tyrael/Desktop/temp/agentDemo
python -c "from backend.rag.generator import Generator; print('Import successful')"
```

- [ ] **Step 5: Commit**

```bash
git add backend/rag/generator.py
git commit -m "fix: update httpx client config for Ollama streaming support"
```

---

### Task 2: Update httpx client configuration in Generator.update_config

**Files:**
- Modify: `backend/rag/generator.py:128-135`

- [ ] **Step 1: Read current update_config implementation**

Read the `update_config` method to see the current httpx client recreation logic.

- [ ] **Step 2: Update httpx transport in update_config**

Modify the `update_config` method to use the same updated transport configuration:

```python
transport = httpx.HTTPTransport(
    http1=True, 
    http2=False,
    verify=False,
)
http_client = httpx.Client(
    transport=transport,
    timeout=httpx.Timeout(60.0, connect=10.0),
    headers={"Accept": "text/event-stream"}
)
```

- [ ] **Step 3: Verify the changes**

Run a quick test to ensure the code is syntactically correct:
```bash
cd /Users/tyrael/Desktop/temp/agentDemo
python -c "from backend.rag.generator import Generator; g = Generator(api_key='test', base_url='http://localhost:11434/v1'); print('Update config test successful')"
```

- [ ] **Step 4: Commit**

```bash
git add backend/rag/generator.py
git commit -m "fix: update httpx client config in update_config method"
```

---

### Task 3: Test streaming functionality

**Files:**
- Test: Manual testing with the application

- [ ] **Step 1: Start the backend server**

```bash
cd /Users/tyrael/Desktop/temp/agentDemo
python -m backend.main
```

- [ ] **Step 2: Start the frontend development server**

```bash
cd /Users/tyrael/Desktop/temp/agentDemo/frontend
npm run dev
```

- [ ] **Step 3: Test streaming output**

1. Open the browser to the frontend URL (typically http://localhost:5173)
2. Send a chat message
3. Verify that tokens appear incrementally in the UI
4. Check browser Network tab (F12 -> Network) to confirm SSE events are arriving separately

- [ ] **Step 4: Verify streaming behavior**

Expected behavior:
- Tokens should appear one by one or in small batches
- The streaming indicator should show during response generation
- The Network tab should show multiple SSE event frames arriving over time

---

## Self-Review Checklist

1. **Spec coverage:** ✅ The plan covers updating httpx client configuration in both `__init__` and `update_config` methods
2. **Placeholder scan:** ✅ No TBD, TODO, or vague instructions found
3. **Type consistency:** ✅ All method signatures and property names are consistent

---

## Execution Handoff

Plan complete and saved to `docs/superpowers/plans/2026-06-22-streaming-output-fix.md`. Two execution options:

**1. Subagent-Driven (recommended)** - I dispatch a fresh subagent per task, review between tasks, fast iteration

**2. Inline Execution** - Execute tasks in this session using executing-plans, batch execution with checkpoints

Which approach?