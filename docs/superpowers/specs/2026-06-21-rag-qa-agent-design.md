# 多源文档智能问答 Agent（RAG）设计文档

## 1. 项目概述

### 1.1 项目目标
构建一个基于RAG（检索增强生成）的智能问答Agent，能够根据知识库内容回答问题并标注出处。

### 1.2 核心需求
1. 文档接入（至少2种方式）：本地文件夹、文件上传
2. RAG流水线：文档切分 → 向量化 → 检索 → 生成回答
3. 引用溯源：每条回答必须附带引用来源
4. Agent行为：检索不到相关内容时明确回复「知识库中未找到」，不编造答案
5. 支持至少1轮追问或澄清
6. 可配置项：chunk大小、top-k、embedding方式、数据源路径、系统提示词等
7. 使用LangChain实现，要有Web界面

### 1.3 技术约束
- 开发语言：Python 3.10+
- 框架：LangChain
- 前端：React
- 部署：本地开发环境

## 2. 系统架构

### 2.1 整体架构
```
┌─────────────────────────────────────────┐
│           React 前端 (Port 3000)        │
│  - 聊天界面                              │
│  - 文件上传                              │
│  - 引用来源展示                          │
└─────────────────┬───────────────────────┘
                  │ HTTP API
┌─────────────────▼───────────────────────┐
│          FastAPI 后端 (Port 8000)        │
│  - 文档处理服务                          │
│  - RAG流水线服务                         │
│  - Agent对话服务                         │
└─────────────────┬───────────────────────┘
                  │
┌─────────────────▼───────────────────────┐
│           数据存储层                      │
│  - Chroma 向量数据库                     │
│  - 文件系统 (文档存储)                   │
│  - 配置文件 (YAML)                       │
└─────────────────────────────────────────┘
```

### 2.2 技术栈
- **后端**：FastAPI + Python 3.10+
- **前端**：React 18 + TypeScript + Ant Design
- **RAG引擎**：LangChain
- **向量数据库**：Chroma
- **LLM**：OpenAI兼容API
- **配置管理**：YAML

## 3. RAG流水线设计

### 3.1 文档接入层
**支持的数据源**：
1. **本地文件夹**：监控 `./docs` 目录，支持 `.md` 和 `.txt` 文件
2. **文件上传**：通过Web界面上传文件，存储到 `./uploads` 目录

**文档加载器**：
- 使用LangChain的 `DirectoryLoader` 和 `TextLoader`
- 支持递归扫描子目录
- 自动检测文件编码

### 3.2 文档处理层
**文本分割策略**：
- 使用 `RecursiveCharacterTextSplitter`
- 默认chunk_size: 512字符
- 默认chunk_overlap: 64字符
- 支持中文分句优化

**向量化**：
- 使用LangChain的Embeddings接口
- 支持OpenAI兼容的embedding API
- 默认使用 `text-embedding-ada-002` 模型

### 3.3 检索层
**向量存储**：
- 使用Chroma作为向量数据库
- 支持持久化存储到 `./chroma_db`
- 支持元数据过滤

**检索策略**：
- 默认使用相似度检索
- top_k: 5（返回最相关的5个文档块）
- 支持相似度阈值过滤

### 3.4 生成层
**LLM集成**：
- 使用LangChain的ChatOpenAI接口
- 支持OpenAI兼容的API
- 配置：model、base_api、temperature等

**提示词模板**：
使用配置文件中的`agent.system_prompt`作为系统提示词，并添加上下文和问题模板：
```
{system_prompt}

上下文：
{context}

问题：{question}

回答时请引用来源，格式为：[来源：文档名]
```

**引用溯源**：
- 从检索到的文档块中提取元数据（文档名、章节、段落摘要）
- 在回答中标注引用来源
- 支持多引用标注

## 4. Agent行为设计

### 4.1 对话管理
**对话状态**：
- 维护对话历史（最多10轮）
- 支持上下文理解
- 支持追问和澄清

**Agent行为规则**：
1. **检索不到相关内容时**：明确回复「知识库中未找到相关信息」
2. **拒绝编造答案**：当置信度低于阈值时拒绝回答
3. **支持追问**：理解上下文，支持多轮对话

