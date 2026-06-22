import { useState, useCallback } from "react";
// import { useConfig } from "../../hooks/useConfig";
import { UploadArea } from "../FileUpload";
import { FileList } from "./FileList";
// import { ConfigPanel } from "./ConfigPanel";
import { documentsApi } from "../../services/api";

interface Props {
  isOpen: boolean;
  onToggle: () => void;
}

export function Sidebar({ isOpen, onToggle }: Props) {
  // const { config, loading: configLoading, updateConfig, reloadConfig } = useConfig();
  const [refreshTrigger, setRefreshTrigger] = useState(0);
  const [deleting, setDeleting] = useState(false);

  const handleUploadComplete = useCallback(() => {
    setRefreshTrigger((n) => n + 1);
  }, []);

  const handleDeleteAll = useCallback(async () => {
    if (!confirm("Delete all documents?")) return;
    setDeleting(true);
    try {
      await documentsApi.deleteAll();
      setRefreshTrigger((n) => n + 1);
    } catch {
      // silently fail
    } finally {
      setDeleting(false);
    }
  }, []);

  if (!isOpen) {
    return (
      <button
        onClick={onToggle}
        style={{
          position: "fixed",
          left: 0,
          top: 12,
          padding: "8px 12px",
          background: "#1f2937",
          color: "white",
          border: "none",
          borderRadius: "0 6px 6px 0",
          cursor: "pointer",
          zIndex: 10,
        }}
      >
        ☰
      </button>
    );
  }

  return (
    <aside
      style={{
        width: 320,
        background: "#f9fafb",
        borderRight: "1px solid #e5e7eb",
        display: "flex",
        flexDirection: "column",
        overflowY: "auto",
        flexShrink: 0,
      }}
    >
      <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", padding: "12px 16px", borderBottom: "1px solid #e5e7eb" }}>
        <h3 style={{ margin: 0, fontSize: 16 }}>Settings</h3>
        <button
          onClick={onToggle}
          style={{ background: "none", border: "none", cursor: "pointer", fontSize: 18, color: "#6b7280" }}
        >
          ✕
        </button>
      </div>
      <div style={{ padding: 16, display: "flex", flexDirection: "column", gap: 20 }}>
        <UploadArea onUploadComplete={handleUploadComplete} />
        <FileList refreshTrigger={refreshTrigger} />
        {refreshTrigger > 0 && (
          <button
            onClick={handleDeleteAll}
            disabled={deleting}
            style={{
              padding: "6px 12px",
              background: "#ef4444",
              color: "white",
              border: "none",
              borderRadius: 4,
              cursor: deleting ? "not-allowed" : "pointer",
              fontSize: 13,
            }}
          >
            {deleting ? "Deleting..." : "Delete All Documents"}
          </button>
        )}
        <hr style={{ border: "none", borderTop: "1px solid #e5e7eb" }} />
        {/* <ConfigPanel
          config={config}
          loading={configLoading}
          onUpdate={updateConfig}
          onReload={reloadConfig}
        /> */}
      </div>
    </aside>
  );
}
