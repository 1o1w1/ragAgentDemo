import { useState, type FormEvent, type KeyboardEvent } from "react";

interface Props {
  onSend: (message: string) => void;
  disabled: boolean;
}

export function MessageInput({ onSend, disabled }: Props) {
  const [input, setInput] = useState("");

  const handleSubmit = (e: FormEvent) => {
    e.preventDefault();
    if (input.trim() && !disabled) {
      onSend(input.trim());
      setInput("");
    }
  };

  const handleKeyDown = (e: KeyboardEvent) => {
    if (e.key === "Enter" && !e.shiftKey) {
      e.preventDefault();
      handleSubmit(e);
    }
  };

  return (
    <form onSubmit={handleSubmit} style={{ display: "flex", gap: 8, padding: 16, borderTop: "1px solid #e5e7eb" }}>
      <textarea
        value={input}
        onChange={(e) => setInput(e.target.value)}
        onKeyDown={handleKeyDown}
        placeholder="Ask a question about your documents..."
        disabled={disabled}
        rows={2}
        style={{
          flex: 1,
          padding: 8,
          border: "1px solid #d1d5db",
          borderRadius: 6,
          resize: "none",
          fontFamily: "inherit",
        }}
      />
      <button
        type="submit"
        disabled={disabled || !input.trim()}
        style={{
          padding: "8px 20px",
          background: disabled || !input.trim() ? "#9ca3af" : "#3b82f6",
          color: "white",
          border: "none",
          borderRadius: 6,
          cursor: disabled || !input.trim() ? "not-allowed" : "pointer",
          fontWeight: 500,
        }}
      >
        Send
      </button>
    </form>
  );
}
