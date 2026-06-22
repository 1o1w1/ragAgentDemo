export interface Citation {
  content: string;
  source: string;
  score?: number;
}

export interface ChatMessage {
  role: "user" | "assistant";
  content: string;
  thinking?: string;
  citations?: Citation[];
  has_context?: boolean;
}

export interface ChatResponse {
  answer: string;
  reasoning?: string;
  citations: Citation[];
  has_context: boolean;
}

export interface DocumentUploadResponse {
  filename: string;
  chunks: number;
  status: string;
}

export interface UploadedFile {
  name: string;
  size: number;
}

export interface DocumentStats {
  count: number;
  name: string;
}

export interface AppConfig {
  rag: RagConfig;
  agent: AgentConfig;
  llm: LlmConfig;
  embedding: EmbeddingConfig;
  storage: StorageConfig;
  ui: UiConfig;
}

export interface RagConfig {
  chunk_size: number;
  chunk_overlap: number;
  top_k: number;
  similarity_threshold: number;
}

export interface AgentConfig {
  system_prompt: string;
  max_history: number;
  temperature: number;
  refuse_when_no_context: boolean;
}

export interface LlmConfig {
  model: string;
  base_api: string;
  max_tokens: number;
  enable_thinking: boolean;
}

export interface EmbeddingConfig {
  model: string;
  base_api: string;
}

export interface StorageConfig {
  vector_db: string;
  uploads: string;
}

export interface UiConfig {
  show_similarity_score: boolean;
}
