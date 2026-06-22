# Docker Compose 部署设计文档

## 概述

为 RAG 智能问答系统创建 Docker Compose 部署方案，支持一键启动后端、前端和 Ollama 服务。

## 需求总结

- 所有服务作为 Docker 容器运行
- Ollama 使用 CPU 模式（无 GPU）
- 容器启动时自动拉取所需模型
- 仅持久化业务数据（ChromaDB、上传文件），Ollama 模型不持久化
- 前端使用 Nginx 静态服务 + 反向代理
- Ollama 宿主机端口：21434

## 服务架构

### 服务列表

| 服务 | 镜像 | 容器端口 | 宿主机端口 | 说明 |
|------|------|---------|-----------|------|
| ollama | ollama/ollama:latest | 11434 | 21434 | LLM 服务，启动时自动拉取模型 |
| backend | 自定义构建 | 8000 | 8000 | FastAPI 后端 |
| frontend | 自定义构建（Nginx） | 80 | 80 | React 前端 + Nginx 反向代理 |

### 网络拓扑

```
用户浏览器 → frontend:80 (Nginx)
                ↓ /api/* 反向代理
            backend:8000 (FastAPI)
                ↓
            ollama:11434 (LLM)
```

### 数据卷

| 卷名 | 挂载路径 | 说明 |
|------|---------|------|
| chroma_data | /app/chroma_db | ChromaDB 向量数据库 |
| uploads_data | /app/uploads | 用户上传文件 |

## 文件结构

```
agentDemo/
├── docker-compose.yml          # 主编排文件
├── backend/
│   └── Dockerfile              # 后端镜像构建
├── frontend/
│   ├── Dockerfile              # 前端镜像构建（多阶段）
│   └── nginx.conf              # Nginx 配置（反向代理）
├── scripts/
│   └── ollama-init.sh          # Ollama 初始化脚本（自动拉取模型）
├── config.docker.yaml          # Docker 环境专用配置
└── .env                        # 环境变量（可选）
```

## 启动流程

```
1. ollama 容器启动
   ↓
2. 执行 ollama-init.sh 自动拉取模型（qwen3.5:0.8b, qwen3-embedding:0.6b）
   ↓
3. 健康检查通过后，backend 容器启动
   ↓
4. frontend 容器启动（依赖 backend）
```

## 配置详情

### docker-compose.yml

```yaml
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
```

### backend/Dockerfile

```dockerfile
FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

CMD ["uvicorn", "backend.main:app", "--host", "0.0.0.0", "--port", "8000"]
```

### frontend/Dockerfile

```dockerfile
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
```

### frontend/nginx.conf

```nginx
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
```

### scripts/ollama-init.sh

```bash
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
```

### config.docker.yaml

```yaml
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
```

## 使用说明

### 启动服务

```bash
# 构建并启动所有服务
docker compose up -d --build

# 查看启动日志（观察模型拉取进度）
docker compose logs -f ollama

# 查看所有服务状态
docker compose ps
```

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

### 首次启动预期

- Ollama 启动后自动拉取模型（约 1-2 分钟，取决于网络）
- 模型拉取完成后 backend 才会启动
- 整个启动过程约 2-3 分钟

## 注意事项

1. **端口冲突**：确保宿主机 80、8000、21434 端口未被占用
2. **磁盘空间**：Ollama 模型较大，确保有足够磁盘空间
3. **网络**：首次拉取模型需要稳定的网络连接
4. **数据持久化**：使用 `docker compose down -v` 会删除所有持久化数据
