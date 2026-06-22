import { useState, useEffect, useCallback } from "react";
import type { UploadedFile } from "../../types";
import { documentsApi } from "../../services/api";

interface Props {
  refreshTrigger: number;
}

export function FileList({ refreshTrigger }: Props) {
  const [files, setFiles] = useState<UploadedFile[]>([]);
  const [loading, setLoading] = useState(true);

  const loadFiles = useCallback(async () => {
    setLoading(true);
    try {
      const data = await documentsApi.listUploads();
      setFiles(data.files);
    } catch {
      // silently fail
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    loadFiles();
  }, [loadFiles, refreshTrigger]);

  if (loading) {
    return <div style={{ color: "#9ca3af", fontSize: 13 }}>Loading files...</div>;
  }

  if (files.length === 0) {
    return <div style={{ color: "#9ca3af", fontSize: 13 }}>No documents uploaded</div>;
  }

  return (
    <div>
      <div style={{ fontWeight: 600, fontSize: 13, marginBottom: 6 }}>
        Uploaded Files ({files.length})
      </div>
      <div style={{ maxHeight: 200, overflowY: "auto" }}>
        {files.map((file) => (
          <div
            key={file.name}
            style={{
              display: "flex",
              justifyContent: "space-between",
              padding: "4px 0",
              fontSize: 13,
              borderBottom: "1px solid #f3f4f6",
            }}
          >
            <span style={{ overflow: "hidden", textOverflow: "ellipsis", whiteSpace: "nowrap" }}>
              {file.name}
            </span>
            <span style={{ color: "#9ca3af", flexShrink: 0, marginLeft: 8 }}>
              {(file.size / 1024).toFixed(1)}KB
            </span>
          </div>
        ))}
      </div>
    </div>
  );
}
