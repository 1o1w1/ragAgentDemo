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