### 4.2 引用溯源
**引用格式**：
```
根据知识库内容，[回答内容]

引用来源：
1. [文档名] - [章节/段落摘要]
2. [文档名] - [章节/段落摘要]
```

**引用信息包含**：
- 文档名称
- 章节标题（如果有）
- 段落摘要（前100字符）
- 相似度分数（可选）

### 4.3 错误处理
**异常情况处理**：
- 文档加载失败：记录错误，继续处理其他文档
- 向量化失败：重试机制，失败后跳过该文档
- LLM调用失败：返回友好错误信息
- 检索超时：返回部分结果或错误提示

## 5. 配置管理设计

### 5.1 配置文件结构
使用YAML格式，文件路径：`./config.yaml`

```yaml
# 数据源配置
sources:
  local:
    enabled: true
    path: "./docs"
    patterns: ["**/*.md", "**/*.txt"]
  upload:
    enabled: true
    path: "./uploads"

# RAG配置
rag:
  chunk_size: 512
  chunk_overlap: 64
  top_k: 5
  similarity_threshold: 0.7

# Agent配置
agent:
  max_history: 10
  refuse_when_no_context: true
  temperature: 0.7
  system_prompt: |
    你是一个知识库问答助手。根据上下文信息回答问题。
    如果没有相关信息，明确回复"知识库中未找到相关信息"。
    回答时请引用来源。

# UI配置
ui:
  show_citations: true
  show_similarity_score: false
  theme: "light"

# LLM配置
llm:
  provider: "openai"
  model: "gpt-3.5-turbo"
  base_api: "https://api.openai.com/v1"
  temperature: 0.7
  max_tokens: 2000

# Embedding配置
embedding:
  provider: "openai"
  model: "text-embedding-ada-002"
  base_api: "https://api.openai.com/v1"

# 存储配置
storage:
  vector_db: "./chroma_db"
  documents: "./docs"
  uploads: "./uploads"
```

### 5.2 配置管理功能
**配置热重载**：
- 监听配置文件变化
- 自动重新加载配置
- 无需重启服务

**配置验证**：
- 启动时验证配置格式
- 必填项检查
- 默认值填充

**环境变量覆盖**：
- 支持环境变量覆盖配置
- 格式：`RAG_CHUNK_SIZE=512`

## 6. Web界面设计

### 6.1 界面布局
**主界面分为三个区域**：
1. **左侧边栏**：配置面板、数据源管理
2. **中央区域**：聊天界面
3. **右侧面板**：引用来源详情、文档预览

### 6.2 核心功能
**聊天界面**：
- 消息输入框
- 对话历史显示
- 引用来源高亮显示
- 支持Markdown渲染

**文件上传**：
- 拖拽上传文件
- 支持多文件上传
- 上传进度显示
- 文件列表管理

**配置面板**：
- 实时编辑配置
- 配置保存/加载
- 配置验证反馈

**引用展示**：
- 引用来源列表
- 相似度分数显示
- 文档内容预览
- 引用跳转功能

### 6.3 技术实现
**前端技术栈**：
- React 18 + TypeScript
- Ant Design组件库
- React Router路由管理
- Axios HTTP客户端

**API设计**：
- RESTful API
- WebSocket支持（可选，用于实时更新）
- 错误处理统一格式

## 7. 项目结构设计

