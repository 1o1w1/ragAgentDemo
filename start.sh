#!/bin/bash

# RAG 智能问答 Agent 启动脚本

set -e

echo "🚀 启动 RAG 智能问答 Agent..."

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"

VENV_DIR="$SCRIPT_DIR/backend/.venv"

# 检查虚拟环境
if [ ! -d "$VENV_DIR" ]; then
    echo "📦 创建 Python 虚拟环境..."
    python3 -m venv "$VENV_DIR"
fi

# 激活虚拟环境
echo "🔧 激活虚拟环境..."
. "$VENV_DIR/bin/activate"

# 检查依赖
if ! "$VENV_DIR/bin/python" -c "import uvicorn" 2>/dev/null; then
    echo "📥 安装 Python 依赖..."
    "$VENV_DIR/bin/python" -m pip install -r "$SCRIPT_DIR/backend/requirements.txt"
fi

# 检查 npm
if ! command -v npm &> /dev/null; then
    echo "⚠️  未检测到 npm，请先安装 Node.js 和 npm"
    echo "   访问 https://nodejs.org 下载安装"
    exit 1
fi

# 检查 Ollama
if ! command -v ollama &> /dev/null; then
    echo "⚠️  未检测到 Ollama，请先安装 Ollama"
    echo "   访问 https://ollama.ai 下载安装"
    exit 1
fi

# 检查 Ollama 服务
if ! curl -s http://localhost:11434 > /dev/null 2>&1; then
    echo "⚠️  Ollama 服务未启动，正在启动..."
    ollama serve &
    sleep 3
fi

# 检查模型
echo "🔍 检查模型..."
if ! ollama list | grep -q "qwen3.5:0.8b"; then
    echo "📥 拉取 LLM 模型 (qwen3.5:0.8b)..."
    ollama pull qwen3.5:0.8b
fi

if ! ollama list | grep -q "qwen3-embedding:0.6b"; then
    echo "📥 拉取 Embedding 模型 (qwen3-embedding:0.6b)..."
    ollama pull qwen3-embedding:0.6b
fi

# 启动后端
echo "🌐 启动后端服务..."
cd "$SCRIPT_DIR/backend"
"$VENV_DIR/bin/python" -m uvicorn main:app --reload --host 0.0.0.0 --port 8000 &
BACKEND_PID=$!
cd "$SCRIPT_DIR"

# 等待后端启动
sleep 3

# 启动前端
echo "🖥️  启动前端服务..."
cd frontend
if [ ! -d "node_modules" ]; then
    echo "📥 安装前端依赖..."
    npm install
fi
npm run dev &
FRONTEND_PID=$!
cd ..

echo ""
echo "✅ 启动完成！"
echo ""
echo "📌 访问地址："
echo "   前端界面: http://localhost:5173"
echo "   后端 API: http://localhost:8000"
echo "   API 文档: http://localhost:8000/docs"
echo ""
echo "按 Ctrl+C 停止服务"

# 捕获退出信号
trap "echo ''; echo '🛑 停止服务...'; kill $BACKEND_PID $FRONTEND_PID 2>/dev/null; exit" INT TERM

# 等待
wait
