# Docker Compose 部署实现计划

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** 创建 Docker Compose 配置，实现一键启动后端、前端和 Ollama 服务

**Architecture:** 使用单 docker-compose.yml 文件定义三个服务（ollama、backend、frontend），通过 Docker 网络实现服务间通信，Nginx 反向代理统一入口

**Tech Stack:** Docker, Docker Compose, Nginx, Python, Node.js, Ollama

---

## 文件结构

| 文件 | 操作 | 说明 |
|------|------|------|
| `docker-compose.yml` | 创建 | 主编排文件 |
| `backend/Dockerfile` | 创建 | 后端镜像构建 |
| `frontend/Dockerfile` | 创建 | 前端镜像构建（多阶段） |
| `frontend/nginx.conf` | 创建 | Nginx 反向代理配置 |
| `scripts/ollama-init.sh` | 创建 | Ollama 初始化脚本 |
| `config.docker.yaml` | 创建 | Docker 环境专用配置 |

---

### Task 1: 创建 Ollama 初始化脚本

**Files:**
- Create: `scripts/ollama-init.sh`

- [ ] **Step 1: 创建 scripts 目录**

```bash
mkdir -p scripts
```

- [ ] **Step 2: 创建 ollama-init.sh 文件**

```bash
cat > scripts/ollama-init.sh << 'EOF'
#!/bin/bash

# 启动 Ollama 服务
ollama serve &

# 等待服务就绪
echo "等待 Ollama 服务启动..."
sleep 5

# 拉取模型
echo "拉取 LLM 模型: qwen3.5:0.8b..."
ollama pull qwen3.5:0.8b

echo "拉取 Embedding 模型: qwen3-embedding:0.6b..."
ollama pull qwen3-embedding:0.6b

echo "模型拉取完成！"

# 保持前台运行
wait
EOF
```

- [ ] **Step 3: 添加执行权限**

```bash
chmod +x scripts/ollama-init.sh
```

- [ ] **Step 4: 验证文件创建**

```bash
ls -la scripts/ollama-init.sh
cat scripts/ollama-init.sh
```

Expected: 文件存在且内容正确，有执行权限

- [ ] **Step 5: Commit**

```bash
git add scripts/ollama-init.sh
git commit -m "feat: add Ollama init script for auto model pulling"
```

---

### Task 2: 创建 Docker 环境配置文件

**Files:**
- Create: `config.docker.yaml`

- [ ] **Step 1: 创建 config.docker.yaml 文件**

```bash
cat > config.docker.yaml << 'EOF'
agent:
  max_history: 10
  refuse_when_no_context: true
  system_prompt: '你是一个知识库问答助手。根据上下文信息回答问题。

    如果没有相关信息，明确回复"知识库中未找到相关信息"。

    请按以下结构组织回答：
    1. 先简要总结核心答案（2-3句话）
    2. 再展开详细说明
    3. 最后列出参考来源

    '
  temperature: 0.7

embedding:
  base_api: http://ollama:11434/v1
  model: qwen3-embedding:0.6b
  provider: openai

llm:
  base_api: http://ollama:11434/v1
  max_tokens: 2000
  model: qwen3.5:0.8b
  provider: openai
  temperature: 0.7
  enable_thinking: false

rag:
  chunk_overlap: 64
  chunk_size: 2048
  similarity_threshold: 1.2
  top_k: 5

sources:
  local:
    enabled: true
    path: ./knowledge
    patterns:
      - '**/*.md'
      - '**/*.txt'
  upload:
    enabled: true
    path: ./uploads

storage:
  documents: ./knowledge
  uploads: ./uploads
  vector_db: ./chroma_db

ui:
  show_citations: true
  show_similarity_score: false
  theme: light
EOF
```

- [ ] **Step 2: 验证文件创建**

```bash
cat config.docker.yaml
```

Expected: 文件内容正确，包含所有配置项

- [ ] **Step 3: Commit**

```bash
git add config.docker.yaml
git commit -m "feat: add Docker-specific config with internal network addresses"
```

---

### Task 3: 创建后端 Dockerfile

**Files:**
- Create: `backend/Dockerfile`

- [ ] **Step 1: 创建 backend/Dockerfile 文件**

```bash
cat > backend/Dockerfile << 'EOF'
FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

CMD ["uvicorn", "backend.main:app", "--host", "0.0.0.0", "--port", "8000"]
EOF
```

- [ ] **Step 2: 验证文件创建**

```bash
cat backend/Dockerfile
```

Expected: 文件内容正确

- [ ] **Step 3: Commit**

```bash
git add backend/Dockerfile
git commit -m "feat: add backend Dockerfile"
```

---

### Task 4: 创建前端 Nginx 配置

**Files:**
- Create: `frontend/nginx.conf`

- [ ] **Step 1: 创建 frontend/nginx.conf 文件**

```bash
cat > frontend/nginx.conf << 'EOF'
server {
    listen 80;
    server_name localhost;

    location / {
        root /usr/share/nginx/html;
        index index.html;
        try_files $uri $uri/ /index.html;
    }

    location /api/ {
        proxy_pass http://backend:8000/api/;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}
EOF
```

- [ ] **Step 2: 验证文件创建**

```bash
cat frontend/nginx.conf
```

Expected: 文件内容正确，包含反向代理配置

- [ ] **Step 3: Commit**

```bash
git add frontend/nginx.conf
git commit -m "feat: add Nginx config with reverse proxy for API"
```

---

### Task 5: 创建前端 Dockerfile

**Files:**
- Create: `frontend/Dockerfile`

- [ ] **Step 1: 创建 frontend/Dockerfile 文件**

