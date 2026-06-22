import type {
  ChatResponse,
  DocumentUploadResponse,
  DocumentStats,
  UploadedFile,
  AppConfig,
} from "../types";

const API_BASE = "/api";

async function fetchJson<T>(url: string, options?: RequestInit): Promise<T> {
  const response = await fetch(url, options);
  if (!response.ok) {
    const error = await response.json().catch(() => ({ detail: response.statusText }));
    throw new Error(error.detail || "Request failed");
  }
  return response.json();
}

export const chatApi = {
  sendMessage(query: string): Promise<ChatResponse> {
    return fetchJson(`${API_BASE}/chat/`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ query }),
    });
  },

  sendMessageStream(query: string): EventSource {
    const url = new URL(`${API_BASE}/chat/stream`, window.location.origin);
    url.searchParams.append("query", query);
    return new EventSource(url.toString());
  },

  getHistory(): Promise<{ history: Array<{ role: string; content: string }> }> {
    return fetchJson(`${API_BASE}/chat/history`);
  },

  clearHistory(): Promise<{ status: string }> {
    return fetchJson(`${API_BASE}/chat/history`, { method: "DELETE" });
  },
};

export interface ServerStatus {
  status: string;
  is_loading: boolean;
  loading_message: string;
}

export const statusApi = {
  getHealth(): Promise<ServerStatus> {
    return fetchJson("/health");
  },
};

export const documentsApi = {
  async upload(file: File): Promise<DocumentUploadResponse> {
    const formData = new FormData();
    formData.append("file", file);
    const response = await fetch(`${API_BASE}/documents/upload`, {
      method: "POST",
      body: formData,
    });
    if (!response.ok) {
      const error = await response.json().catch(() => ({ detail: response.statusText }));
      throw new Error(error.detail || "Upload failed");
    }
    return response.json();
  },

  getStats(): Promise<DocumentStats> {
    return fetchJson(`${API_BASE}/documents/stats`);
  },

  listUploads(): Promise<{ files: UploadedFile[] }> {
    return fetchJson(`${API_BASE}/documents/uploads`);
  },

  deleteAll(): Promise<{ status: string }> {
    return fetchJson(`${API_BASE}/documents/`, { method: "DELETE" });
  },
};

export const configApi = {
  getConfig(): Promise<AppConfig> {
    return fetchJson(`${API_BASE}/config/`);
  },

  updateConfig(updates: Record<string, unknown>): Promise<AppConfig> {
    return fetchJson(`${API_BASE}/config/`, {
      method: "PUT",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ updates }),
    });
  },

  reloadConfig(): Promise<AppConfig> {
    return fetchJson(`${API_BASE}/config/reload`, { method: "POST" });
  },
};
