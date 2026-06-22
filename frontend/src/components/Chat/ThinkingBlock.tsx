import { useState, useEffect } from "react";

interface ThinkingBlockProps {
  content: string;
  isStreaming?: boolean;
}

export function ThinkingBlock({ content, isStreaming = false }: ThinkingBlockProps) {
  const [expanded, setExpanded] = useState(false);

  useEffect(() => {
    if (isStreaming) {
      setExpanded(true);
    } else {
      setExpanded(false);
    }
  }, [isStreaming]);

  if (!content) return null;

  return (
    <div
      style={{
        marginBottom: 8,
        borderRadius: 8,
        border: "1px solid #e5e7eb",
        background: "#fafafa",
        overflow: "hidden",
      }}
    >
      <button
        onClick={() => setExpanded(!expanded)}
        style={{
          display: "flex",
          alignItems: "center",
          gap: 6,
          width: "100%",
          padding: "6px 10px",
          background: "none",
          border: "none",
          cursor: "pointer",
          fontSize: 12,
          color: "#9ca3af",
          textAlign: "left",
        }}
      >
        <span
          style={{
            display: "inline-block",
            transition: "transform 0.2s",
            transform: expanded ? "rotate(90deg)" : "rotate(0deg)",
            fontSize: 10,
          }}
        >
          ▶
        </span>
        <span>思考过程</span>
        {isStreaming && (
          <span
            style={{
              display: "inline-block",
              width: 4,
              height: 4,
              borderRadius: "50%",
              backgroundColor: "#9ca3af",
              marginLeft: 4,
              animation: "blink 1s infinite",
            }}
          />
        )}
      </button>
      {expanded && (
        <div
          style={{
            padding: "4px 10px 8px",
            fontSize: 12,
            color: "#9ca3af",
            lineHeight: 1.5,
            whiteSpace: "pre-wrap",
            maxHeight: 200,
            overflowY: "auto",
          }}
        >
          {content}
        </div>
      )}
    </div>
  );
}
