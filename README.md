# RAG 智能问答 Agent

基于检索增强生成（RAG）的智能问答系统，支持本地文档知识库。

## 功能特性

- 📚 支持 Markdown 和 TXT 文档导入
- 🔍 基于向量相似度的智能检索
- 💬 多轮对话支持
- 📖 回答附带引用来源
- ⚙️ 可配置的 RAG 参数
- 🖥️ 现代化 React 前端界面

## 技术栈

**后端：**
- Python 3.9+
- FastAPI
- LangChain
- ChromaDB（向量数据库）

**前端：**
- React 18
- TypeScript
- Vite

**LLM & Embedding：**
- 默认使用 Ollama（本地部署）
- 支持 OpenAI 兼容 API

---

## 本地启动

### 前提条件

安装 [Ollama](https://ollama.ai)（脚本会自动检查并提示）：

```bash
# macOS / Linux
curl -fsSL https://ollama.ai/install.sh | sh

# Windows
# 从官网下载安装包
```

### 一键启动

```bash
# 克隆项目
git clone <repository-url>
cd agentDemo

# 运行启动脚本（自动处理环境、依赖、模型和服务）
chmod +x start.sh
./start.sh
```

脚本会自动完成以下工作：
- 创建 Python 虚拟环境
- 安装后端依赖
- 检查并启动 Ollama 服务
- 拉取所需模型（首次运行）
- 启动后端和前端服务

启动完成后访问：
- 前端界面: http://localhost:5173
- 后端 API: http://localhost:8000
- API 文档: http://localhost:8000/docs

按 `Ctrl+C` 停止所有服务。

<details>
<summary>手动启动（点击展开）</summary>

如果需要手动控制启动过程：

```bash
# 1. 创建虚拟环境
python3 -m venv .venv
source .venv/bin/activate

# 2. 安装后端依赖
pip install -r requirements.txt

# 3. 安装前端依赖
cd frontend && npm install && cd ..

# 4. 拉取模型
ollama pull qwen3.5:0.8b
ollama pull qwen3-embedding:0.6b

# 5. 启动后端（终端 1）
uvicorn backend.main:app --reload --host 0.0.0.0 --port 8000

# 6. 启动前端（终端 2）
cd frontend && npm run dev
```

</details>

---

## Docker 启动

### 前提条件

- [Docker](https://docs.docker.com/get-docker/) 20.10+
- [Docker Compose](https://docs.docker.com/compose/install/) v2+

验证安装：

```bash
docker --version
docker compose version
```

### 一键启动

```bash
# 克隆项目
git clone <repository-url>
cd agentDemo

# 构建并启动所有服务
docker compose up -d --build
```

首次启动需要拉取模型，耗时较长，可通过日志查看进度：

```bash
docker compose logs -f
```

启动完成后访问：
- 前端界面: http://localhost
- 后端 API: http://localhost:8000
- API 文档: http://localhost:8000/docs
- Ollama API: http://localhost:21434

### 常用命令

```bash
# 查看服务状态
docker compose ps

# 查看日志
docker compose logs -f
docker compose logs -f backend

# 停止服务
docker compose down

# 重启服务
docker compose restart

# 进入容器
docker compose exec backend bash
docker compose exec ollama bash

# 拉取模型
docker compose exec ollama ollama pull qwen3.5:0.8b
docker compose exec ollama ollama pull qwen3-embedding:0.6b

# 查看模型列表
docker compose exec ollama ollama list

# 清理数据（删除向量数据库和上传文件）
docker compose down -v
```

---

## 配置说明

配置文件位于 `config.yaml`（本地启动）或 `config.docker.yaml`（Docker 启动）：

```yaml
# LLM 配置
llm:
  provider: ollama                    # 提供商：ollama / openai
  base_api: http://localhost:11434    # API 地址（Docker 环境使用 http://ollama:11434）
  model: qwen3.5:0.8b                   # 模型名称
  temperature: 0.7                    # 温度参数
  max_tokens: 2000                    # 最大 token 数

# Embedding 配置
embedding:
  provider: ollama
  base_api: http://localhost:11434
  model: qwen3-embedding:0.6b

# RAG 配置
rag:
  chunk_size: 512          # 文档分块大小
  chunk_overlap: 64        # 分块重叠大小
  top_k: 5                 # 检索返回的文档数量
  similarity_threshold: 0.7 # 相似度阈值

# Agent 配置
agent:
  max_history: 10                    # 对话历史轮数
  refuse_when_no_context: true       # 无上下文时拒绝回答
  system_prompt: |                   # 系统提示词
    你是一个知识库问答助手。根据上下文信息回答问题。
    如果没有相关信息，明确回复"知识库中未找到相关信息"。
    回答时请引用来源。
```

### 使用 OpenAI API

如需使用 OpenAI API，修改配置：

```yaml
llm:
  provider: openai
  base_api: https://api.openai.com/v1
  model: gpt-3.5-turbo

embedding:
  provider: openai
  base_api: https://api.openai.com/v1
  model: text-embedding-ada-002
```

并设置环境变量：

```bash
export OPENAI_API_KEY=your_api_key_here
```

---

## 项目结构

```
agentDemo/
├── backend/                # 后端代码
│   ├── main.py            # FastAPI 入口
│   ├── config.py          # 配置管理
│   ├── rag/               # RAG 模块
│   │   ├── document_loader.py  # 文档加载
│   │   ├── text_splitter.py    # 文本分割
│   │   ├── embeddings.py       # Embedding
│   │   ├── vector_store.py     # 向量存储
│   │   ├── retriever.py        # 检索器
│   │   └── generator.py        # 生成器
│   ├── agent/             # Agent 模块
│   │   ├── conversation.py     # 对话管理
│   │   ├── citation.py         # 引用管理
│   │   └── behavior.py         # Agent 行为
│   └── api/               # API 路由
│       ├── chat.py             # 聊天接口
│       ├── documents.py        # 文档接口
│       └── config.py           # 配置接口
├── frontend/               # 前端代码
│   └── src/
│       ├── components/     # React 组件
│       ├── hooks/          # 自定义 Hooks
│       ├── services/       # API 服务
│       └── types/          # TypeScript 类型
├── docs/                   # 示例文档
├── config.yaml             # 配置文件
├── requirements.txt        # Python 依赖
└── README.md               # 项目说明
```

---

## API 接口

### 聊天接口

```bash
# 发送消息
curl -X POST http://localhost:8000/api/chat/ \
  -H "Content-Type: application/json" \
  -d '{"query": "什么是机器学习？"}'

# 获取历史
curl http://localhost:8000/api/chat/history

# 清空历史
curl -X DELETE http://localhost:8000/api/chat/history
```

### 文档接口

```bash
# 上传文档
curl -X POST http://localhost:8000/api/documents/upload \
  -F "file=@document.md"

# 加载目录文档
curl -X POST http://localhost:8000/api/documents/load-directory

# 获取统计信息
curl http://localhost:8000/api/documents/stats
```

### 配置接口

```bash
# 获取配置
curl http://localhost:8000/api/config/

# 更新配置
curl -X PUT http://localhost:8000/api/config/ \
  -H "Content-Type: application/json" \
  -d '{"rag": {"top_k": 10}}'
```

---

## 添加文档

1. 将 Markdown 或 TXT 文件放入 `docs/` 目录
2. 调用加载接口或重启后端服务
3. 文档会自动分块并建立索引

---

## 常见问题

### Ollama 连接失败

确保 Ollama 服务正在运行：

```bash
ollama serve
```

检查服务状态：

```bash
curl http://localhost:11434
```

### 模型未找到

拉取所需模型：

```bash
ollama pull qwen3.5:0.8b
ollama pull qwen3-embedding:0.6b
```

查看已安装模型：

```bash
ollama list
```

### 端口被占用

修改启动端口：

```bash
# 后端
uvicorn backend.main:app --port 8001

# 前端
cd frontend
# 修改 vite.config.ts 中的 server.port
```

---

## 开发

### 运行测试

```bash
# 运行所有测试
python3 -m pytest tests/

# 运行特定测试
python3 -m pytest tests/backend/test_config.py

# 查看测试覆盖率
python3 -m pytest tests/ --cov=backend
```

### 代码格式化

```bash
# 后端
black backend/
isort backend/

# 前端
cd frontend
npm run lint
```

---

## 许可证

MIT License