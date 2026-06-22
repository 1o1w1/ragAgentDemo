FROM ollama/ollama:latest

# 在构建时并行拉取模型
RUN ollama serve & \
    sleep 5 && \
    ollama pull qwen3.5:0.8b && \
    ollama pull qwen3-embedding:0.6b && \
    pkill ollama

CMD ["serve"]
