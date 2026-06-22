import { useState, useCallback, type DragEvent } from "react";
import { documentsApi } from "../../services/api";

interface Props {
  onUploadComplete: () => void;
}

export function UploadArea({ onUploadComplete }: Props) {
  const [uploading, setUploading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [dragOver, setDragOver] = useState(false);

  const handleFiles = useCallback(
    async (files: FileList | File[]) => {
      setError(null);
      setUploading(true);
      try {
        for (const file of Array.from(files)) {
          await documentsApi.upload(file);
        }
        onUploadComplete();
      } catch (err) {
        setError(err instanceof Error ? err.message : "Upload failed");
      } finally {
        setUploading(false);
      }
    },
    [onUploadComplete]
  );

  const handleDrop = useCallback(
    (e: DragEvent) => {
      e.preventDefault();
      setDragOver(false);
      if (e.dataTransfer.files.length > 0) {
        handleFiles(e.dataTransfer.files);
      }
    },
    [handleFiles]
  );

  const handleDragOver = (e: DragEvent) => {
    e.preventDefault();
    setDragOver(true);
  };

  const handleInputChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    if (e.target.files && e.target.files.length > 0) {
      handleFiles(e.target.files);
    }
  };

  return (
    <div>
      <div
        onDrop={handleDrop}
        onDragOver={handleDragOver}
        onDragLeave={() => setDragOver(false)}
        style={{
          border: `2px dashed ${dragOver ? "#3b82f6" : "#d1d5db"}`,
          borderRadius: 8,
          padding: 20,
          textAlign: "center",
          background: dragOver ? "#eff6ff" : "#f9fafb",
          cursor: "pointer",
          transition: "all 0.2s",
        }}
      >
        <input
          type="file"
          accept=".md,.txt"
          multiple
          onChange={handleInputChange}
          disabled={uploading}
          style={{ display: "none" }}
          id="file-upload"
        />
        <label htmlFor="file-upload" style={{ cursor: uploading ? "not-allowed" : "pointer" }}>
          {uploading ? (
            <span style={{ color: "#6b7280" }}>Uploading...</span>
          ) : (
            <>
              <div style={{ fontSize: 24, marginBottom: 4 }}>📄</div>
              <div style={{ color: "#374151", fontWeight: 500 }}>
                Drop files here or click to upload
              </div>
              <div style={{ color: "#9ca3af", fontSize: 13, marginTop: 4 }}>
                Supports .md and .txt files
              </div>
            </>
          )}
        </label>
      </div>
      {error && (
        <div style={{ marginTop: 8, color: "#dc2626", fontSize: 13 }}>{error}</div>
      )}
    </div>
  );
}