```bash
cat > frontend/Dockerfile << 'EOF'
# 构建阶段
FROM node:18-alpine AS builder

WORKDIR /app

COPY package*.json ./
RUN npm ci

COPY . .
RUN npm run build

# 运行阶段
FROM nginx:alpine

COPY --from=builder /app/dist /usr/share/nginx/html
COPY nginx.conf /etc/nginx/conf.d/default.conf

EXPOSE 80

CMD ["nginx", "-g", "daemon off;"]
EOF
```

- [ ] **Step 2: 验证文件创建**

```bash
cat frontend/Dockerfile
```

Expected: 文件内容正确，包含多阶段构建配置

- [ ] **Step 3: Commit**

```bash
git add frontend/Dockerfile
git commit -m "feat: add frontend Dockerfile with multi-stage build"
```

---

### Task 6: 创建 docker-compose.yml

**Files:**
- Create: `docker-compose.yml`

- [ ] **Step 1: 创建 docker-compose.yml 文件**

```bash
cat > docker-compose.yml << 'EOF'
version: '3.8'

services:
  ollama:
    image: ollama/ollama:latest
    container_name: rag-ollama
    ports:
      - "21434:11434"
    volumes:
      - ./scripts/ollama-init.sh:/init.sh
    entrypoint: ["/bin/bash", "/init.sh"]
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:11434"]
      interval: 10s
      timeout: 5s
      retries: 5
    restart: unless-stopped

  backend:
    build:
      context: ./backend
      dockerfile: Dockerfile
    container_name: rag-backend
    ports:
      - "8000:8000"
    volumes:
      - chroma_data:/app/chroma_db
      - uploads_data:/app/uploads
      - ./config.docker.yaml:/app/config.yaml
      - ./knowledge:/app/knowledge
    depends_on:
      ollama:
        condition: service_healthy
    restart: unless-stopped

  frontend:
    build:
      context: ./frontend
      dockerfile: Dockerfile
    container_name: rag-frontend
    ports:
      - "80:80"
    depends_on:
      - backend
    restart: unless-stopped

volumes:
  chroma_data:
  uploads_data:
EOF
```

- [ ] **Step 2: 验证文件创建**

```bash
cat docker-compose.yml
```

Expected: 文件内容正确，包含三个服务定义

- [ ] **Step 3: 验证 docker-compose.yml 语法**

```bash
docker compose config
```

Expected: 语法验证通过，无错误

- [ ] **Step 4: Commit**

```bash
git add docker-compose.yml
git commit -m "feat: add docker-compose.yml with all services"
```

---

### Task 7: 构建并启动服务

**Files:**
- None (验证步骤)

- [ ] **Step 1: 构建所有镜像**

```bash
docker compose build
```

Expected: 所有镜像构建成功

- [ ] **Step 2: 启动所有服务**

```bash
docker compose up -d
```

Expected: 所有服务启动成功

- [ ] **Step 3: 查看 Ollama 启动日志**

```bash
docker compose logs -f ollama
```

Expected: 看到模型拉取进度，等待完成

- [ ] **Step 4: 检查所有服务状态**

```bash
docker compose ps
```

Expected: 所有服务状态为 running

- [ ] **Step 5: 验证前端访问**

```bash
curl -I http://localhost
```

Expected: 返回 HTTP 200

- [ ] **Step 6: 验证后端 API 访问**

```bash
curl http://localhost:8000/docs
```

Expected: 返回 API 文档页面

- [ ] **Step 7: 验证 Ollama 服务访问**

```bash
curl http://localhost:21434
```

Expected: 返回 Ollama 服务响应

- [ ] **Step 8: Commit 最终状态**

```bash
git status
```

Expected: 所有文件已提交，工作区干净

---

### Task 8: 更新 README 文档

**Files:**
- Modify: `README.md`

- [ ] **Step 1: 在 README.md 中添加 Docker 部署章节**

在 `## 本地启动` 之前添加：

```markdown
## Docker 部署（推荐）

### 前提条件

- 安装 [Docker](https://docs.docker.com/get-docker/)
- 安装 [Docker Compose](https://docs.docker.com/compose/install/)

### 一键启动

```bash
# 克隆项目
git clone <repository-url>
cd agentDemo

# 启动所有服务
docker compose up -d --build

# 查看启动日志（观察模型拉取进度）
docker compose logs -f ollama
```

首次启动需要拉取 Ollama 模型（约 1-2 分钟），请耐心等待。

### 访问地址

| 服务 | 地址 |
|------|------|
| 前端界面 | http://localhost |
| 后端 API | http://localhost:8000 |
| API 文档 | http://localhost:8000/docs |
| Ollama 服务 | http://localhost:21434 |

### 常用命令

```bash
# 停止服务
docker compose down

# 重启服务
docker compose restart

# 查看日志
docker compose logs -f backend
docker compose logs -f frontend

# 进入容器调试
docker compose exec backend bash
docker compose exec ollama bash

# 清理数据（重置向量数据库和上传文件）
docker compose down -v
```

---
```

- [ ] **Step 2: 验证 README 修改**

```bash
grep -A 50 "## Docker 部署" README.md
```

Expected: 显示新增的 Docker 部署章节

- [ ] **Step 3: Commit**

```bash
git add README.md
git commit -m "docs: add Docker deployment instructions to README"
```

---

## 执行选项

**Plan complete and saved to `docs/superpowers/plans/2026-06-22-docker-compose-plan.md`. Two execution options:**

**1. Subagent-Driven (recommended)** - 我为每个任务调度一个新的子代理，任务间进行审查，快速迭代

**2. Inline Execution** - 在当前会话中使用 executing-plans 执行任务，批量执行并设置检查点

**选择哪种方式？**