```
agentDemo/
├── README.md
├── config.yaml                  # 主配置文件
├── requirements.txt             # Python依赖
├── package.json                 # 前端依赖
├── .env.example                 # 环境变量示例
├── docs/                        # 示例文档目录
│   ├── example1.md
│   ├── example2.md
│   ├── example3.md
│   ├── example4.md
│   └── example5.md
├── uploads/                     # 上传文件目录
├── chroma_db/                   # 向量数据库存储
├── backend/                     # Python后端
│   ├── __init__.py
│   ├── main.py                  # FastAPI入口
│   ├── config.py                # 配置管理
│   ├── rag/                     # RAG核心模块
│   │   ├── __init__.py
│   │   ├── document_loader.py   # 文档加载器
│   │   ├── text_splitter.py     # 文本分割器
│   │   ├── embeddings.py        # 嵌入模型
│   │   ├── vector_store.py      # 向量存储
│   │   ├── retriever.py         # 检索器
│   │   └── generator.py         # 生成器
│   ├── agent/                   # Agent模块
│   │   ├── __init__.py
│   │   ├── conversation.py      # 对话管理
│   │   ├── citation.py          # 引用溯源
│   │   └── behavior.py          # Agent行为
│   ├── api/                     # API路由
│   │   ├── __init__.py
│   │   ├── chat.py              # 聊天API
│   │   ├── documents.py         # 文档API
│   │   └── config.py            # 配置API
│   └── utils/                   # 工具函数
│       ├── __init__.py
│       ├── logger.py            # 日志工具
│       └── validators.py        # 验证工具
├── frontend/                    # React前端
│   ├── public/
│   ├── src/
│   │   ├── components/          # React组件
│   │   │   ├── Chat/            # 聊天组件
│   │   │   ├── Sidebar/         # 侧边栏组件
│   │   │   ├── FileUpload/      # 文件上传组件
│   │   │   └── Citations/       # 引用展示组件
│   │   ├── pages/               # 页面组件
│   │   ├── services/            # API服务
│   │   ├── hooks/               # 自定义Hooks
│   │   ├── utils/               # 工具函数
│   │   ├── types/               # TypeScript类型
│   │   └── App.tsx
│   ├── package.json
│   └── tsconfig.json
└── tests/                       # 测试目录
    ├── backend/
    └── frontend/
```

## 8. 示例文档和标准问题

### 8.1 示例文档（5篇）
1. **Python编程指南.md** - Python基础知识
2. **机器学习入门.md** - 机器学习概念
3. **Web开发技术.md** - Web开发技术栈
4. **数据库设计.md** - 数据库设计原则
5. **项目管理.md** - 项目管理方法

### 8.2 标准问题（3个）
1. **问题1**：Python中如何定义函数？
   - **期望命中**：Python编程指南.md
   - **期望回答**：包含函数定义语法、参数、返回值等

2. **问题2**：什么是监督学习和无监督学习？
   - **期望命中**：机器学习入门.md
   - **期望回答**：包含两种学习方式的定义和区别

3. **问题3**：如何设计数据库表结构？
   - **期望命中**：数据库设计.md
   - **期望回答**：包含数据库设计原则、范式等

### 8.3 知识库外问题测试
**测试问题**：2024年奥运会举办地点是哪里？
- **期望行为**：拒绝回答，回复"知识库中未找到相关信息"
- **验证**：确保Agent不会编造答案

## 9. 开发计划

### 9.1 阶段1：基础架构（2天）
- 项目结构搭建
- 配置管理模块
- FastAPI后端框架
- React前端框架

### 9.2 阶段2：RAG核心（3天）
- 文档加载器实现
- 文本分割器实现
- 嵌入模型集成
- 向量存储集成
- 检索器实现
- 生成器实现

### 9.3 阶段3：Agent功能（2天）
- 对话管理模块
- 引用溯源模块
- Agent行为实现

### 9.4 阶段4：Web界面（3天）
- 聊天界面开发
- 文件上传功能
- 配置面板开发
- 引用展示功能

### 9.5 阶段5：测试和优化（2天）
- 单元测试编写
- 集成测试
- 性能优化
- 文档编写

## 10. 验收标准

### 10.1 功能验收
1. ✅ 支持本地文件夹和文件上传两种文档接入方式
2. ✅ 实现完整的RAG流水线
3. ✅ 每条回答附带引用来源
4. ✅ 检索不到相关内容时明确回复「知识库中未找到」
5. ✅ 支持至少1轮追问或澄清
6. ✅ 配置项可调整
7. ✅ 有Web界面

### 10.2 技术验收
1. ✅ 使用Python 3.10+实现
2. ✅ 使用LangChain框架
3. ✅ 代码结构清晰，模块化
4. ✅ 有基本的错误处理
5. ✅ 有基本的测试覆盖

### 10.3 文档验收
1. ✅ README包含项目说明
2. ✅ 包含5篇示例文档
3. ✅ 包含3个标准问题及期望答案
4. ✅ 包含部署和使用说明