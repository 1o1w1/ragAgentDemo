import { useState } from "react";
import type { AppConfig } from "../../types";

interface Props {
  config: AppConfig | null;
  loading: boolean;
  onUpdate: (updates: Record<string, unknown>) => void;
  onReload: () => void;
}

export function ConfigPanel({ config, loading, onUpdate, onReload }: Props) {
  const [topK, setTopK] = useState(String(config?.rag.top_k ?? 3));
  const [threshold, setThreshold] = useState(String(config?.rag.similarity_threshold ?? 0.5));
  const [temperature, setTemperature] = useState(String(config?.agent.temperature ?? 0.7));

  if (loading || !config) {
    return <div style={{ color: "#9ca3af", fontSize: 13 }}>Loading config...</div>;
  }

  const handleSave = () => {
    onUpdate({
      "rag.top_k": Number(topK),
      "rag.similarity_threshold": Number(threshold),
      "agent.temperature": Number(temperature),
    });
  };

  return (
    <div style={{ fontSize: 13 }}>
      <div style={{ fontWeight: 600, marginBottom: 8 }}>Configuration</div>
      <div style={{ marginBottom: 8 }}>
        <label style={{ display: "block", color: "#6b7280", marginBottom: 2 }}>Top K</label>
        <input
          type="number"
          value={topK}
          onChange={(e) => setTopK(e.target.value)}
          style={{ width: "100%", padding: "4px 8px", border: "1px solid #d1d5db", borderRadius: 4 }}
        />
      </div>
      <div style={{ marginBottom: 8 }}>
        <label style={{ display: "block", color: "#6b7280", marginBottom: 2 }}>Similarity Threshold</label>
        <input
          type="number"
          step="0.1"
          min="0"
          max="1"
          value={threshold}
          onChange={(e) => setThreshold(e.target.value)}
          style={{ width: "100%", padding: "4px 8px", border: "1px solid #d1d5db", borderRadius: 4 }}
        />
      </div>
      <div style={{ marginBottom: 12 }}>
        <label style={{ display: "block", color: "#6b7280", marginBottom: 2 }}>Temperature</label>
        <input
          type="number"
          step="0.1"
          min="0"
          max="2"
          value={temperature}
          onChange={(e) => setTemperature(e.target.value)}
          style={{ width: "100%", padding: "4px 8px", border: "1px solid #d1d5db", borderRadius: 4 }}
        />
      </div>
      <div style={{ display: "flex", gap: 8 }}>
        <button
          onClick={handleSave}
          style={{
            flex: 1,
            padding: "6px 12px",
            background: "#3b82f6",
            color: "white",
            border: "none",
            borderRadius: 4,
            cursor: "pointer",
            fontSize: 13,
          }}
        >
          Save
        </button>
        <button
          onClick={onReload}
          style={{
            flex: 1,
            padding: "6px 12px",
            background: "#6b7280",
            color: "white",
            border: "none",
            borderRadius: 4,
            cursor: "pointer",
            fontSize: 13,
          }}
        >
          Reload
        </button>
      </div>
    </div>
  );
}
